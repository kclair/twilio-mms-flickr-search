import os
import sys
import urllib2
import traceback
from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from app.app_base import app, db, AppBase 

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_access_code', methods=['POST'])
def send_access_code():
    app_base = AppBase()
    success = app_base.send_access_code()
    return render_template('access.html', success=True)

@app.route('/enter_access_code')
def enter_access_code():
    return render_template('access.html', success=True)

@app.route('/history', methods=['POST'])
def get_history():
    app_base = AppBase()
    success = app_base.check_access_code()
    if not success:
        return render_template('access.html', success=False)
    images = app_base.get_images()
    try:
        return render_template('history.html', images=images) 
    except Exception as e:
        return '<br>'.join(['Error! {}'.format(e.__class__.__name__),
                            traceback.format_exc() ])

@app.route('/search_flickr', methods=['POST'])
def search_flickr():
    app_base = AppBase()
    return app_base.flickr_search()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
