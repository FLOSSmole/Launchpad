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
# python 8LaunchpadParserreleaseTable.py <datasource_id> <password>
#
# purpose:
# inserts release info into release table
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

def run():
    try:
        cursor.execute(insertReleasesQuery,
                       (datasource_id,      #
                        display_name,       #
                        title,              #
                        milestones,         #
                        version,            #
                        project_name,       #
                        release_notes,      #
                        changelog,          #
                        date_created,       #
                        date_released,      #
                        html))              #
        db.commit()
        print(project_name, "inserted into releases table!\n")
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

selectQuery = 'SELECT name, project_name FROM lpd_milestones'  # where project_name = "k8s-docker-suite-app-murano" and name = "1.0.0" LIMIT 1'


insertReleasesQuery = 'INSERT INTO lpd_releases (datasource_id, \
                                                display_name, \
                                                title, \
                                                milestone, \
                                                version, \
                                                project_name, \
                                                release_notes, \
                                                changelog, \
                                                date_created, \
                                                date_released,\
                                                html, \
                                                last_updated) \
                    VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, now())'

hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

try:
    cursor.execute(selectQuery)
    listOfProjects = cursor.fetchall()

    for project in listOfProjects:
        milestones = project[0]
        project_name = project[1]
        print('\nworking on ', project_name, ' ', milestones)

        url = 'https://launchpad.net/' + project_name +'/+milestone/' + milestones
        print(url)

        changelog = None
        releaser_notes = None

        try:
            req = urllib2.Request(url, headers=hdr)
            html = urllib2.urlopen(req).read()
            soup = BeautifulSoup(html, 'html.parser')
            details = soup.find('div', id='Release-details')
            # print(details)

            regexDisplayName = '<dt>Project:</dt>\s*<dd><a class=\"bg-image\" href=\"/(.*?)\" style=\"background-image: url(.*?)\">(.*?)</a></dd>'
            nameFinder = re.findall(regexDisplayName, str(details))
            if nameFinder:
                display_name = nameFinder[0][2]
                print('display name: ', display_name)
            else:
                regexDisplayName = '<dt>Project:</dt>\s*<dd><a class=\"sprite product\" href=\"/(.*?)\">(.*?)</a></dd>'
                nameFinder = re.findall(regexDisplayName, str(details))
                if nameFinder:
                    display_name = nameFinder[0][1]
                    print('display name: ', display_name)

            dl = details.find('dl', id='version')
            dd = dl.find('dd')
            if dd:
                version = dd.contents[0]
                print('version: ', version)

            regexReleased = '<dt>Released:</dt>\s*<dd><span title=\"(.*?)\">'
            releasedDateFinder = re.findall(regexReleased, str(details))
            if releasedDateFinder:
                dateSplit = releasedDateFinder[0].split(' ')
                date_released = dateSplit[0] + ' ' + dateSplit[1]
                print('date released: ', date_released)

            regexCreated = '<dt>Release registered:</dt>\s*<dd><span title=\"(.*?)\">'
            createdDateFinder = re.findall(regexCreated, str(details))
            if createdDateFinder:
                dateSplit = createdDateFinder[0].split(' ')
                date_created = dateSplit[0] + ' ' + dateSplit[1]
                print('date created: ', date_created)

            div = soup.find('div', id='release-notes')
            if div:
                p = div.find('p')
                release_notes = ''
                for line in p:
                    if isinstance(line, str):
                        release_notes = release_notes + line
                    else:
                        for l in line.contents:
                            if isinstance(l, str):
                                release_notes = release_notes + l
                print('release notes: ', release_notes)

            divChangelog = soup.find('div', id='changelog')
            if divChangelog:
                changelog = ''
                ps = divChangelog.find_all('p')
                logLine = ps[0].contents
                for l in logLine:
                    if isinstance(l, str):
                        changelog = changelog + l
                print('changelog: ', changelog)

            regexTitle = '<title>(.*?):(.*?)</title>'
            titleFinder = re.findall(regexTitle, str(soup))
            if titleFinder:
                title = titleFinder[0][1] + ' ' + titleFinder[0][0]
                print('title: ', title)

            run()

        except urllib2.HTTPError as herror:
            print(herror)

except pymysql.Error as err:
    print(err)
