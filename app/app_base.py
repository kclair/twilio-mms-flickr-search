import os
import urllib2
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flickr_search import FlickrSearch
from twilio_mms import TwilioMms
from responses import WELCOME_MESSAGE, HELP_MESSAGE

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///:memory:')
db = SQLAlchemy(app)

import phone_number

class AppBase(object):

    def __init__(self):
        from_number = request.args.get('From', None)
        self.from_number = urllib2.unquote(from_number)
        search_term = request.args.get('Body', None)
        self.search_term = search_term.replace('+', ' ') 
        self.twilio_mms = TwilioMms()

    def check_new_number(self):
        number_exists = phone_number.lookup_number(self.from_number)
        if not number_exists:
            return WELCOME_MESSAGE
        return None

    def check_help(self):
        if 'help me' in self.search_term.lower():
            return HELP_MESSAGE 

    def parse_options(self):
        return_msg = None
        return_msg = self.check_new_number()
        if not return_msg:
            return_msg = self.check_help()
        return return_msg
    
    def flickr_search(self):
        return_msg = self.parse_options()
        if return_msg:
            return self.twilio_mms.twiml_message(return_msg)
        if not self.search_term:
            return self.twilio_mms.twiml_message('search term not found. %s' % WELCOME_MESSAGE)
        f_search = FlickrSearch(self.search_term)
        (photo, image_url) = f_search.search() 
        if not image_url:
           return self.twilio_mms.twiml_message('no matching image found.')
        self.twilio_mms.send_mms(to_number=from_number, image_url=image_url, photo=photo)
        return ''
