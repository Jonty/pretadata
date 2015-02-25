#!/usr/bin/python
import os
import json
import simplekml

kml = simplekml.Kml()

for pretfile in os.listdir('json'):
    with open('json/' + pretfile) as f:
        data = json.load(f)

    if 'latitude' in data['location']:
        kml.newpoint(name=data['details']['name'], coords=[
            (data['location']['longitude'], data['location']['latitude'])
        ])

kml.save("prets.kml")
