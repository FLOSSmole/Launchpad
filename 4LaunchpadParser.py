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
# python 3LaunchpadParser.py <datasource_id> <password>
#
# purpose:
# inserts collects and inserts information into the projects table
################################################################

import re
import sys
import pymysql
from bs4 import BeautifulSoup

description = None
bug_supervisor = None
bug_tracker = None
driver = None
description = None

datasource_id = '272' # sys.argv[1]


def regexMaker(word):
    regex = '\"' + word + '\": (.*?),'
    match = re.findall(regex, str(body))
    if match:
        m = match[0]
        if '"' in m:
            result = m.split('"')[1]
            return result
        return m


def regexMaker2(word):
    regex = '\"' + word + '\": \"(.*?)\"'
    line = re.findall(regex, str(body))
    if line:
        word = line[0]
        return word


def regexMaker3(word, url):
    regex = '\"' + word + '_link\": \"' + url + '/~(.*?)\"'
    line = re.findall(regex, str(body))
    if line:
        word = line[0]
        return word


def run():
    try:
        cursor.execute(updateQuery,
                   (active,                                 # 1
                    bug_reported_acknowledgement,           # 2
                    bug_reporting_guidelines,               # 3
                    commercial_subscription_is_due,         # 4
                    date_created,                           # 5
                    description,                            # 6
                    download_url,                           # 7
                    freshmeat_project,                      # 8
                    homepage_url,                           # 9
                    qualifies_for_free_hosting,             # 10
                    screenshots_url,                        # 11
                    sourceforge_project,                    # 12
                    summary,                                # 13
                    title,                                  # 14
                    wiki_url,                               # 15
                    bug_supervisor,                         # 16
                    bug_tracker,                            # 17
                    development_focus,                      # 18
                    driver,                                 # 19
                    owner,                                  # 20
                    project_group,                          # 21
                    registrant,                             # 22
                    translation_focus,                      # 23
                    datasource_id,                          # 24
                    name))                                  # 25
        db.commit()
        print(name, "inserted into projects table!\n")
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

selectQuery = 'SELECT name, html FROM lpd_indexes'  # WHERE name = "albayanradioindicator" LIMIT 1'


updateQuery = 'UPDATE lpd_projects SET active = %s, \
                                        bug_reported_acknowledgement = %s, \
                                        bug_reporting_guidelines = %s, \
                                        commercial_subscription_is_due = %s, \
                                        date_created = %s, \
                                        description = %s, \
                                        download_url = %s, \
                                        freshmeat_project = %s, \
                                        homepage_url = %s, \
                                        qualifies_for_free_hosting = %s, \
                                        screenshots_url = %s, \
                                        sourceforge_project = %s, \
                                        summary = %s, \
                                        title = %s, \
                                        wiki_url = %s, \
                                        bug_supervisor = %s, \
                                        bug_tracker = %s, \
                                        development_focus = %s, \
                                        driver = %s, \
                                        owner = %s, \
                                        project_group = %s, \
                                        registrant = %s, \
                                        translation_focus = %s, \
                                        last_updated = now() \
            WHERE datasource_id = %s AND name = %s'

try:
    cursor.execute(selectQuery)
    listOfProjects = cursor.fetchall()

    for project in listOfProjects:
        name = project[0]
        html = project[1]
        print('\nworking on ', name)

        soup = BeautifulSoup(html, 'html.parser')
        body = soup.find('body', id='document')

        # runs a regex and finds the values
        active = regexMaker('active')
        print('1: ', active)

        bug_reported_acknowledgement = regexMaker2('bug_reported_acknowledgement')
        print('2: ', bug_reported_acknowledgement)

        bug_reporting_guidelines = regexMaker2('bug_reporting_guidelines')
        print('3: ', bug_reporting_guidelines)

        commercial_subscription_is_due = regexMaker('commercial_subscription_is_due')
        print('4: ', commercial_subscription_is_due)

        date_created = regexMaker2('date_created')
        print('5: ', date_created)

        try:
            descriptionLine = body.find('div', {'class': 'description'})
            desc = descriptionLine.find_all('p')
            description = ''
            for p in desc:
                for cont in p.contents:
                    if isinstance(cont, str):
                        description = description + cont
                    else:
                        for word in cont.contents:
                            if str(word).startswith('<wbr>') is False:
                                description = description + str(word)
                description = description + '\n'

            print('6: ', description)
        except:
            description = None
            print('6: ', description)

        download_url = regexMaker2('download_url')
        print('7: ', download_url)

        freshmeat_project = regexMaker2('freshmeat_project')
        print('8: ', freshmeat_project)

        homepage_url = regexMaker2('homepage_url')
        print('9: ', homepage_url)

        qualifies_for_free_hosting = regexMaker('qualifies_for_free_hosting')
        print('10: ', qualifies_for_free_hosting)

        screenshots_url = regexMaker2('screenshots_url')
        print('11: ', screenshots_url)

        sourceforge_project = regexMaker2('sourceforge_project')
        print('12: ', sourceforge_project)

        try:
            div = body.find('div', {'class': 'summary'})
            divP = div.find_all('p')
            summary = ''
            for d in divP:
                for cont in d.contents:
                    if isinstance(cont, str):
                        summary = summary + cont
                    else:
                        for word in cont.contents:
                            if str(word).startswith('<wbr>') is False:
                                summary = summary + str(word)
                summary = summary + '\n'
            print('13: ', summary)
        except:
            summary = None
            print("Unexpected error:", sys.exc_info()[0])

        title = regexMaker2('title')
        print('14: ', title)

        wiki_url = regexMaker2('wiki_url')
        print('15: ', wiki_url)

        bug_supervisor = regexMaker3('bug_supervisor', 'https://launchpad\.net/api/devel')
        print('16: ', bug_supervisor)

        bug_tracker = regexMaker3('bug_tracker', 'https://launchpad\.net/api/devel/bugs/bugtrackers')
        print('17: ', bug_tracker)

        try:
            p = body.find('p', id='development-focus')
            a = p.find('a')
            development_focus = a.contents[0]
            print('18: ', development_focus)
        except:
            print('18: no development focus')

        driver = regexMaker3('driver', 'https://launchpad\.net/api/devel')
        print('19: ', driver)

        owner = regexMaker3('owner', 'https://launchpad\.net/api/devel')
        print('20: ', owner)

        project_group = regexMaker3('project_group', 'https://launchpad.net/api/devel')
        print('21: ', project_group)

        registrant = regexMaker3('registrant', 'https://launchpad.net/api/devel')
        print('22: ', registrant)

        translation_focus = regexMaker3('translation_focus', 'https://launchpad.net/api/devel/obsolete-junk')
        print('23: ', translation_focus)

        run()

except pymysql.Error as err:
    print(err)

'''


# Not in script id:
#    date_next_suggest_packaging **** Deleted from update since not in html
#    security_contact            **** Deleted from update since not in html
#    license_info                **** Deleted from update since there is a
#                                       licenses table



'''
