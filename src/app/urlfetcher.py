# Copyright 2011.  BSpoke, LLC.

"""CoolGeekJobs generic url fetcher class."""

__author__ = 'Matt Maeda <msmaeda@gmail.com>'

import feedparser
import re

from google.appengine.api import urlfetch

class RssUrlFetcher:
    """ Generic RSS url fetcher class """
    def __init__(self, url, name):
        self.url    = url
        self.name   = name
        
    
    def entries(self):
        """ Fetch entries from RSS feed """
        jobs        = []
        result      = urlfetch.fetch(self.url)
        
        if result.status_code == 200:
            feed        = feedparser.parse(result.content)
            
            
            for entry in feed.entries:
                
                if not _ignore_jobs(entry['description']):
                    continue
                
                job                 = {}
        
                job['title']        = entry.title
                job['link']         = entry.link
                job['desc']         = entry.description
                job['geo']          = ''
                job['state_prov']   = ''
                job['city']         = ''
                job['tag_info']     = _tag_jobs(entry['description'])
                                    
                jobs.append(job)
            
        return jobs
    
def _tag_jobs(description):
    """ Tags job descriptions """
    tags   = {'python'      :'Python',
              ' ror '       :'Ruby',
              'ruby'        :'Ruby',
              'perl'        :'PERL',
              'erlang'      :'Erlang',
              'java'        :'Java',
              'php'         :'PHP',
              'objective c' :'Objective C',
              'objective-c' :'Objective C',
              'obj c'       :'Objective C',
              'obj-c'       :'Objective C',
              ' ios '       :'Objective C',
              'iphone'      :'Objective C',
              'ipad'        :'Objective C',
              'android'     :'Android',
              "C\#"         :'C#',
              "C\+\+"       :'C++',
              '\.net'       :'.NET',
              'mysql'       :'MySQL',
              'oracle'      :'Oracle',
              ' lua '       :'Lua',
              'redis'       :'Redis'}
    
    tag_info    = []
    
    if description is not None:
    
        for tag in tags.keys():
            if re.search(tag, description, re.IGNORECASE):
                tag_info.append(tags[tag])
    
    return tag_info
    
def _ignore_jobs(description):
    """ Checks for non-telecommute jobs """
    ignore  = {'no telecommute'                 : '',
               'no telecommuting'               : '',
               'telecommuting is not an option' : '',
               'telecommute is not an option'   : ''}
    
    is_valid    = True
    
    if description is not None:
    
        for ignore in ignore.keys():
            if re.search(ignore, description, re.IGNORECASE):
                is_valid = False        
    
    return is_valid    
            
                
        
    
