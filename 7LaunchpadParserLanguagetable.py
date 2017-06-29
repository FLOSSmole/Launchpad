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
# python 7LaunchpadParserLanguagetable.py <datasource_id> <password>
#
# purpose:
# inserts programming language info into the programming language table
################################################################

import re
import sys
import pymysql
from bs4 import BeautifulSoup

datasource_id = '122'  # sys.argv[1]


def run():
    try:
        cursor.execute(insertProgLangQuery,
                       (datasource_id,
                        name,
                        programming_language))
        db.commit()
        print(name, " inserted into programming language table!\n")
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

selectQuery = 'SELECT name, html FROM lpd_indexes'


insertProgLangQuery = 'INSERT INTO lpd_programming_language (datasource_id, \
                                                             name, \
                                                             programming_language, \
                                                             last_updated) \
                        VALUES(%s, %s, %s, now())'

try:
    cursor.execute(selectQuery)
    listOfProjects = cursor.fetchall()

    for project in listOfProjects:
        name = project[0]
        html = project[1]
        print('\nworking on ', name)

        soup = BeautifulSoup(html, 'html.parser')

        regex = '\"programming_language\": "(.*?)",'
        listOfLang = re.findall(regex, str(soup))
        if listOfLang:
            for l in listOfLang:
                if ',' in l:
                    words = l.split(',')
                    for w in words:
                        print('language: ', w)
                        programming_language = w
                        run()
                else:
                    programming_language = l
                    print('language: ', programming_language)
                    run()

except pymysql.Error as err:
    print(err)
