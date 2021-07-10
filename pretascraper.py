#!/usr/bin/python
import os
import re
import json
import datetime

import requests
import lxml.html
from slugify import slugify


response = requests.get("https://locations.pret.co.uk/")

root = lxml.html.document_fromstring(response.content)
regions = root.xpath('//*[@id="footer-countrypicker"]/option')

prets = []

for region in regions:
    region_url = region.attrib["data-href"]
    region_name = region.attrib["data-ya-track"]

    if "locations" not in region_url:
        continue

    response = requests.get(region_url)
    root = lxml.html.document_fromstring(response.content)
    cities = root.xpath('//a[@class="Directory-listLink"]')
    for city in cities:
        city_name = city.text_content().strip()

        city_url = region_url + "/" + city.attrib["href"]
        pret_id = slugify(city.attrib["href"])
        city_count = city.attrib["data-count"]

        if city_count == "(1)":
            prets.append((region_name, pret_id, city_url))
        else:
            response = requests.get(city_url)
            root = lxml.html.document_fromstring(response.content)

            pret_links = root.xpath('//a[@class="Teaser-titleLink"]')
            for pret_link in pret_links:
                pret_url = pret_link.attrib["href"]
                pret_id = slugify(pret_url)
                prets.append((region_name, pret_id, region_url + "/" + pret_url))

            city_links = root.xpath('//a[@class="Directory-listLink"]')
            cities.extend(city_links)


for region_name, pret_id, pret_url in prets:
    print(pret_url)

    response = requests.get(pret_url)
    root = lxml.html.document_fromstring(response.content)

    name = "Pret a Manger"
    name_elem = root.xpath('//h1[@id="location-name"]')
    if name_elem:
        name = name_elem[0].text_content()

    latitude = root.xpath('//meta[@itemprop="latitude"]')[0].attrib["content"]
    longitude = root.xpath('//meta[@itemprop="longitude"]')[0].attrib["content"]

    address_street = root.xpath('//meta[@itemprop="streetAddress"]')[0].attrib[
        "content"
    ]
    address_city = root.xpath('//meta[@itemprop="addressLocality"]')[0].attrib[
        "content"
    ]
    address_postal_code = root.xpath('//span[@itemprop="postalCode"]')[0].text_content()
    address_country = root.xpath('//abbr[@itemprop="addressCountry"]')[0].text_content()

    phone_number = ""
    phone_elem = root.xpath('//a[@class="Phone-link"]')
    if phone_elem:
        phone_number = phone_elem[0].attrib["href"].split(":")[1]

    store_closed = True
    opening_hours = {}

    hours_row = root.xpath('//tr[@itemprop="openingHours"]')
    for row in hours_row:
        day = row.xpath('.//td[@class="c-hours-details-row-day"]')[0].text_content()

        open_time = None
        close_time = None
        closed = False

        times = row.xpath(
            './/span[contains(@class, "c-hours-details-row-intervals-instance")]'
        )
        if times:
            store_closed = False
            open_time = times[0].attrib["data-open-interval-start"]
            open_time = open_time[:-2] + ":" + open_time[-2:]
            close_time = times[0].attrib["data-open-interval-end"]
            close_time = close_time[:-2] + ":" + close_time[-2:]
        else:
            closed = True

        opening_hours[day.lower()] = {
            "open": open_time,
            "close": close_time,
            "closed": closed,
        }

    facilities = {
        "seating": False,
        "wheelchair": False,
        "wifi": False,
    }

    facilities_nodes = root.xpath('//li[@class="Core-facility"]/svg')
    for node in facilities_nodes:
        matches = re.search("icon--(\w+)", node.attrib["class"])
        facility_name = matches.group(1)
        facilities[facility_name] = True

    data = {
        "details": {
            "id": pret_id,
            "url": pret_url,
            "open": not store_closed,
            "name": name,
            "phone_number": phone_number,
            "data_last_updated": datetime.datetime.now().isoformat(),
        },
        "facilities": facilities,
        "location": {
            "street": address_street,
            "city": address_city,
            "postal_code": address_postal_code,
            "country": address_country,
            "latitude": latitude,
            "longitude": longitude,
        },
        "opening_hours": opening_hours,
    }

    try:
        os.mkdir("json/%s" % region_name)
    except FileExistsError:
        pass

    with open("json/%s/%s.json" % (region_name, pret_id), "w") as f:
        f.write(json.dumps(data, indent=4, separators=(",", ": ")))
