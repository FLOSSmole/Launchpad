# -*- coding: utf-8 -*-
# Copyright (C) 2004-2017 Megan Squire <msquire@elon.edu>
# License: GPLv3
# 
# Contribution from:
# Caroline Frankel
#
# We're working on this at http://flossmole.org - Come help us build
# an open and accessible repository for data and analyses for free and open
# source projects.
#
# If you use this code or data for preparing an academic paper please
# provide a citation to:
#
# Howison, J., Conklin, M., & Crowston, K. (2006). FLOSSmole:
# A collaborative repository for FLOSS research data and analyses.
# International Journal of Information Technology and Web Engineering, 1(3),
# 17–26.
#
# and
#
# FLOSSmole: a project to provide research access to
# data and analyses of open source projects.
# Available at http://flossmole.org
#
################################################################
# usage:
# python 1LaunchpadWebScraper.py <datasource_id> <password>
#
# purpose:
# grab a list of the projects on Launchpad
# get the name, display name, and website of each project 
################################################################

import re
import sys
import pymysql
from bs4 import BeautifulSoup
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

datasource_id = '272'


def insert():
    try:
        cursor.execute(insertQuery,
                       (datasource_id,
                        name,
                        displayName,
                        web_link))
        db.commit()
        print(name, " inserted into projects table!\n")
    except pymysql.Error as err:
        print(err)
        db.rollback()

# establish database connection: SYR
try:
    db = pymysql.connect(host='flossdata.syr.edu',
                         user='',
                         passwd='',
                         db='',
                         use_unicode=True,
                         charset="utf8mb4")
    cursor = db.cursor()
except pymysql.Error as err:
    print(err)

insertQuery = 'INSERT INTO lpd_projects (datasource_id, \
                                         name, \
                                         display_name, \
                                         web_link, \
                                         last_updated) \
            VALUES(%s, %s, %s, %s, now())'

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

numResults = 'of\s*(.*?)\s*results'
results = re.findall(numResults, str(soup))[0]

num = 0
i = 1

while num < int(results):
    listOfProjectUrl = 'https://launchpad.net/projects/+all?batch=300&memo=' + str(num) + '&start=' + str(num)

    req = urllib2.Request(listOfProjectUrl, headers=hdr)
    listOfProjectHtml = urllib2.urlopen(req).read()

    soup = BeautifulSoup(listOfProjectHtml, 'html.parser')

    table =soup.find('table', id = 'product-listing')

    classProduct = 'class=\"sprite product\" href=\"/(.*?)\">(.*?)</a>'
    classImage = '<div>\s*<a class=\"bg-image\" href=\"/(.*?)\" style=\"background-image: url(.*?)\">(.*?)</a>'
    for line in table:
        product = re.findall(classProduct, str(line))
        if product:
            productInfo = product[0]
            name = productInfo[0]
            displayName = productInfo[1]
            web_link = 'https://launchpad.net/' + name
            print(i, 'name: ', name, '\n    display name: ', displayName)
            print('    web link: ', web_link)
            i = i + 1
            insert()

        productWithImage = re.findall(classImage, str(line))
        if productWithImage:
            productWithImage = productWithImage[0]
            name = productWithImage[0]
            displayName = productWithImage[2]
            web_link = 'https://launchpad.net/' + name
            print('*', i, 'name: ', name, '\n    display name: ', displayName)
            print('    web link: ', web_link)
            i = i + 1
            insert()

    num = num + 300
