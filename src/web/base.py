#!python2.5

"""Base class for all webapp handlers
"""
__author__ = 'Matt Maeda <msmaeda@gmail.com>'

import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

class BasePage(webapp.RequestHandler):
    """ Base class for all webapp handlers
    """

    template_full_path      = ''
    template_values         = {}

    def __init__(self):
        """ Create a new handler.
        """
        super(webapp.RequestHandler, self).__init__()

    def set_template(self, full_path):
        """Sets template used when printing out page
                * full_path string path to template

                (typically found in templates directory
                e.g. 'templates/base.html')
        """
        self.template_full_path     = os.path.join(os.path.dirname(__file__),
                                                   full_path)

    def add_template_value(self, k, v):
        """ Set template value
            * k template variable
            * v template variable value
        """
        self.template_values[k]     = v

    def error_message(self, error_message):
        """ Sets page error message.
            * error_message string
        """
        self.add_template_value('error_message', error_message)

    def write_page(self):
        """ Prints out template
            If template is not set, prints out base template
            with an error message
        """
        # Set default template values used in all templates
        _set_default_template_values(self)

        # In case template is not set
        if self.template_full_path == '':
            self.template_full_path = os.path.join(os.path.dirname(__file__),
                                                   'templates/base.html')
            self.add_template_value('error_message', 'Template not set.')

        self.response.out.write(template.render(self.template_full_path,
                                                self.template_values,
                                                True))

def _get_greeting(self):
    """ Gets user information and if not logged in, redirects user to login.
        Technically, the redirect to login should not occur.  This is
        already handled in app.yaml
    """
    user            = users.get_current_user()

    if user:
        return ("Welcome, %s (<a href=\"%s\">sign out</a>)" %
                (user.nickname(), users.create_logout_url("/")))
    #TODO: Add login/signin option
        
    #else:
    #    self.redirect(users.create_login_url(self.request.uri))

def _menu_links():
    """ Maintain report menu list here
    """
    
    return {""              : "HOME",}

def _set_default_template_values(self):
    """ Set default template values
    """
    self.template_values.update({'logout_url'   : _get_greeting(self)})
    self.template_values.update({'links'        : _menu_links()})
    self.template_values.update({'message'      : ''})
    self.template_values.update({'error_message': ''})
