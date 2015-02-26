#!/usr/bin/python
import os
import requests
import lxml.html

req = requests.get('http://www.pret.com/find_a_pret/list.htm')
root_page = req.content

prets = []

root = lxml.html.document_fromstring(root_page)
links = root.xpath('//*[@id="content"]/table/tr/td[1]/a')
for link in links:
    pret = link.attrib['href']
    print pret
    req = requests.get('http://www.pret.com' + pret)
    with open('raw_prets/' + os.path.split(pret)[1], 'w') as f:
        f.write(req.content)
