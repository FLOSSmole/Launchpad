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
# python 9LaunchpadParserSeriesTable.py <datasource_id> <password>
#
# purpose:
# inserts series information for the series table
################################################################

import re
import sys
import pymysql
from bs4 import BeautifulSoup
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

datasource_id = '122'  # sys.argv[1]


def regexMaker(word):
    line = '\"' + word + '\": \"(.*?)\",'
    lineFinder = re.findall(line, str(soup))
    if lineFinder:
        word = lineFinder[0]
        return word
        

def run():
    try:
        cursor.execute(insertSeriesQuery,
                       (datasource_id,  #
                        display_name,   #
                        title,
                        status,         #
                        name,           #
                        project_name,   #
                        summary))       #
        db.commit()
        print(project_name, "inserted into series table!\n")
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

selectQuery = 'SELECT name, seriesHtml FROM lpd_indexes limit 1'


insertSeriesQuery = 'INSERT INTO lpd_series (datasource_id, \
                                             display_name, \
                                             title, \
                                             status, \
                                             name, \
                                             project_name, \
                                             summary, \
                                             last_updated) \
                    VALUES(%s, %s, %s, %s, %s, %s, %s, now())'

try:
    cursor.execute(selectQuery)
    listOfProjects = cursor.fetchall()

    for project in listOfProjects:
        project_name = project[0]
        html = project[1]
        print('\nworking on ', project_name)

        soup = BeautifulSoup(html, 'html.parser')
        strong = soup.find_all('strong')
        for s in strong:
            a = s.find_all('a')
            for line in a:
                regexName = '<a href=\"/(.*?)/(.*?)">(.*?)</a>'
                nameFinder = re.findall(regexName, str(line))
                if nameFinder:
                    name = nameFinder[0][1]
                    print('name: ', name)
                    
                    display_name = nameFinder[0][2]
                    print('display name: ', display_name)

                regexStatus = '>' + display_name + '</a>\s*(.*?)\s*</strong>\s*<em>(.*?)</em>'
                statusFinder = re.findall(regexStatus, str(soup))
                if statusFinder:
                    status = statusFinder[0][1]
                    print('status: ', status)
            
                p = soup.find('p')
                summary = p.contents[0]
                print('summary: ', summary)

                title = project_name + ' ' + name + ' series'
                print('title: ', title)

                run()
            
except pymysql.Error as err:
    print(err)
