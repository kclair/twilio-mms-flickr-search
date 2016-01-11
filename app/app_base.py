import os
import urllib2
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flickr_search import FlickrSearch
from twilio_mms import TwilioMms

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///:memory:')
db = SQLAlchemy(app)

import phone_number
def flickr_search():
    from_number = request.args.get('From', None)
    from_number = urllib2.unquote(from_number)
    number_exists = phone_number.lookup_number(from_number)
    twilio_mms = TwilioMms()
    if not number_exists:
        return twilio_mms.twiml_message(WELCOME_MESSAGE)
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
