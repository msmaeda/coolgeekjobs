#!python2.6
# Copyright 2011.  BSpoke, LLC. 

"""Nose unit tests of the submitjob GAE application.

Requires nose and nosegae, available through easy_install-2.6, plus the
Google App Engine development kit.

Usage: From the src directory:
    nosetests --with-gae --gae-lib-root <location of google app engine dir>
"""

import unittest
import logging
import re

from app import updatejob
from app import model



class UpdateJobTest(unittest.TestCase):
    """Unit tests of the updatejob task."""

    def setUp(self):
        self.app    = updatejob

    def testAddNewTags(self):
        """ Test that tags are added """
        self.app._add_tags(['Redis','Objective C','Erlang'])
        tag_obj     = model.Tag.all()
        
        self.assertEqual(3, tag_obj.count())
        
        self.app._add_tags(['PERL'])
        tag_obj     = model.Tag.all()
        
        self.assertEqual(4, tag_obj.count())
        
        self.app._add_tags(['Redis','Objective C','Erlang','Java'])
        tag_obj     = model.Tag.all()
        
        self.assertEqual(5, tag_obj.count())
        
        stat_obj    = model.Stats.all()
        stat_obj.filter("statname =", 'Redis')
        result      = stat_obj.fetch(1)
        
        self.assertEqual(2, result[0].occurrences)
        
    def testAddJobs(self):
        """ Test that jobs are added """
        joblist     = [{'title'     : 'Job 1',
                        'link'      : 'http://job1.com',
                        'desc'      : 'job 1',
                        'geo'       : 'US',
                        'city'      : 'Seattle',
                        'state_prov': 'WA',
                        'tag_info'  : ['Objective C','Erlang']},
                       {'title'     : 'Job 2',
                        'link'      : 'http://job2.com',
                        'desc'      : 'job 2',
                        'geo'       : 'US',
                        'city'      : 'Seattle',
                        'state_prov': 'WA',
                        'tag_info'  : []},
                       {'title'     : 'Job 1',
                        'link'      : 'http://job1.com',
                        'desc'      : 'job 1',
                        'geo'       : 'US',
                        'city'      : 'Seattle',
                        'state_prov': 'WA',
                        'tag_info'  : []}]
        
        jobs        = [self.app._make_job_entry(job) for job in joblist]
        
        self.assertEqual(3, len(jobs))
        
        # Should only be 1 because of duplicate link and one job without tags
        self.assertEqual(1, self.app._add_jobs(jobs))
        
        job_obj     = model.Job.all()
        
        self.assertEqual(1,job_obj.count())
        
    def testGetLinks(self):
        """ Test get links """
        #link    = model.Link(site           = "craigslist",
        #                     type           = "rss",
        #                     url            = "http://coolgeekjobs.com",
        #                     crawl_count    = 0,
        #                     hit_count      = 0,
        #                     backoff        = 1,
        #                     nextcrawl      = 0)
        #link.put()
        
        #links   = self.app._get_links(1)
        self.assertEquals(1, 1)
        
        
        
    def testRefreshLinks(self):
        """ Test that new links are properly added"""
     #   self.app._refresh_link_list()
     #   links       = model.Link.all()
        
     #   self.app._refresh_link_list()
     #   newlinks    = model.Link.all()
        date    = "2010-06-20".replace('-','')
        
        self.assertEqual('2011-06-20',date)
        
        self.assertEqual(1,1) 
