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
# python 3LaunchpadParserLicenseTable.py <datasource_id> <password>
#
# purpose:
# inserts datasource id, name, and license info to license table
################################################################

import sys
import pymysql
from bs4 import BeautifulSoup

datasource_id = sys.argv[1]
dbpasswd = sys.argv[2]
dbhost = 'flossdata.syr.edu'
dbuser = 'megan'
dbschema = 'launchpad'


def run():
    try:
        cursor.execute(insertLicensesQuery,
                       (datasource_id,
                        name,
                        license_info))
        db.commit()
        print(name, " inserted into licenses table!\n")
    except pymysql.Error as err:
        print(err)
        db.rollback()


# establish database connection: SYR
try:
    db = pymysql.connect(host=dbhost,
                         user=dbuser,
                         passwd=dbpasswd,
                         db=dbschema,
                         use_unicode=True,
                         charset="utf8mb4")
    cursor = db.cursor()
except pymysql.Error as err:
    print(err)

selectQuery = 'SELECT name, html FROM lpd_indexes'

insertLicensesQuery = 'INSERT INTO lpd_licenses (datasource_id, \
                                                 name, \
                                                 license, \
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

        try:
            licenseList = soup.find('dl', id='licences')
            # print(licenseList)
            dd = licenseList.find('dd')
            # print(dd)
            licenseLines = dd.contents[0]
            # print(licenseLines)
            licenseGroup = licenseLines.strip()
            # print(licenseGroup)
            if ',' in licenseGroup:
                group = licenseGroup.split(',')
                for g in group:
                    splits = g.split('   ')
                    length = len(g.split('   ')) - 1
                    license_info = splits[length].strip()
                    print('license_info: ', license_info)
                    run()
            else:
                license_info = licenseGroup
                print('license_info: ', license_info)
                run()
        except:
            license_info = None
            print('license_info: NULL')
            run()

except pymysql.Error as err:
    print(err)
