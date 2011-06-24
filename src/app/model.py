# Copyright 2011.  BSpoke, LLC.

"""CoolGeekJobs data model."""

__author__ = 'Matt Maeda <msmaeda@gmail.com>'

from google.appengine.ext import db

class Tag(db.Model):
    """A list entry for Job containing tag information."""
    """Key name is tag name"""  

class Job(db.Model):
    """A job listing from a crawler instance scanning job boards."""
    title       = db.StringProperty(required=True)
    entry_date  = db.DateTimeProperty(required=True, auto_now_add=True)
    link        = db.StringProperty(required=True)
    desc        = db.TextProperty(required=True)
    geo         = db.StringProperty(required=False)
    state_prov  = db.StringProperty(required=False)
    city        = db.StringProperty(required=False)
    tag_info    = db.StringListProperty(required=True, default=None)
    
class User(db.Model):
    """A user signed up to receive notifications."""
    first       = db.StringProperty(required=False)
    last        = db.StringProperty(required=False)
    username    = db.StringProperty(required=True)
    password    = db.StringProperty(required=True)
    email       = db.EmailProperty(required=True)
    conf_key    = db.StringProperty(required=True)
    email_conf  = db.BooleanProperty(required=True, default=False)
    entry_date  = db.DateTimeProperty(required=True, auto_now_add=True)
    ios_dev_id  = db.StringProperty(required=False)
    and_dev_id  = db.StringProperty(required=False)
    mis_dev_id  = db.StringProperty(required=False)
    tag_types   = db.StringListProperty(required=True, default=None)
    plan_type   = db.StringProperty(required=True, choices=set(['immediate',
                                                                'hourly',
                                                                'daily',
                                                                'weekly']))    
    plan_date   = db.DateTimeProperty(required=True)    
    want_email  = db.BooleanProperty(required=True, default=True)
    last_login  = db.DateTimeProperty(required=False)
    session     = db.StringProperty(required=False)
    
class Crawler(db.Model):
    """Stores crawler information"""
    crawlid     = db.IntegerProperty(required=True)
    last_crawl  = db.DateTimeProperty(required=True, auto_now_add=True)
    crawl_count = db.IntegerProperty(required=True)
    total_links = db.IntegerProperty(required=True)
    
class Link(db.Model):
    """Stores link information"""
    site        = db.StringProperty(required=True)
    type        = db.StringProperty(required=True)
    url         = db.StringProperty(required=True)
    crawl_count = db.IntegerProperty(required=True)
    hit_count   = db.IntegerProperty(required=True)
    backoff     = db.IntegerProperty(required=True)
    nextcrawl   = db.IntegerProperty(required=True)
    city        = db.StringProperty(required=False)
    state       = db.StringProperty(required=False)
    country     = db.StringProperty(required=False)

class Languages(db.Model):
    """ Stores tag link information """
    name        = db.StringProperty(required=False)
    display     = db.StringProperty(required=True)
    logo        = db.StringProperty(required=True)
    
class Stats(db.Model):
    statname    = db.StringProperty(required=True)
    date        = db.DateProperty(required=True, auto_now_add=True)
    occurrences = db.IntegerProperty(required=True)
