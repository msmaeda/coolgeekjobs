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

from web import jobreport
from app import model


MAX_ITEMS=250
#from google.appengine.api import memcache
#TODO: Add this in for queries to speed things up"""

class AdminHandler(BasePage):
    """ Handler for report requests
    """

    def __init__(self):
        """ Create a new handler.
        """
        super(AdminHandler, self).__init__()
        
    def get(self, offset=''):
        """ Serve up base admin page.
        """
        self.set_template('templates/admin/admin.html')

        jobs        = model.Job.all()
        
        filter  = 'all'
        
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
                short_desc  = jobreport._remove_html_tags(job.desc)
                    
                j   = {'key'    : job.key().id(),
                       'date'   : job.entry_date,
                       'title'  : job.title,
                       'link'   : job.link,
                       'short'  : (short_desc[:240]) if len(short_desc) > 240 else short_desc,
                       'tags'   : [jobreport._make_tags(tag) for tag in job.tag_info]}
                
                records.append(j)

                cur += 1
            elif cur == MAX_ITEMS:
                has_more    = True
                
            idx += 1
        
        if current_offset >= MAX_ITEMS:
            self.add_template_value('has_previous', True)
            self.add_template_value('filter',filter)
            self.add_template_value('previous_offset',(current_offset - MAX_ITEMS))
            
        if has_more:
            self.add_template_value('has_more', True)
            self.add_template_value('filter',filter)
            self.add_template_value('offset',(current_offset + MAX_ITEMS))        
                 
        self.add_template_value('jobs',records)        
        self.write_page()

class AdminKnownIssuesHandler(BasePage):
    """ Handler for report requests
    """

    def __init__(self):
        """ Create a new handler.
        """
        super(AdminKnownIssuesHandler, self).__init__()
        
    def get(self):
        """ Serve up base admin page.
        """
        self.set_template('templates/admin/admin.html')

        jobs        = model.Job.all()

        records = []
        
        jobs.order("-entry_date")
        
        add_job = False
        
        bad_titles  = ['tech','paid','sale','associate','market']
        
        for job in jobs:
            short_desc  = jobreport._remove_html_tags(job.desc)
            
            # If tags are empty
            if len(job.tag_info) == 0:
                add_job = True
            
            for bad in bad_titles:
                if bad in job.title.lower():
                    add_job = True
            
            if add_job:
                    
                j   = {'key'    : job.key().id(),
                       'date'   : job.entry_date,
                       'title'  : job.title,
                       'link'   : job.link,
                       'short'  : (short_desc[:240]) if len(short_desc) > 240 else short_desc,
                       'tags'   : [jobreport._make_tags(tag) for tag in job.tag_info]}
                    
                records.append(j)
     
        self.add_template_value('jobs',records)        
        self.write_page()
        
class AdminJobHandler(BasePage):
    """ Handler for report requests
    """

    def __init__(self):
        """ Create a new handler.
        """
        super(AdminJobHandler, self).__init__()
        
    def get(self, action='', jobid='', tagname=''):
        """ Serve up job admin actions """
        job     = model.Job.get_by_id(int(jobid))
        
        j   = {'title':         job.title,
               'entry_date':    job.entry_date,
               'link':          job.link,
               'desc':          job.desc,
               'tags':          [jobreport._make_tags(tag) for tag in job.tag_info]}
        
        if action == 'deletejob':
            self.set_template('templates/admin/admindeletejob.html')
            self.add_template_value('jobid',jobid)
            self.add_template_value('job',j)
        elif action == 'deletejobconfirm':
            title   = job.title
            job.delete()
            
            self.set_template('templates/admin/admindeletejobconfirm.html')
            self.add_template_value('title',title)
        elif action == 'editjobtags':
            self.set_template('templates/admin/admineditjob.html')
            self.add_template_value('jobid',jobid)
            self.add_template_value('job',j)
        elif action == 'removetag':
            self.set_template('templates/admin/admineditjob.html')
            self.add_template_value('jobid',jobid)
            self.add_template_value('job',j)
            
        self.write_page()    

class AdminTagHandler(BasePage):
    """ Handler for report requests
    """

    def __init__(self):
        """ Create a new handler.
        """
        super(AdminTagHandler, self).__init__()
        
    def get(self, jobid='', tagname=''):
        """ Handler for tag admin actions """
                
        job         = model.Job.get_by_id(int(jobid))
        
        newtaglist  = []
        actualtag   = ''
        
        if tagname  == 'objectivec':
            actualtag   = 'Objective C'
        elif tagname == 'cplus':
            actualtag   = 'C++'
        elif tagname == 'csharp':
            actualtag   = 'C#'
        else:
            actualtag   = tagname
        
        for tag in job.tag_info:
            if tag != actualtag:
                newtaglist.append(tag)
                
        job.tag_info    = newtaglist
        job.put()
        
        j   = {'title':         job.title,
               'entry_date':    job.entry_date,
               'link':          job.link,
               'desc':          job.desc,
               'tags':          [jobreport._make_tags(tag) for tag in newtaglist]}
                
        
        self.set_template('templates/admin/admineditjob.html')
        self.add_template_value('message', actualtag + " removed")
        self.add_template_value('jobid',jobid)
        
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
        [('/_admincoolgeeks', AdminHandler),
         ('/_admincoolgeeks/all/(.*)', AdminHandler),
         ('/_admincoolgeeks/removetag/(.*)/(.*)', AdminTagHandler),
         ('/_admincoolgeeks/knownissues', AdminKnownIssuesHandler),
         ('/_admincoolgeeks/(.*)/(.*)', AdminJobHandler)],
        debug=True)

def main():
    run_wsgi_app(application())

if __name__ == "__main__":
    main()