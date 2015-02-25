Pretadata
=========
This repository contains a lovely JSON representation of data about every Pret A Manger fast food restaurant, and the code used to extract it from their website.

And [a map](https://maps.google.com/maps?q=https://raw.githubusercontent.com/jonty/pretadata/master/prets.kml). Which was the reason for doing this.

Data
----
You probably want [the json](json/) files, but there's also [a kml file of all pret locations](prets.kml) that you can look at in [google maps](https://maps.google.com/maps?q=https://raw.githubusercontent.com/jonty/pretadata/master/prets.kml).

Code
----
```scrapeprets.py``` grabs all the html pages about each pret into ```raw_prets```, ```extractprets.py``` extracts the information from the html pages and drops json files into ```json```, ```pretkml.py``` uses the json files to generate ```prets.kml```.
