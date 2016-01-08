import os
import sys
from flask import Flask, request, render_template
from twilio import twiml
from twilio.rest import TwilioRestClient
from flask_sqlalchemy import SQLAlchemy
from app.flickr_search import FlickrSearch, LICENSE_CODES

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///:memory:')
db = SQLAlchemy(app)

TW_SID = os.environ.get('TW_SID')
TW_TOKEN = os.environ.get('TW_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER') 

WELCOME_MESSAGE = '' \
    'Hello! Send any word or phrase (under 20 characters) ' \
    'to this number to receive a random photo from Flickr. '

class PhoneNumber(db.Model):
    phone_number = db.Column(db.String(30), primary_key=True)

    def __init__(self, phone_number):
        self.phone_number = phone_number

def welcome_message():
    pass

def twilio_auth():
    return TwilioRestClient(TW_SID, TW_TOKEN)

def lookup_number(number):
    phone_number = PhoneNumber.query.filter_by(phone_number=number).first()
    if not phone_number:
        phone_number = PhoneNumber(phone_number=number)
        db.session.add(phone_number)
        db.session.commit()
        return None
    return phone_number

def return_error(error_msg):
    r = twiml.Response()
    r.message(error_msg)
    return str(r)

def send_mms(to_number,image_url, photo):
    client = twilio_auth()
    try:
        license_text = u'\N{COPYRIGHT SIGN} %s' % LICENSE_CODES[photo['license']]
    except KeyError:
        license_text = 'Unknown.'
    client.messages.create(
        body=u'Your search results! {}'.format(license_text),
        to=to_number,
        from_=TWILIO_NUMBER,
        media_url=image_url)

@app.route('/')
def index():
    return 'Hello, World'

@app.route('/search_flickr')
def search_flickr():
    from_number = request.args.get('From', None)
    from_number = urllib2.unquote(from_number)
    number_exists = lookup_number(from_number)
    if not number_exists:
        return return_error(WELCOME_MESSAGE)
    search_term = request.args.get('Body', None)
    if not search_term:
       return return_error('search term not found. %s' % WELCOME_MESSAGE)
    search_term = search_term.replace('+', ' ') 
    f_search = FlickrSearch(search_term)
    (photo, image_url) = f_search.search() 
    if not image_url:
       return return_error('no matching image found.')
    send_mms(to_number=from_number, image_url=image_url, photo=photo)
    return ''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
