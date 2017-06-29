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
# python 5LaunchpadParserMilestoneTable.py <datasource_id> <password>
#
# purpose:
# inserts milestone information into the milestone table
################################################################

import re
import sys
import pymysql
from bs4 import BeautifulSoup

datasource_id = '122'  # sys.argv[1]


def run():
    try:
        cursor.execute(insertMilestoneQuery,
                       (datasource_id,
                        name,
                        project_name,
                        title,
                        summary,
                        code_name,
                        series,
                        date_targeted,
                        date_released))
        db.commit()
        print(name, " inserted into milestone table!\n")
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

selectQuery = 'SELECT name, milestoneHtml FROM lpd_indexes'

insertMilestoneQuery = 'INSERT INTO lpd_milestones (datasource_id, \
                                                    name, \
                                                    project_name, \
                                                    title, \
                                                    is_active, \
                                                    summary, \
                                                    code_name, \
                                                    series, \
                                                    date_targeted, \
                                                    date_released, \
                                                    last_updated) \
                       VALUES(%s, %s, %s, %s, NULL, %s, %s, %s, %s, %s, now())'
  
try:
    cursor.execute(selectQuery)
    listOfProjects = cursor.fetchall()

    for project in listOfProjects:
        project_name = project[0]
        html = project[1]
        print('\nworking on ', project_name)

        try:
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table', id='milestones')
            # print(table)

            tr = table.find_all('tr')
            # print(tr)
            for t in tr:
                td = t.find_all('td')
                # print(td)
                for line in td:
                    # print(line)
                    regexName = '<a href=\"/' + project_name + '\/\+milestone/(.*?)\">(.*?)</a>'
                    nameFinder = re.findall(regexName, str(line))
                    if nameFinder:
                        name = nameFinder[0][0]
                        title = nameFinder[0][1]
                        if '"' in title:
                            codeNameRegex = '"(.*?)"'
                            codeNameFinder = re.findall(codeNameRegex, str(title))
                            if codeNameFinder:
                                code_name = codeNameFinder[0]
                                print('codename: ', code_name)
                            print('name: ', name)
                        print('title: ', title)

                    regexSeries = '<a href=\"/' + project_name + '/(.*?)\">(.*?)</a>'
                    seriesFinder = re.findall(regexSeries, str(line))
                    if seriesFinder:
                        if seriesFinder[0][0] == seriesFinder[0][1]:
                            series = seriesFinder[0][1]
                            print('series: ', series)

                # both dates there or are labeled 'None'
                dateRegexBoth = 'title=\"(.*?)\">(.*?)</span>\s*</td>, <td>\s*<span title=\"(.*?)\">(.*?)</span>\s*</td>, <td>\s*(.*?)\s*</td>'
                dateFinder = re.findall(dateRegexBoth, str(td))
                if dateFinder:
                    date_targeted = dateFinder[0][0]
                    print('date_targeted: ', date_targeted)
                    date_released = dateFinder[0][3]
                    print('date_released: ', date_released)
                    summary = dateFinder[0][4]
                    print('summary: ', summary)

                # second date is not released yet
                dateRegexNoRight = '<span title=\"(.*?)\">(.*?)</span>\s*</td>, <td>\s*(.*?)\s*</td>, <td>(.*?)\s*</td>'
                dateFinder2 = re.findall(dateRegexNoRight, str(td))
                if dateFinder2:
                    date_targeted = dateFinder2[0][0]
                    print('date_targeted: ', date_targeted)
                    date_released = dateFinder2[0][2]
                    print('date_released: ', date_released)
                    summary = dateFinder2[0][3]
                    print('summary: ', summary)

                # first date is None
                dateRegexNoRight = '<span title=\"(.*?)\">\s*(.*?)\s*</span>\s*</td>, <td>\s*<span title=\"(.*?)\">(.*?)</span>\s*</td>, <td>(.*?)\s*</td>'
                dateFinder2 = re.findall(dateRegexNoRight, str(td))
                if dateFinder2:
                    date_targeted = dateFinder2[0][1]
                    print('date_targeted: ', date_targeted)
                    date_released = dateFinder2[0][2]
                    print('date_released: ', date_released)
                    summary = dateFinder2[0][4]
                    print('summary: ', summary)
                run()
            print('\n')

        except:
            print('There are no milestones associated with ' + project_name)

except pymysql.Error as err:
    print(err)
