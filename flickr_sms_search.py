import os
import sys
import urllib2
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from app.flickr_search import FlickrSearch
from app.twilio_mms import TwilioMms
from app.app_base import app, db, flickr_search

@app.route('/')
def index():
    return ''

@app.route('/search_flickr')
def search_flickr():
    flickr_search()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
