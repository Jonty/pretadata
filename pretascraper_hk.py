#!/usr/bin/python

# This is absolutely horrendous because the page is horrendous

import os
import re
import json
import datetime

import requests
import lxml.html
from slugify import slugify

api_key = os.getenv("GMAPS_API_KEY")
region = "hk"

response = requests.get("https://www.pret.hk/en-HK/find-a-pret")

root = lxml.html.document_fromstring(response.content)
[pret_json_elems] = root.xpath('//script[@id="__NEXT_DATA__"]')
data = json.loads(pret_json_elems.text)

for slot in data["props"]["pageProps"]["page"]["slots"]:
    if slot["identifier"] == "HK Shops Accordion":
        for pret in slot["entries"]:
            name = pret["title"].strip()
            address = ""
            phone = None

            for content in pret["body"]["content"]:
                value = content["content"][0]["value"].strip()
                if value != "":
                    if value.startswith("Tel"):
                        phone = value
                    else:
                        if "\n" in value:
                            for line in value.splitlines():
                                line = line.strip()
                                if line != "":
                                    if line.startswith("Tel"):
                                        phone = line
                                    else:
                                        address = line
                        else:
                            address = value

            if phone:
                phone = "+852 " + phone.replace("Tel.", "").replace("Tel:", "").strip()

            pret_id = slugify(region + "_" + name)

            geocode_address = address
            if "Hong Kong" not in geocode_address:
                geocode_address += ", Hong Kong"

            address_bits = geocode_address.split(",")
            geocode_address = ",".join(address_bits[-4:])

            response = requests.get(
                "https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s"
                % (geocode_address, api_key)
            )
            geocoding = response.json()["results"][0]

            valid = False
            postal_code = None
            for item in geocoding["address_components"]:
                if item["long_name"] == "Hong Kong":
                    valid = True
                if "administrative_area_level_1" in item["types"]:
                    city = item["long_name"]

            # Sometimes it really really wrongly geocodes
            if not valid:
                raise ("Invalid geocoding for %s", geocoding)

            latitude = geocoding["geometry"]["location"]["lat"]
            longitude = geocoding["geometry"]["location"]["lng"]

            data = {
                "details": {
                    "id": pret_id,
                    "url": "https://www.pret.hk/en-HK/find-a-pret",
                    "open": None,
                    "name": name,
                    "phone_number": phone,
                    "data_last_updated": datetime.datetime.now().isoformat(),
                },
                "facilities": {},
                "location": {
                    "street": address,
                    "city": city,
                    "postal_code": None,
                    "country": "Hong Kong",
                    "latitude": latitude,
                    "longitude": longitude,
                },
                "opening_hours": {},
            }

            with open("json/%s/%s.json" % (region, pret_id), "w") as f:
                f.write(json.dumps(data, indent=4, separators=(",", ": ")))
