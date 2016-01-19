import os
import urllib2
import random
import string
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
import image

class AppBase(object):

    def __init__(self):
        from_number = request.form.get('phoneNumber', None)
        self.from_number = urllib2.unquote(from_number)
        try:
            search_term = request.args.get('Body', None)
            self.search_term = search_term.replace('+', ' ') 
        except Exception as e:
            self.search_term = None
        self.twilio_mms = TwilioMms()

    def send_access_code(self):
        number = phone_number.lookup_number(self.from_number)
        if not number:
            return False
        access_code = ''.join(
            random.choice(string.digits) for _ in range(6))
        number.update_access_code(access_code)
        return True

    def check_access_code(self):
        access_code = request.form['accessCode']
        number = phone_number.lookup_number(self.from_number)
        if access_code != number.access_code:
            return False
        return True

    def check_new_number(self):
        number_exists = phone_number.lookup_and_create_number(self.from_number)
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
        image.store_image(photo, image_url, self.from_number)
        self.twilio_mms.send_mms(to_number=self.from_number, image_url=image_url, photo=photo)
        return ''

    def get_images(self):
        return self.twilio_mms.get_sent_media(self.from_number)
