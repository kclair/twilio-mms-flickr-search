import os
import sys
import urllib2
import json
import random
from flask import Flask, request, render_template
from twilio import twiml
from twilio.rest import TwilioRestClient

app = Flask(__name__)
app.debug = True

TW_SID = 'ACd6488e81463bb3c87c446a63cb563d05'
TW_TOKEN = '7ac4e33455f4d50db5f71bfe5009e923'

def twilio_auth():
    return TwilioRestClient(TW_SID, TW_TOKEN)

def flickr_args(search_term):
    return '&'.join([
        'api_key=3ec65cdbfb9d1c0e566c056fd2ae4bc6',
        'format=json',
        'method=flickr.photos.search',
        'content_type=1',
        'extras=original_format,description',
        'sort=relevance',
        'text={}'.format(search_term),
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
    data = json.load(response)
    photo = find_photo(data=data,search_term=search_term) 
    return construct_url_for_photo(photo)

def return_error(error_msg):
    r = twiml.Response()
    r.message(error_msg)
    return str(r)

def send_mms(to_number,image_url):
    to_number = urllib2.unquote(to_number)
    client = twilio_auth()
    client.messages.create(
        body='Your search results!',
        to=to_number,
        from_='+14253104023',
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
    image_url = search_flickr_for_term(search_term) 
    if not image_url:
       return return_error('no matching image found.')
    send_mms(to_number=from_number,image_url=image_url)
    return ''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
