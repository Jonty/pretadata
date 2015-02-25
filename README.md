Pretadata
=========
This repository contains a lovely JSON representation of data about every Pret A Manger fast food restaurant, and the code used to extract it from their website.

And [a map](https://maps.google.com/maps?q=https://raw.githubusercontent.com/jonty/pretadata/master/prets.kml). Which was the reason for doing this.

Data
----
You probably want [the JSON](json/) files, but there's also [a KML file of all Pret locations](prets.kml) that you can look at in [Google Maps](https://maps.google.com/maps?q=https://raw.githubusercontent.com/jonty/pretadata/master/prets.kml).

Code
----
```pretascraper.py``` grabs all the HTML pages about each Pret into ```raw_prets```, ```extractprets.py``` extracts the information from the HTML pages and drops JSON files into ```json```, ```pretkml.py``` uses the JSON files to generate ```prets.kml```.

Example JSON data
-----------------
From the oldest Pret still around, [#2](json/UK0002.json).
```
{
    "number": "2",
    "details": {
        "has_opened": true,
        "name": "319 High Holborn",
        "phone_number": "020 7932 5202"
    },
    "facilities": {
        "seating": "No seats",
        "toilets": "None",
        "wheelchair_access": true,
        "wifi": false
    },
    "location": {
        "address": "319 High Holborn, London WC1V 7PU",
        "getting_there": "Exit Chancery Lane station and take a left down High Holborn. You will see the shop on your left.",
        "latitude": "51.5181546133",
        "longitude": "-0.112728300111"
    },
    "opening_hours": {
        "friday": "06:30 - 19:30",
        "monday": "06:30 - 19:30",
        "saturday": "08:00 - 17:00",
        "sunday": "09:00 - 16:00",
        "thursday": "06:30 - 19:30",
        "tuesday": "06:30 - 19:30",
        "wednesday": "06:30 - 19:30"
    }
}
```
