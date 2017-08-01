# -*- coding: utf-8 -*-
# Copyright (C) 2004-2017 Megan Squire <msquire@elon.edu>
# and Caroline Frankel
# License: GPLv3
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
# python 5LaunchpadBugTags.py <datasource_id> <password>
#
# purpose:
# inserts bug tag information into the bug tag table
################################################################

import re
import sys
import pymysql
from bs4 import BeautifulSoup

datasource_id = sys.argv[1]
dbpw = sys.argv[2]
dbschema = ''
dbhost = ''
dbuser = ''


def run():
    try:
        cursor.execute(insertBugTagQuery,
                       (datasource_id,
                        name,
                        official_bug_tag))
        db.commit()
        print(name, " inserted into bug tag table!\n")
    except pymysql.Error as err:
        print(err)
        db.rollback()


# establish database connection: SYR
try:
    db = pymysql.connect(host=dbhost,
                         user=dbuser,
                         passwd=dbpw,
                         db=dbschema,
                         use_unicode=True,
                         charset="utf8mb4")
    cursor = db.cursor()
except pymysql.Error as err:
    print(err)

selectQuery = 'SELECT name FROM lpd_indexes \
                WHERE datasource_id = %s'

selectHtmlQuery = 'SELECT html FROM lpd_indexes \
                    WHERE datasource_id = %s AND name = %s'

insertBugTagQuery = 'INSERT INTO lpd_official_bug_tags (datasource_id, \
                                                        name, \
                                                        official_bug_tag, \
                                                        last_updated) \
                       VALUES(%s, %s, %s, now())'

try:
    cursor.execute(selectQuery)
    listOfProjects = cursor.fetchall()

    for project in listOfProjects:
        name = project[0]

        cursor.execute(selectHtmlQuery, (datasource_id, name))
        html = cursor.fetchone()[0]
        print('\nworking on ', name)

        soup = BeautifulSoup(html, 'html.parser')

        regex = '\"official_bug_tags\": \[(.*?)\]'
        listOfTags = re.findall(regex, str(soup))
        if listOfTags:
            splitList = listOfTags[0].split(',')
            for s in splitList:
                regex2 = '"(.*?)"'
                word = re.findall(regex2, str(s))
                if word:
                    official_bug_tag = word[0]
                    print('official_bug_tag: ', official_bug_tag)
                    run()

except pymysql.Error as err:
    print(err)
