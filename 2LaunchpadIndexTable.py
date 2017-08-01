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
# python 2LaunchpadIndexTable.py <datasource_id> <password>
#
# purpose:
# inserts datasource id, name, and html to indexes table
################################################################

import sys
import time
import pymysql
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

datasource_id = sys.argv[1]
dbpw = sys.argv[2]
dbhost = ''
dbuser = ''
dbschema = ''


def connectToDb():
    try:
        db = pymysql.connect(host=dbhost,
                             user=dbuser,
                             passwd=dbpw,
                             db=dbschema,
                             use_unicode=True,
                             charset="utf8mb4")
    except pymysql.Error as err:
        print(err)
    return db

# network issue
# imagemagick

#mysql error:
# nunitv2

selectQuery = 'SELECT p.name, p.web_link \
               FROM lpd_projects p \
               LEFT OUTER JOIN lpd_indexes i \
               ON p.name = i.name \
               WHERE i.name IS NULL \
               AND p.datasource_id = %s \
               AND p.name != "nunitv2"'
               
insertQuery = 'INSERT IGNORE INTO lpd_indexes (datasource_id, \
                                         name, \
                                         html, \
                                         milestoneUrl, \
                                         milestoneIsActiveUrl, \
                                         seriesUrl, \
                                         date_collected) \
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s, now())'

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}


db = connectToDb()
cursor = db.cursor()
cursor.execute(selectQuery, (datasource_id))
listOfProjects = cursor.fetchall()

for project in listOfProjects:
        time.sleep(2)
        name = project[0]
        url = project[1]
        print('working on', name)

        try:
            req = urllib2.Request(url, headers=hdr)
            projectHtml = urllib2.urlopen(req).read()
        except urllib2.HTTPError as herr1:
            print("~~~~~SKIPPING html~~~~~")
            print(herr1)
            pass

        try:
            cursor.execute(insertQuery,
                           (datasource_id,
                            name,
                            projectHtml,
                            milestoneUrl,
                            milestoneIsActiveUrl,
                            seriesUrl))
            db.commit()
            print(name, " inserted into indexes table!\n")
        except pymysql.Error as err:
            print(err)
            db.rollback()
        except:
            pass
