#!/usr/bin/python
import os
import re
import json
import lxml.html

for pretfile in os.listdir('raw_prets'):
    name, _ = pretfile.split('.')
    print name

    f = open('raw_prets/' + pretfile)
    root = lxml.html.parse(f)

    data = {}

    [title_img] = root.xpath('//*[@id="content"]/div[1]/img')
    data['title'] = title_img.attrib['alt']

    phone_span = root.xpath('//*[@id="content"]/div[2]/span/text()')
    data['phone_number'] = ''.join(phone_span).strip().replace('Telephone Number: ', '')
    
    opening_soon = root.xpath('//*[@id="content"]/div[1]/span/img')
    data['has_opened'] = not opening_soon

    opening_hours = {}
    hours_table = root.xpath('//*[@id="content"]/div[3]/div[1]/table/tr')
    for day in hours_table:
        weekday_td, hours_td = day.getchildren()
        opening_hours[weekday_td.text.lower()] = hours_td.text
    
    data['opening_hours'] = opening_hours

    [seating_img] = root.xpath('//*[@id="content"]/div[3]/div[2]/img[2]')
    data['seating'] = seating_img.attrib['alt']

    [toilets_img] = root.xpath('//*[@id="content"]/div[3]/div[2]/img[4]')
    data['toilets'] = toilets_img.attrib['alt']

    [wheelchair_img] = root.xpath('//*[@id="content"]/div[3]/div[2]/img[6]')
    data['wheelchair_access'] = wheelchair_img.attrib['alt'] == 'Yes'

    [wifi_img] = root.xpath('//*[@id="content"]/div[3]/div[2]/img[8]')
    data['wifi'] = wifi_img.attrib['alt'] == 'Yes'

    getting_there_span = root.xpath('//*[@id="content"]/div[3]/div[2]/text()')
    data['getting_there'] = ''.join(getting_there_span).strip()

    address_div = root.xpath('//*[@id="content"]/div[2]/text()')
    data['location'] = {
        'address': address_div[0].strip(),
    }

    map_img = root.xpath('//*[@id="content"]/div[4]/img')
    if map_img:
        matches = re.search('\|(\d+.\d+),(-?\d+.\d+)&', map_img[0].attrib['src'])
        data['location']['latitude'] = matches.group(1)
        data['location']['longitude'] = matches.group(2)

    with open('json/' + name + '.json', 'w') as f:
        f.write(json.dumps(data, sort_keys=True, indent=4, separators=(',', ': ')))
