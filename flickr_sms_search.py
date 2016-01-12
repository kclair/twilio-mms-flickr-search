import os
import sys
import urllib2
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from app.app_base import app, db, AppBase 

@app.route('/')
def index():
    return ''

@app.route('/history')
def get_history():
    app_base = AppBase()
    images = app_base.get_images()
    try:
        return render_template('history.html', images=images) 
    except Exception as e:
        return 'Error! {}'.format(e.__class__.__name__)

@app.route('/search_flickr')
def search_flickr():
    app_base = AppBase()
    return app_base.flickr_search()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
