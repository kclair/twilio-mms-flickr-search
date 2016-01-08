import os
import sys
import urllib2
from twilio import twiml
from twilio.rest import TwilioRestClient
from flickr_search import LICENSE_CODES

TW_SID = os.environ.get('TW_SID')
TW_TOKEN = os.environ.get('TW_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER') 

WELCOME_MESSAGE = '' \
    'Hello! Send any word or phrase (under 20 characters) ' \
    'to this number to receive a random photo from Flickr. '

class TwilioMms(object):

    def __init__(self):
        self.client = TwilioRestClient(TW_SID, TW_TOKEN)

    def twiml_message(msg):
        r = twiml.Response()
        r.message(msg)
        return str(r)

    def send_mms(self, to_number, image_url, photo):
        try:
            license_text = u'\N{COPYRIGHT SIGN} %s' % LICENSE_CODES[photo['license']]
        except KeyError:
            license_text = 'Unknown.'
        self.client.messages.create(
            body=u'Your search results! {}'.format(license_text),
            to=to_number,
            from_=TWILIO_NUMBER,
            media_url=image_url)
