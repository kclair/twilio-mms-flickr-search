import os
import sys
import urllib2
import json
import random
from flask import Flask, request, render_template
from twilio import twiml
from twilio.rest import TwilioRestClient
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///:memory:')
db = SQLAlchemy(app)

TW_SID = 'ACd6488e81463bb3c87c446a63cb563d05'
TW_TOKEN = '7ac4e33455f4d50db5f71bfe5009e923'
TWILIO_NUMBER = '+14253104023'

LICENSE_CODES = {
  '0': 'All Rights Reserved',
  '1': 'Attribution-NonCommercial-ShareAlike License (http://creativecommons.org/licenses/by-nc-sa/2.0/)',
  '2': 'Attribution-NonCommercial License (http://creativecommons.org/licenses/by-nc/2.0/)',
  '3': 'Attribution-NonCommercial-NoDerivs License (http://creativecommons.org/licenses/by-nc-nd/2.0/)',
  '4': 'Attribution License (http://creativecommons.org/licenses/by/2.0/)',
  '5': 'Attribution-ShareAlike License (http://creativecommons.org/licenses/by-sa/2.0/)',
  '6': 'Attribution-NoDerivs License (http://creativecommons.org/licenses/by-nd/2.0/)',
  '7': 'No known copyright restrictions (http://flickr.com/commons/usage/)',
  '8': 'United States Government Work (http://www.usa.gov/copyright.shtml)',
}

WELCOME_MESSAGE = '' \
    'Hello! Send any word or phrase (under 20 characters) ' \
    'to this number to receive a random photo from Flickr. '

class PhoneNumber(db.Model):
    phone_number = db.Column(db.String(30), unique=True)

    def __init__(self, phone_number):
        self.phone_number = phone_number

def welcome_message():
    pass

def twilio_auth():
    return TwilioRestClient(TW_SID, TW_TOKEN)

def flickr_args(search_term):
    return '&'.join([
        'api_key=3ec65cdbfb9d1c0e566c056fd2ae4bc6',
        'format=json',
        'method=flickr.photos.search',
        'content_type=1',
        'extras=license,description',
        'sort=relevance',
        'text={}'.format(urllib2.quote(search_term)),
        'nojsoncallback=1',
        'safe_search=1'
    ])

def find_photo(data, search_term):
    matching_photos = []
    if 'photos' not in data:
        return None
    if 'photo' not in data['photos']:
        return None
    for photo in data['photos']['photo']:
        match_strings = [
            photo['title'],
            photo['description']['_content']
        ]
        for s in match_strings:
            if search_term.lower() in s.lower():
                matching_photos.append(photo)
                continue
    try:
        return random.choice(matching_photos)
    except IndexError:
        return None

def construct_url_for_photo(photo):
    if not photo:
        return None
    return 'https://farm{farm}.staticflickr.com/{server}/{id}_{secret}.jpg'.format(
        **photo)

def search_flickr_for_term(search_term):
    flickr_url = '?'.join([
        'https://www.flickr.com/services/rest/',
        flickr_args(search_term)
    ]) 
    response = urllib2.urlopen(flickr_url)
    try:
        data = json.load(response)
    except ValueError:
        return None
    photo = find_photo(data=data,search_term=search_term) 
    return (photo, construct_url_for_photo(photo))

def return_error(error_msg):
    r = twiml.Response()
    r.message(error_msg)
    return str(r)

def send_mms(to_number,image_url, photo):
    to_number = urllib2.unquote(to_number)
    client = twilio_auth()
    try:
        license_text = LICENSE_CODES[photo['license']]
    except KeyError:
        license_text = 'Unknown.'
    client.messages.create(
        body='Your search results! Copyright: {}'.format(license_text),
        to=to_number,
        from_=TWILIO_NUMBER,
        media_url=image_url)

@app.route('/')
def index():
    return 'Hello, World'

@app.route('/search_flickr')
def search_flickr():
    from_number = request.args.get('From', None)
    search_term = request.args.get('Body', None)
    if not search_term:
       return return_error('search term not found')
    search_term = search_term.replace('+', ' ') 
    (photo, image_url) = search_flickr_for_term(search_term) 
    if not image_url:
       return return_error('no matching image found.')
    send_mms(to_number=from_number, image_url=image_url, photo=photo)
    return ''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
