#!python2.5
# Copyright 2011.  BSpoke, LLC.

"""Script for updating job listings from urlfetcher."""

__author__ = 'Matt Maeda <msmaeda@gmail.com>'

import logging
import datetime

from BeautifulSoup import BeautifulSoup

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch import DownloadError 

from app import model
from app import urlfetcher

CRAWLS_PER_WEEK = 168

class UpdateJobProcess(webapp.RequestHandler):
    """ Performs updates to job listings """
    def __init__(self):
        self.sites  = ['craigslist']

    def get(self):
        """ Call to execute job update process."""
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Job Update Crawl initiated...')
        self.update_listings()        
                
    def update_listings(self):
        """ Makes the call to sites to update job listings """
        crawler = model.Crawler.get_by_key_name("coolgeekcrawler")
        
        if crawler is None:
            crawler = model.Crawler(key_name    ="coolgeekcrawler",
                                    crawlid     = 1,
                                    crawl_count = 0,
                                    total_links = 0)
            crawler.put()
            
        links   = _get_links(crawler.crawlid)
        
        # Update this before the run in case of Deadline error
        logging.info("Current crawlid is " + str(crawler.crawlid))
        current_crawlid             = crawler.crawlid
        crawler.crawlid             = crawler.crawlid + 1
        crawler.crawl_count         = crawler.crawl_count + 1
        crawler.put()
        
        if links is not None:
            
            for link in links:
                # Check link type
                if link.type    == "rss":
                    try:
                        fetcher     = urlfetcher.RssUrlFetcher(link.url,link.site)
                        entries     = [_make_job_entry(j) for j in fetcher.entries()]
                        jobs_added  = _add_jobs(entries)
                        
                        # Implement backoff algorithm to conserve resouce usage
                        if jobs_added > 0:
                            link.backoff    = 1
                            link.nextcrawl  = current_crawlid + 1
                            link.put()
                            
                        else:
                            if link.backoff == CRAWLS_PER_WEEK:
                                link.nextcrawl = current_crawlid + link.backoff
                            else:
                                if (2 * link.backoff) > CRAWLS_PER_WEEK:
                                    link.backoff    = CRAWLS_PER_WEEK
                                    link.nextcrawl  = current_crawlid + CRAWLS_PER_WEEK
                                else:
                                    link.backoff    = 2 * link.backoff
                                    link.nextcrawl  = current_crawlid + (2 * link.backoff)
                            link.put()
                    except DownloadError:       
                        logging.error("Connection refused to " + link.url)
                
                else:
                    logging.error("Unknown link type " + link.type)
                    
                # Update link count
                crawler.total_links     = crawler.total_links + 1
                crawler.put()
        
class UpdateJobUrls(webapp.RequestHandler):
    """ Performs updates to job urls """
    
    def __init__(self):
        self.sites  = ['craigslist']
        
    def get(self):
        """ Update URL listings for craigslist"""
        _refresh_link_list()
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Job Listing Updated...')

def _refresh_link_list():
    """ Updates URL listings """
    baseurls    = []
            
    # Just get listing of cities in US
    isos    = ['us']
    
    # Internet engineering, software jobs, web design
    types       = ['eng','sof','web']
    
    for iso in isos:
        url     = 'http://geo.craigslist.org/iso/' + iso
        
        result  = urlfetch.fetch(url)
        
        if result.status_code == 200:
            soup    = BeautifulSoup(result.content)
            for link in soup.html.body.div.findAll('a'):
                
                baseurls.append(link['href'])
                                    
        # Build url list to crawl
        for url in baseurls:
            for type in types:
                if url.endswith('/'):
                    joburl  = url + 'search/jjj?query&catAbb=' + type + '&srchType=A&addOne=telecommuting&format=rss' 
                else:
                    joburl  = url + '/search/jjj?query&catAbb=' + type + '&srchType=A&addOne=telecommuting&format=rss'
                    
                link    = model.Link.all()
                link.filter("url =", joburl)
                
                results = link.fetch(1)
                
                if len(results) == 0:
                    logging.info("Adding job url" + joburl)
                    link    = model.Link(site           = "craigslist",
                                         type           = "rss",
                                         url            = joburl,
                                         crawl_count    = 0,
                                         hit_count      = 0,
                                         backoff        = 1,
                                         nextcrawl      = 0)
                    
                    link.put()        

def _get_links(crawlid):
    """ Get list of links to crawl for this crawlid """
    links   = model.Link.all()
    links.filter("nextcrawl <=", crawlid)
    links.order("nextcrawl")
    logging.info(links.count())
    
    return links

def _make_job_entry(record):
    """Create a job datastore entity from a dictionary of fields.
    """
    return model.Job(
        title       = record['title'],
        link        = record['link'],
        desc        = record['desc'],
        geo         = record['geo'],
        state_prov  = record['state_prov'],
        city        = record['city'],
        tag_info    = _add_tags(record.get('tag_info',None))
    )
    
def _add_tags(tag_list):
    """ Add new tags.  Ignore if tag already exists """
    list    = []
    
    date    = datetime.date.today()
    
    if tag_list is not None:
        for tag in tag_list:
            list.append(tag)
            
            tag_obj = model.Tag.get_by_key_name(tag)
            
            if tag_obj is None:
                tag_obj = model.Tag(key_name=tag)
                tag_obj.put()
            
            stats   = model.Stats.all()
            stats.filter("statname =", tag)
            stats.filter("date =", date)
            
            results = stats.fetch(1)
            
            if len(results) == 0:
                stats   = model.Stats(statname      = tag,
                                      occurrences    = 1)
                stats.put()
                
            else:
                stat    = results[0]
                stat.occurrences    = stat.occurrences + 1
                stat.put()
                
    return list
        
        
def _add_jobs(job_list):
    """ Store each Job in a sequence into the datastore.
     """
    # Sometimes duplicate links come in the same list
    ignore_links    = {}

    if (type(job_list) not in (tuple, list)):
        raise TypeError('Expected record sequence; not "%s"' %
                        type(job_list).__name__)
    
    added_jobs      = 0
    
    for job in job_list:          
        # Check if record exists first.  Ignore if already in datastore
        jobs        = model.Job.all()
        jobs.filter("link =",job.link)

        results     = jobs.fetch(1)
        
        if len(results) == 0:
            if not ignore_links.has_key(job.link):
                ignore_links[job.link]  = 'exists'
                
                # Only add jobs with tags
                if len(job.tag_info) != 0:
                    job.put()
                    added_jobs  += 1            
                    
    return added_jobs    

def application():
    """Instantiate a report application object."""

    return webapp.WSGIApplication(
        [('/update/jobs', UpdateJobProcess),
         ('/update/joburls', UpdateJobUrls)],
        debug=True)

def main():
    run_wsgi_app(application())

if __name__ == "__main__":
    main()