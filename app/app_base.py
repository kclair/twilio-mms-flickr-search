import os
import urllib2
import random
import string
from flask import Flask, request, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from flickr_search import FlickrSearch
from twilio_mms import TwilioMms
from responses import WELCOME_MESSAGE, HELP_MESSAGE, FORGOT_NUMBER_MESSAGE

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///:memory:')
db = SQLAlchemy(app)

import phone_number
import image

class AppBase(object):

    def __init__(self):
        from_number = request.form['From']
        self.from_number = urllib2.unquote(from_number)
        try:
            search_term = request.form.get('Body', None)
            self.search_term = search_term.replace('+', ' ') 
        except Exception as e:
            self.search_term = None
        self.twilio_mms = TwilioMms()

    def generate_access_code(self):
        number = phone_number.lookup_number(self.from_number)
        if not number:
            return False
        access_code = ''.join(
            random.choice(string.digits) for _ in range(6))
        number.update_access_code(access_code)
        return access_code

    def send_access_code(self):
        access_code = self.generate_access_code()
        if not access_code:
            return False
        self.twilio_mms.send_sms(self.from_number, 
            'Your access code: {}'.format(access_code))
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

    def check_commands(self):
        if 'help me' in self.search_term.lower():
            return HELP_MESSAGE 
        if 'forget me' in self.search_term.lower():
            image.delete_images_for_number(self.from_number)
            phone_number.delete_number(self.from_number)
            return FORGOT_NUMBER_MESSAGE
        if 'history' in self.search_term.lower():
            access_code = self.generate_access_code()
            if not access_code:
                # return link to index page to generate a new access code
                return 'Could not generate an access code'
            return 'Go to {} and enter your phone number and access code {}'.format(
                url_for('get_history', _external=True), access_code)

    def parse_options(self):
        return_msg = None
        return_msg = self.check_new_number()
        if not return_msg:
            return_msg = self.check_commands()
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
        #return self.twilio_mms.get_sent_media(self.from_number)
        return image.get_images_by_phone_number(self.from_number)
