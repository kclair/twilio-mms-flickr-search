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

def check_new_number():
    number_exists = phone_number.lookup_number(from_number)
    if not number_exists:
        return WELCOME_MESSAGE
    return None

def check_help():
    search_term = request.args.get('Body', None)
    if 'help me' in search_term.lower():
        return HELP_MESSAGE 

def parse_options():
    from_number = request.args.get('From', None)
    from_number = urllib2.unquote(from_number)
    return_msg = None
    return_msg = check_new_number()
    if not return_msg:
        return_msg = check_help()
    return return_msg
    
def flickr_search():
    twilio_mms = TwilioMms()
    return_msg = parse_options()
    if return_msg:
        return twilio_mms.twiml_message(return_msg)
    search_term = request.args.get('Body', None)
    if not search_term:
       return twilio_mms.twiml_message('search term not found. %s' % WELCOME_MESSAGE)
    search_term = search_term.replace('+', ' ') 
    f_search = FlickrSearch(search_term)
    (photo, image_url) = f_search.search() 
    if not image_url:
       return twilio_mms.twiml_message('no matching image found.')
    twilio_mms.send_mms(to_number=from_number, image_url=image_url, photo=photo)
    return ''
