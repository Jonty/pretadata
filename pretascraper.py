#!/usr/bin/env python

import fiona
import requests
from shapely.geometry import Point
import geopandas as gp
import pandas as pd
import numpy as np
import os
import re
import bs4

# TODO: populate this value using an encrypted env var within CircleCI
OPENCAGE_KEY = os.environ["OPENCAGE"]

# See https://api.ratings.food.gov.uk/help for all API endpoints
base_url = "https://api.ratings.food.gov.uk"
establishments = "/Establishments"
headers = {"x-api-version": "2"}

r = requests.get(
    base_url + establishments, params={"name": "pret a manger"}, headers=headers
)
r.raise_for_status()

df_pret = pd.DataFrame(r.json()["establishments"])
# We don't really need these columns, so drop them
df_pret.drop(
    columns=[
        "LocalAuthorityWebSite",
        "LocalAuthorityEmailAddress",
        "scores",
        "RightToReply",
        "Distance",
        "NewRatingPending",
        "meta",
        "Phone",
        "RatingDate",
        "LocalAuthorityCode",
        "LocalAuthorityBusinessID",
        "SchemeType",
        "BusinessType",
        "links",
    ],
    inplace=True,
)


def dict_to_point(value):
    """
    Create a Point from a dict value containing lon / lat
    str values.
    If either of the values are None, return NaN
    """
    if value["longitude"] is None or value["latitude"] is None:
        return np.nan
    else:
        return Point(float(value["longitude"]), float(value["latitude"]))


def geocode(df):
    """
    Attempt to geocode a concatenated string,
    assigning the result coordinates to a Point,
    or returning NaN
    """
    cols = ["AddressLine1", "AddressLine2", "AddressLine3", "AddressLine4", "PostCode"]
    to_join = []
    # only join non-empty address fields
    for col in cols:
        if df[col] != "":
            to_join.append(df[col])
    to_join.append("UK")
    return ", ".join(to_join)


def scrape(postcode):
    """
    Accepts a UK post code string, and attempts to scrape
    the Pret A Manger site for the opening hours of the nearest branch
    """
    base = "https://www.pret.co.uk/en-gb/find-a-pret/"
    rp = requests.get(base + postcode)
    # template to use if we have to bail out
    unknown = {
        "Monday": "unknown",
        "Tuesday": "unknown",
        "Wednesday": "unknown",
        "Thursday": "unknown",
        "Friday": "unknown",
        "Saturday": "unknown",
        "Sunday": "unknown",
    }
    try:
        rp.raise_for_status()
    # bail out early if something goes wrong with "the internet"
    except requests.exceptions.HTTPError:
        return unknown
    soup = BeautifulSoup(rp.content, "lxml")
    reg = re.compile("OPENING HOURS")
    # if we can't find opening hours, bail out
    try:
        opening_raw = soup.find("h4", text=reg).find_next("dl")
    except AttributeError:
        return unknown
    opening_times = {}
    for day, times in zip(
        opening_raw.findChildren("dt"), opening_raw.findChildren("dd")
    ):
        spl = times.text.split(" - ")
        if spl[0] == "Closed":
            continue
        opening_times[day.text] = {"open": spl[0], "close": spl[1]}
    return opening_times


df_pret["geometry"] = df_pret["geocode"].apply(dict_to_point)
# drop now-redundant geocoding columns
df_pret.drop(columns=["geocode"], inplace=True)
# create GeoDataFrame, and dump to GeoJSON
gdf = gp.GeoDataFrame(df_pret, geometry="geometry")

# attempt to geocode branches whose FHRS data is missing coordinates
geocoded = gp.tools.geocode(
    gdf[gdf.isnull().any(axis=1)].apply(geocode, axis=1),
    provider="opencage",
    api_key=OPENCAGE_KEY,
    timeout=10,
)
# update dataframe with newly-geocoded values
gdf.update(geocoded["geometry"])
# missing data are transformed into NA values, so drop those rows
gdf.dropna(inplace=True)
# Add opening hours to remaining records
df_pret["OpeningHours"] = df_pret["PostCode"].apply(scrape)
# dump to GeoJSON
gdf.to_file("prets.geojson", driver="GeoJSON")

# set up fiona with a KML driver, and use it to write the DataFrame
gp.io.file.fiona.drvsupport.supported_drivers["KML"] = "rw"
with fiona.drivers():
    gdf.to_file("prets.kml", driver="KML")
