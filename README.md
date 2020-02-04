Pretadata
=========
This repository contains a lovely GeoJSON representation of data about every Pret A Manger fast food restaurant, and the code used to extract it using the [Food Hygiene Rating Scheme API](https://api.ratings.food.gov.uk/help).

And [a map](prets.geojson). Which was the reason for doing this.

Data
----
You probably want [the GeoJSON](prets.geojson), but there's also [a KML file](prets.kml) of all Pret locations.

Code
----
[`pretascraper.py`](pretascraper.py) grabs all the raw data from the FRHS API endpoint, tidies it up, removes non-geocoded data, then outputs a GeoJSON `FeatureCollection`. Each `Feature` contains metadata about that particular Pret branch under the `properties` key, but alas, opening hours are not currently recorded.  

You can see the old data by checking out the `v1.0.0` tag in the Git repository, or using by [this link](https://github.com/urschrei/pretadata/tree/V1.0.0).
