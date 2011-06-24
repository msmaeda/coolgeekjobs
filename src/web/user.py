#!python2.5

"""Script for managing user account management
"""

__author__ = 'Matt Maeda <msmaeda@gmail.com>'

import datetime
import logging
import cgi
import random
import string
import hashlib
from base64 import b64decode, b64encode

from web.base import BasePage
from google.appengine.ext import webapp
from google.appengine.api import mail
from google.appengine.ext.webapp.util import run_wsgi_app
from django.utils import simplejson

from app.model import User

STATUS_OK       = 'ok'
STATUS_ERROR    = 'err'

B64SALT = "kDPdraeewad0Py2QwEdJYtUX9cJABdfe3g=="
B64HASH = "OJF6H4KdxFreas34arLgLu+oTDNFodCEfMA="
BINSALT = b64decode(B64SALT)

#from google.appengine.api import memcache
#TODO: Add this in for queries to speed things up"""

class UserHandler(BasePage):
    """ Handler for user related requests"""

    def __init__(self):
        """ Create a new handler.
        """
        super(UserHandler, self).__init__()
        
    def get(self, action='', account_key='', arg1=''):
        """ Serve up user related pages."""
        if action == 'signup':
            self.set_template('templates/account/signup.html')
            
        #elif action == 'complete':
            
        elif action == 'confirm':
            self.set_template('templates/account/signupconfirm.html')
            user    = User.all()
            user.filter("conf_key =", account_key)
            user.get()
            
            if user is None:
                error   = "Could not locate your account information."
                self.error_message(error)
                self.add_template_value('title', "Cool Geek Jobs - Ooops!!!")
            else:
                u   = user[0]
                logging.info(u.key())
                self.add_template_value('title', "Cool Geek Jobs - Your Account is Activated")
                self.add_template_value('username', u.username.upper())
                self.add_template_value('firstname', u.first.upper())
                u.email_conf = True
                u.put()
        elif action == 'signin':
            self.set_template('templates/account/signin.html')
        elif action == 'edit':
            session_id  = cgi.escape(self.request.get('session_id'))
            user        = _check_logged_in(session_id)
            
            if user is None:
                self.set_template('templates/account/signin.html')
                self.error_message("SESSION EXPIRED")
            else:
                self.set_template('templates/account/useraccount.html')
                self.add_template_value("session_id", user.session)
            
        else:
            self.set_template('templates/account/signup.html')
            
        self.write_page()
        


class UserSubmitHandler(BasePage):
    def __init__(self):
        """ Create a new handler.
        """
        super(UserSubmitHandler, self).__init__()
            
    def post(self, action="" , arg=""):
        """Handle posts"""
        if action == 'new':
            username    = cgi.escape(self.request.get('username'))
            password    = cgi.escape(self.request.get('password'))
            email       = cgi.escape(self.request.get('email'))
            first       = cgi.escape(self.request.get('firstname'))
            last        = cgi.escape(self.request.get('lastname'))
            plan        = cgi.escape(self.request.get('plan'))
            
            m1 = hashlib.sha1()
            
            # Pass in salt
            m1.update(BINSALT)
            m1.update(password)
            encrypt = b64encode(m1.digest())            
            logging.info(encrypt)
            
            conf_key    = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(20))
            
            user    = User(username   = username,
                           password   = encrypt,
                           email      = email,
                           conf_key   = conf_key, 
                           first      = first,
                           last       = last,
                           plan_type  = plan,
                           plan_date  = datetime.datetime.now())
            user.put()
            
            confirm_url     = "http://www.coolgeekjobs.com/account/confirm/" + conf_key
            sender_address  = "Cool Geek Jobs Alerts <msmaeda@gmail.com>"
            subject         = "Please confirm your registration"
            body            = """
Thank you for creating an account!  Please confirm your email address by
clicking on the link below:

%s
""" % confirm_url

            mail.send_mail(sender_address, email, subject, body)
            
            self.set_template('templates/account/signuppending.html')
            self.add_template_value('username', username.upper())
            self.add_template_value('email', email.upper())
            self.add_template_value('firstname', first.upper())
            
            if last != '':
                self.add_template_value('lastname', last.upper())
            
            planname    = ''
            planfreq    = ''
            
            if plan == 'weekly':
                planname    = 'ONLY IF THE OPPORTUNITY IS RIGHT'
                planfreq    = 'weekly'
            elif plan == 'daily':
                planname    = 'JUST TESTING THE WATERS'
                planfreq    = 'once a day'
            elif plan == 'hourly':
                planname    = 'READY TO MAKE THE LEAP'
                planfreq    = 'hourly'
            else:
                planname    = 'GET ME OUTTA HERE!!!'
                planfreq    = 'immediately'
                
            self.add_template_value('planname', planname)
            self.add_template_value('planfreq', planfreq)
            
        elif action == 'login':
            username    = cgi.escape(self.request.get('username'))
            password    = cgi.escape(self.request.get('password'))            
            
            user    = User.all()
            user.filter("username =", username)
            user.get()
            
            if user.count() == 0:
                self.set_template('templates/account/signin.html')
                self.error_message("USERNAME AND/OR PASSWORD INCORRECT")
            
            else:
                u   = user[0]

                m1 = hashlib.sha1()
                
                # Pass in salt
                m1.update(BINSALT)
                m1.update(password)
                encrypt = b64encode(m1.digest())
                
                if encrypt != u.password:
                    self.set_template('templates/account/signin.html')
                    self.error_message("USERNAME AND/OR PASSWORD INCORRECT")
                    
                else:
                    session_id  = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(20))
                    greeting    = ''    
                    
                    # Save login time
                    u.last_login    = datetime.datetime.now()
                    u.session       = session_id
                    u.put()
                        
                    if u.first is not None:
                        greeting    = u.first.upper()
                    else:
                        greeting    = u.username.upper()
                    
                    self.set_template('templates/account/useraccount.html')
                    self.info_message("WELCOME BACK, " + greeting)
                    self.add_template_value('session_id', session_id)
                    self.add_template_value('links', _logged_in_menu(u.key().id()))
                
        self.write_page()    
        
class UserJsonHandler(BasePage):
    """ Handler for json download for data transfer off of GAE
    """

    def __init__(self):
        """ Create a new handler.
        """
        super(UserJsonHandler, self).__init__()
        self._json_decoder = simplejson.JSONDecoder()
        self._encode_response = simplejson.JSONEncoder().encode

    def get(self, action = '', argument=''):
        """ Validate if username is available"""
        res = dict(status=STATUS_OK)
        
        if action == 'validateusername':
            logging.info("Query for username" + argument)
            
            user    = User.all()
            user.filter("username =", argument)
        
            res['available']    = 'No'
        
            if user.count() == 0:
                res['available'] = 'Yes'
            
            if argument == 'test':
                res['available'] = 'No'
        
        elif action == 'validateemail':
            email   = argument.replace("%40","@")
            
            logging.info("Query for email" + email)
            
            user    = User.all()
            user.filter("email =", email)
        
            res['available']    = 'No'
        
            if user.count() == 0:
                res['available'] = 'Yes'
                            
        self.response.headers['content-type'] = 'text/plain'
        self.response.out.truncate(0)
        self.response.out.write(self._encode_response(res))
        self.response.out.write('\n')

def _check_logged_in(session_id):    
    user    = User.all().filter("session =", session_id).get()
    
    if user is None:
        return None
    else:
        return user[0]
                
def _logged_in_menu(userid):
    links   = {""                                       : "Home",
               "jobstats/all/30"                        : "Job Stats",
               "account/tellafriend/" + str(userid)     : "Tell A Friend",
               "account/edit/" + str(userid)            : "Settings"}
    
    return links
                    
def application():
    """Instantiate a report application object."""

    return webapp.WSGIApplication(
        [('/account/json/(.*)/(.*)', UserJsonHandler),
         ('/account/submit/(.*)/(.*)', UserSubmitHandler),
         ('/account/submit/(.*)', UserSubmitHandler),
         ('/account/login', UserHandler),
         ('/account/upgrade/(.*)/(.*)', UserHandler),
         ('/account/(.*)/(.*)', UserHandler),
         ('/account/(.*)', UserHandler)],
        debug=True)

def main():
    run_wsgi_app(application())

if __name__ == "__main__":
    main()