#!/usr/bin/python
import os
import json
import simplekml
from shapely.geometry import mapping
from shapely.geometry import Point


def make_geojson(lon, lat, location_name):
    """ create a Point and convert it into a dict suitable for GeoJSON output"""
    p = mapping(Point(float(lon), float(lat)))
    return {"type": "Feature", "properties": {"name": location_name}, "geometry": p}


kml = simplekml.Kml()
features = []

for region in os.listdir("json"):
    for pretfile in os.listdir("json/%s" % region):
        with open("json/%s/%s" % (region, pretfile)) as f:
            data = json.load(f)

        if "latitude" in data["location"]:
            kml.newpoint(
                name=data["details"]["name"],
                coords=[(data["location"]["longitude"], data["location"]["latitude"])],
            )
            # create GeoJSON output dict
            features.append(
                make_geojson(
                    data["location"]["longitude"],
                    data["location"]["latitude"],
                    data["details"]["name"],
                )
            )

# GeoJSON FeatureCollection output schema
schema = {
    "type": "FeatureCollection",
    "features": features,
}

with open("prets.geojson", "w") as outfile:
    outfile.write(json.dumps(schema))

kml.save("prets.kml")
