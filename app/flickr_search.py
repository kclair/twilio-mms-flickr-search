import os
import sys
import urllib2
import json
import random

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

COMMON_LICENSE_CODES = [ '1', '2', '3', '4', '5', '6', '7' ]

FLICKR_API_KEY = os.environ.get('FLICKR_API_KEY', None)

class FlickrBase(object):
    '''A base class for flickr api calls'''

    def open_url(self):
        flickr_url = '?'.join([
            'https://www.flickr.com/services/rest/',
            self.request_args
        ]) 
        response = urllib2.urlopen(flickr_url)
        try:
            return json.load(response)
        except ValueError:
            return None

class FlickrPhotoInfo(FlickrBase):
    '''A class for getting info about a flickr photo'''

    def __init__(self, flickr_id):
        self.flickr_id = flickr_id

    @property
    def request_args(self):
        return '&'.join([
            'api_key={}'.format(FLICKR_API_KEY),
            'photo_id={}'.format(self.flickr_id),
        ]) 

class FlickrSearch(FlickrBase):
    '''A class for handling flickr searches'''

    def __init__(self, search_term):
        try:
            (self.search_term, self.option) = search_term.split(':')
        except ValueError:
            (self.search_term, self.option) = (search_term, None)

    @property
    def request_args(self):
        base_args = [
            'api_key={}'.format(FLICKR_API_KEY),
            'format=json',
            'method=flickr.photos.search',
            'content_type=1',
            'extras=license,description',
            'sort=relevance',
            'text={}'.format(urllib2.quote(self.search_term)),
            'nojsoncallback=1',
            'safe_search=1'
        ]
        if self.option == 'common':
            base_args.append('license=%s' % ','.join(COMMON_LICENSE_CODES))
        return '&'.join(base_args)

    def find_photo(self, data):
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
                if self.search_term.lower() in s.lower():
                    matching_photos.append(photo)
                    continue
        try:
            return random.choice(matching_photos)
        except IndexError:
            return None

    def construct_url_for_photo(self, photo):
        if not photo:
            return None
        return 'https://farm{farm}.staticflickr.com/{server}/{id}_{secret}.jpg'.format(
            **photo)

    def search(self):
        data = self.open_url() 
        if not data:
            return (None, None)
        photo = self.find_photo(data=data) 
        return (photo, self.construct_url_for_photo(photo))
