import os
import sys
import urllib2
import base64
import json
from twilio import twiml
from twilio.rest import TwilioRestClient
from flickr_search import LICENSE_CODES

TW_SID = os.environ.get('TW_SID')
TW_TOKEN = os.environ.get('TW_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER') 

class TwilioMms(object):

    def __init__(self):
        self.client = TwilioRestClient(TW_SID, TW_TOKEN)

    def get_sent_media(self, to_number):
        image_sets = []
        messages = self.client.messages.list(to=to_number)
        messages_with_media = [ m for m in messages
                                if int(m.num_media) > 0 ]
        media_uris = [ 
            str(self.get_message_uri(m)) for m in messages_with_media ]
        for i in xrange(0, len(media_uris), 3):
            image_sets.append(
                ['https://api.twilio.com{}'.format(uri) for uri in media_uris[i:i+3] ])
        return image_sets
        
    def get_message_uri(self, message):
        media_json_url = message.subresource_uris['media']
        media_json_url = 'https://api.twilio.com' + media_json_url
        request = urllib2.Request(media_json_url)
        authstring = '{}:{}'.format(TW_SID, TW_TOKEN)
        base64auth = base64.encodestring(authstring).replace('\n', '')
        request.add_header('Authorization', 'Basic {}'.format(base64auth))    
        response = urllib2.urlopen(request)
        media_json = json.load(response) 
        return media_json['media_list'][0]['uri'].replace('.json', '')

    def twiml_message(self, msg):
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

    def send_sms(self, to_number, msg):
        self.client.messages.create(
            body=msg,
            to=to_number,
            from_=TWILIO_NUMBER)
