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

    
class StatHandler(BasePage):
    """ Handler for summary requests
    """

    def __init__(self):
        """ Create a new handler.
        """
        super(StatHandler, self).__init__()     

    def get(self, stat='', range=''):
        """ Handler for job information requests.
        """
        xaxis           = ''
        languages       = ''
        data            = ''
        colors          = ''
        graph_languages = ''
        
        stat_names      = {}
        statistics      = {}
        stat_dates      = []
        x_axis_dates    = []
        stat_array      = []
        
        color_array     = ['616D7E','4C787E','806D7E','4E387E','25383C','15317E',
                           '306EFF','3BB9FF','6960EC','7A5DC7','728FCE','F6358A',
                           '7D053F','E238EC','3B9C9C','348781','347235','EDE275']                
        lang            = []
        
        languages       = model.Languages.all()
        languages.order("display")        
        
        self.set_template('templates/jobstats.html')
        self.add_template_value('languages', languages)
        
        for l in languages:
            lang.append(l.display)
        
        stats   = model.Stats.all()
        
        if stat != 'all':
            if stat == 'cplus':
                statname = 'C++'
            elif stat == 'csharp':
                statname = 'C#'
            elif stat == 'objectivec':
                statname = 'Objective C'
            else:
                statname = stat
            
            stats.filter("statname =", statname)
            
            self.add_template_value('skill', statname.upper())
        else:
            self.add_template_value('skill', "ALL SKILLS")
            
        if range != 'all':
            today       = datetime.datetime.today()
            delta       = datetime.timedelta(days=int(range))
            days_ago    = today - delta
            
            stats.filter('date >=', days_ago)
            
            if range == '7':
                self.add_template_value('graph_time', 'PAST WEEK')
            elif range == '30':
                self.add_template_value('graph_time', 'PAST MONTH')
            elif range == '90':
                self.add_template_value('graph_time', 'PAST QUARTER')
            elif range == '180':
                self.add_template_value('graph_time', 'PAST HALF-YEAR')
            elif range == '360':
                self.add_template_value('graph_time', 'PAST YEAR')
            else:
                timerange   = "PAST " + range + " DAYS"
                self.add_template_value('graph_time', timerange)
        else:
            self.add_template_value('graph_time', 'ALL TIME')
        
        self.add_template_value('skillname', stat)    
        self.add_template_value('range', range)
        
        stats.order('date')
        stats.order('statname')
        
        for stat in stats:
            date_key    = str(stat.date)            
            
            if date_key not in statistics:
                stat_dates.append(date_key)
                x_axis_dates.append(stat.date.strftime("%d-%B"))
                statistics[date_key]   = {}
                
            if stat.statname not in stat_array:
                stat_array.append(stat.statname)
                if colors == '':
                    colors  = color_array[(len(stat_array) - 1)]
                else:
                    colors  = colors + "," + color_array[(len(stat_array) - 1)] 
                
            statistics[date_key][stat.statname]    = stat.occurrences
        
        chart_callback  = "http://chart.apis.google.com/chart?cht=lc&chs=450x300&chd=t:"
        
        for date in x_axis_dates:
            xaxis       = xaxis + "%7C" + date                    
        
        for name in stat_array:
            if name == 'C#':
                urlname = "C%23"
            elif name == 'C++':
                urlname = "C%2B%2B"
            elif name == 'Objective C':
                urlname = "Objective%20C"
            else:
                urlname = name
            
            if graph_languages == '':
                graph_languages = urlname
            else:
                graph_languages = graph_languages + "%7C" + urlname
                
            subdata = ''
            
            for date in stat_dates:
                if subdata == '':
                    if name not in statistics[date]:
                        subdata = "0"
                    else:
                        subdata = str(statistics[date][name])
                else:
                    if name not in statistics[date]:
                        subdata = subdata + ",0"
                    else:
                        subdata = subdata + "," + str(statistics[date][name])
                    
            if data == '':
                data    = subdata
            else:
                data    = data + "%7C" + subdata
        
        chart_callback  = chart_callback + "&chd=t:" + data
        chart_callback  = chart_callback + "&chdl=" + graph_languages
        chart_callback  = chart_callback + "&chco=" + colors
        
        # X,Y axis
        chart_callback  = chart_callback + "&chxt=x,y"
        chart_callback  = chart_callback + "&chxl=0:" + xaxis + "%7C1:%7C0%7C25%7C50%7C75%7C100%7C125%7C150%7C175%7C200%7C225%7C250%7C275%7C300%7C325%7C350%7C375%7C400%7C425%7C450%7C475%7C500"
                
        logging.info(chart_callback)
        self.add_template_value('stats', chart_callback)
        
        self.write_page()

def application():
    """Instantiate a report application object."""

    return webapp.WSGIApplication(
        [('/stats/(.*?)/(.*?)', StatHandler)],
        debug=True)

def main():
    run_wsgi_app(application())

if __name__ == "__main__":
    main()