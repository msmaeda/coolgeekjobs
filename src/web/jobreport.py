#!python2.5

"""Script for generating jobs listings from cool geek jobs_report datastore.
"""

__author__ = 'Matt Maeda <msmaeda@gmail.com>'

import re
import logging
import datetime

from web.base import BasePage
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson as json

from app import model

MAX_ITEMS   = 20

#from google.appengine.api import memcache
#TODO: Add this in for queries to speed things up"""

class JobListingHandler(BasePage):
    """ Handler for report requests
    """

    def __init__(self):
        """ Create a new handler.
        """
        super(JobListingHandler, self).__init__()
        
    def get(self, filter='', offset=''):
        """ Serve up base report page.
        """        
        current_offset  = 0
        
        self.set_template('templates/index.html')
        
        languages       = model.Languages.all()
        languages.order("display")
        
        self.add_template_value('languages', languages)
        
        jobs        = model.Job.all()
        
        if filter != '':                    
            if filter != 'all':
                if filter == 'objectivec':
                    newfilter   = 'Objective C'
                elif filter == 'csharp':
                    newfilter   = 'C#'
                elif filter == 'cplus':
                    newfilter   = 'C++'
                else:
                    newfilter   = filter
                    
                jobs.filter("tag_info =", newfilter)
                self.add_template_value('skilltype', newfilter.upper())
            else:
                self.add_template_value('skilltype', '')
                
            if offset == '':
                current_offset  = 0
            else:
                current_offset  = int(offset)                
            
        else:            
            # If user is logged in, then display user preference.  If not, just
            # display most current job
            filter          = 'all'
            current_offset  = 0
            self.add_template_value('skilltype', '')

        records = []
        
        jobs.order("-entry_date")
        jobs.fetch(MAX_ITEMS)
        
        # Hacky, but limit and offset not working properly for me
        idx         = 0
        cur         = 0
        has_more    = False
        
        for job in jobs:
            if idx  >= current_offset and cur < MAX_ITEMS:
                short_desc  = _remove_html_tags(job.desc)
                    
                j   = {'key'    : job.key().id(),
                       'date'   : job.entry_date,
                       'title'  : job.title,
                       'link'   : job.link,
                       'short'  : (short_desc[:240]) if len(short_desc) > 240 else short_desc,
                       'tags'   : [_make_tags(tag) for tag in job.tag_info]}
                
                records.append(j)

                cur += 1
            elif cur == MAX_ITEMS:
                has_more    = True
                
            idx += 1
        
        if current_offset >= MAX_ITEMS:
            self.add_template_value('has_previous', True)
            self.add_template_value('filter',filter)
            self.add_template_value('previous_offset',(current_offset - MAX_ITEMS))
        else:
            self.add_template_value('has_previous', False)
            
        if has_more:
            self.add_template_value('has_more', True)
            self.add_template_value('filter',filter)
            self.add_template_value('offset',(current_offset + MAX_ITEMS))
        else:
            self.add_template_value('has_more', False)        
                 
        self.add_template_value('jobs',records)
        
        self.write_page()

def _make_tags(tag):
    if tag == 'C#':
        return {'C#':'csharp'}
    elif tag == 'C++':
        return {'C++':'cplus'}
    elif tag == 'Objective C':
        return {'Objective C':'objectivec'}
    else:
        return {tag:tag}
    
def _remove_html_tags(text):
    striptags   = re.compile(r'<.*?>')
    stripspaces = re.compile(r'\s+')
    newtext     = striptags.sub(' ', text)
    
    return      stripspaces.sub(' ', newtext)

class JobHandler(BasePage):
    """ Handler for summary requests
    """

    def __init__(self):
        """ Create a new handler.
        """
        super(JobHandler, self).__init__()     

    def get(self, key=''):
        """ Handler for job information requests.
        """
        job             = model.Job.get_by_id(int(key))
        
        j   = {'title':         job.title,
               'entry_date':    job.entry_date,
               'link':          job.link,
               'desc':          job.desc,
               'tags':          [_make_tags(tag) for tag in job.tag_info]}
        
        languages       = model.Languages.all()
        languages.order("display")
                
        self.set_template('templates/job.html')
        self.add_template_value('languages',languages)
        self.add_template_value('job',j)
        
        self.write_page()
        
class JsonHandler(BasePage):
    """ Handler for json download for data transfer off of GAE
    """

    def __init__(self):
        """ Create a new handler.
        """
        super(JsonHandler, self).__init__()

    def get(self):
        """ Display default page.
        """
        logging.info("Get JSON download ")
        self.set_template('templates/json_download.html')
        self.write_page()

    def post(self):
        """ Process an HTTP POST request for report and
            generate a tab-delimited file for download
        """
        logging.info("Starting JSON download")
    

def application():
    """Instantiate a report application object."""

    return webapp.WSGIApplication(
        [('/', JobListingHandler),         
         ('/morejobs/(.*?)/(.*?)', JobListingHandler),
         ('/job/(.*?)', JobHandler),
         ('/json', JsonHandler)],
        debug=True)

def main():
    run_wsgi_app(application())

if __name__ == "__main__":
    main()