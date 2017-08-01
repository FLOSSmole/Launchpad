
import sys
from launchpadlib.launchpad import Launchpad

cachedir = "projects/cache/"

def getLpProjList():
  launchpad = Launchpad.login_with('Data Gathering', 'production', cachedir)
  result = []
  total_projects = len(launchpad.projects)
  try:
    
    for project in launchpad.projects:
      result.append(project.name)
      print 'Getting project list.'
      print 'Currently getting project '+str(len(result))+' of '+str(total_projects)+'.'
      print project.self_link
    return result
  except KeyboardInterrupt:
    
    sys.exit(1)
  except Exception as e:
    
    print e
    sys.exit(1)

def getProjectInfo(name,launchpad):
  result = {}
  result['display_name'] = launchpad.projects[name].display_name
  result['web_link'] = launchpad.projects[name].web_link
  result['active'] = launchpad.projects[name].active
  result['bug_reported_acknowledgement'] = launchpad.projects[name].bug_reported_acknowledgement
  result['bug_reporting_guidelines'] = launchpad.projects[name].bug_reporting_guidelines
  result['commercial_subscription_is_due'] = launchpad.projects[name].commercial_subscription_is_due
  result['date_created'] = launchpad.projects[name].date_created
  result['date_next_suggest_packaging'] = launchpad.projects[name].date_next_suggest_packaging
  result['description'] = launchpad.projects[name].description
  result['download_url'] = launchpad.projects[name].download_url
  result['freshmeat_project'] = launchpad.projects[name].freshmeat_project
  result['homepage_url'] = launchpad.projects[name].homepage_url
  result['license_info'] = launchpad.projects[name].license_info
  result['qualifies_for_free_hosting'] = launchpad.projects[name].qualifies_for_free_hosting
  result['screenshots_url'] = launchpad.projects[name].screenshots_url
  result['sourceforge_project'] = launchpad.projects[name].sourceforge_project
  result['summary'] = launchpad.projects[name].summary
  result['title'] = launchpad.projects[name].title
  result['wiki_url'] = launchpad.projects[name].wiki_url
  if launchpad.projects[name].bug_supervisor:
    result['bug_supervisor'] = launchpad.projects[name].bug_supervisor.name
  if launchpad.projects[name].bug_tracker:
    result['bug_tracker'] = launchpad.projects[name].bug_tracker.name
  if launchpad.projects[name].development_focus:
    result['development_focus'] = launchpad.projects[name].development_focus.name
  if launchpad.projects[name].driver:
    result['driver'] = launchpad.projects[name].driver.name
  if launchpad.projects[name].owner:
    result['owner'] = launchpad.projects[name].owner.name
  if launchpad.projects[name].project_group:
    result['project_group'] = launchpad.projects[name].project_group.name
  if launchpad.projects[name].registrant:
    result['registrant'] = launchpad.projects[name].registrant.name
  if launchpad.projects[name].security_contact:
    result['security_contact'] = launchpad.projects[name].security_contact.name
  if launchpad.projects[name].translation_focus:
    result['translation_focus'] = launchpad.projects[name].translation_focus.name
  return result
