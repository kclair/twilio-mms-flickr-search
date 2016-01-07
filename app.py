import os
import sys
from flask import Flask, request, render_template
from twilio import twiml
from twilio.rest import TwilioRestClient

app = Flask(__name__)
app.debug = True

TW_SID = 'ACd6488e81463bb3c87c446a63cb563d05'
TW_TOKEN = '7ac4e33455f4d50db5f71bfe5009e923'

def twilio_auth():
    return TwilioRestClient(TW_SID, TW_TOKEN)

@app.route('/')
def index():
    return 'Hello, World'

@app.route('/search_flickr')
def search_flickr():
    r = twiml.Response()
    r.message('Thanks!')
    return str(r)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
