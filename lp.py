# Carter Kozak
# c4kofony@gmail.com
# ckozak@elon.edu

#collector for launchpad data

# flossmole.org

# Copyright (C) 2011 Carter Kozak

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import time
import lpSetup
from dbSetup import dbConnect
from launchpadlib.launchpad import Launchpad
from project_list import *
from sqlalchemy.sql import func
import ConfigParser

config = ConfigParser.RawConfigParser()
config.read('C:\Users\groth\Desktop\launch\lp.conf')
cachedir = "projects/cache/"
launchpad = Launchpad.login_with('Data Gathering', 'production', cachedir)
count = 0

try:
  PROJECTS = config.get('launchpad','projects')
  LICENSES = config.get('launchpad','licenses')
  BUG_TAGS = config.get('launchpad','bug_tags')
  LANGUAGES = config.get('launchpad','languages')
  MILESTONES = config.get('launchpad','milestones')
  RELEASES = config.get('launchpad','releases')
  SERIES_TABLE = config.get('launchpad','series_table')
  DATASOURCE = config.getint('launchpad','datasource')

  db=dbConnect(config.get('launchpad','db_user'),config.get('launchpad','db_pass'),config.get('launchpad','db_address'))
  
except Exception as e:
  print e
  print 'error reading lp.conf'
  sys.exit(1)


projects = db.getTable(PROJECTS)
licenses = db.getTable(LICENSES)
bug_tags = db.getTable(BUG_TAGS)
languages = db.getTable(LANGUAGES)
milestones = db.getTable(MILESTONES)
releases = db.getTable(RELEASES)
series_table = db.getTable(SERIES_TABLE)

if len(db.connection.execute("SELECT name FROM "+PROJECTS+" WHERE datasource_id = "+str(DATASOURCE)+";").fetchall()) < len(launchpad.projects)-100: #the 100 allows for growth over a couple hours/days.
  i = projects.insert()
  resultList = getLpProjList()
  for project_name in resultList:
    try:
      db.connection.execute(projects.insert().values(name=project_name,last_updated=func.now(),datasource_id=DATASOURCE))
    except Exception as e:
      print e
      

names = db.connection.execute("SELECT name FROM "+PROJECTS+" WHERE datasource_id = "+str(DATASOURCE)+" AND display_name IS NULL;")
for result in names:
  print result['name']
  count = count + 1
  print count
  if result['name'] != 'indexu' and result['name'] != 'mattirn':
    for license in launchpad.projects[result['name']].licenses:
        try:
            db.connection.execute(licenses.insert().values(name=result['name'],datasource_id = DATASOURCE,last_updated = func.now(),license = license))    
        except Exception as e:
            print e
        
    
    for bug_tag in launchpad.projects[result['name']].official_bug_tags:
        try:
            db.connection.execute(bug_tags.insert().values(name=result['name'],datasource_id = DATASOURCE,last_updated = func.now(),official_bug_tag = bug_tag))    
        except Exception as e:       
            print e
        
    if launchpad.projects[result['name']].programming_language:
        langs = launchpad.projects[result['name']].programming_language.split(',')
        for language in langs:
            try:
                db.connection.execute(languages.insert().values(name=result['name'],datasource_id = DATASOURCE,last_updated = func.now(),programming_language = language.strip()))    
            except Exception as e:                
                print e        
            
    
    for milestone in launchpad.projects[result['name']].all_milestones.entries:
        try:
            db.connection.execute(milestones.insert().values(datasource_id = DATASOURCE,last_updated = func.now(),name=milestone['name'], title=milestone['title'], summary = milestone['summary'],code_name = milestone['code_name'], date_targeted = milestone['date_targeted'],is_active = milestone['is_active'],project_name = result['name']))
        #official_bug_tags?  meh...
        except Exception as e:
            print e
            
    for release in launchpad.projects[result['name']].releases.entries:
        try:
            db.connection.execute(releases.insert().values(datasource_id = DATASOURCE,last_updated = func.now(),display_name = release['display_name'],title = release['title'],milestone=launchpad.projects[result['name']].getMilestone(name=release['milestone_link'][release['milestone_link'].find('+milestone/')+11:]).name, version = release['version'], project_name = result['name'], release_notes = release['release_notes'],changelog = release['changelog'], date_created = release['date_created'], date_released = release['date_released']))
        except Exception as e:
            print e
        
    
    
    for series in launchpad.projects[result['name']].series.entries:
        try:
            db.connection.execute(series_table.insert().values(datasource_id = DATASOURCE, last_updated = func.now(), bug_reported_acknowledgement = series['bug_reported_acknowledgement'],display_name = series['display_name'], title = series['title'], status = series['status'], date_created = series['date_created'], active = series['active'], name = series['name'], summary = series['summary'], bug_reporting_guidelines = series['bug_reporting_guidelines'], project_name = result['name']))
        except Exception as e:
            print e
        
    #major project data insert
    try:
        db.connection.execute(projects.update().where(projects.c.datasource_id == DATASOURCE).where(projects.c.name == result['name']).values(getProjectInfo(result['name'],launchpad),last_updated = func.now()))
    except Exception as e:
        print e
    
