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
