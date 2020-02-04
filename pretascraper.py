#!/usr/bin/env python

import fiona
import requests
from shapely.geometry import Point, mapping
import geojson
import geopandas as gp
import pandas as pd
import numpy as np

# See https://api.ratings.food.gov.uk/help for all API endpoints
base_url = "https://api.ratings.food.gov.uk"
establishments = "/Establishments"
headers = {"x-api-version": "2"}

r = requests.get(
    base_url + establishments, params={"name": "pret a manger"}, headers=headers
)

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
        "RatingValue",
        "RatingKey",
        "RatingDate",
        "LocalAuthorityCode",
        "LocalAuthorityBusinessID",
        "SchemeType",
        "BusinessType",
        "links",
    ],
    inplace=True,
)

df_pret["point_geo"] = df_pret["geocode"].apply(dict_to_point)
# Missing data resulted in NA values, so drop those rows
df_pret.dropna(inplace=True)
# drop now-redundant geocoding columns
df_pret.drop(columns=["geocode"], inplace=True)
# create GeoDataFrame, and dump to GeoJSON
gdf = gp.GeoDataFrame(df_pret, geometry="point_geo")
gdf.to_file("prets.geojson", driver="GeoJSON")

# set up fiona with a KML driver, and use it to write the DataFrame
gp.io.file.fiona.drvsupport.supported_drivers["KML"] = "rw"
with fiona.drivers():
    gdf.to_file("prets.kml", driver="KML")


def dict_to_point(value):
    """ 
    Create a Point from a dict value containing lon / lat
    str values.
    If either of the values are None, return NaN
    """
    if value["longitude"] == None or value["latitude"] == None:
        return np.nan
    else:
        return Point(float(value["longitude"]), float(value["latitude"]))
