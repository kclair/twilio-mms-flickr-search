import os
import sys
import urllib2
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from app.flickr_search import FlickrSearch
from app.twilio_mms import TwilioMms

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///:memory:')
db = SQLAlchemy(app)

class PhoneNumber(db.Model):
    phone_number = db.Column(db.String(30), primary_key=True)

    def __init__(self, phone_number):
        self.phone_number = phone_number

def lookup_number(number):
    phone_number = PhoneNumber.query.filter_by(phone_number=number).first()
    if not phone_number:
        phone_number = PhoneNumber(phone_number=number)
        db.session.add(phone_number)
        db.session.commit()
        return None
    return phone_number

@app.route('/')
def index():
    return ''

@app.route('/search_flickr')
def search_flickr():
    from_number = request.args.get('From', None)
    from_number = urllib2.unquote(from_number)
    number_exists = lookup_number(from_number)
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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
