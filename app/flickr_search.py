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

class FlickrSearch(object):
    '''A class for handling flickr searches'''

    def __init__(self, search_term):
        try:
            (self.search_term, self.option) = search_term.split(':')
        except ValueError:
            (self.search_term, self.option) = (search_term, None)

    @property
    def request_args(self):
        base_args = '&'.join([
            'api_key=3ec65cdbfb9d1c0e566c056fd2ae4bc6',
            'format=json',
            'method=flickr.photos.search',
            'content_type=1',
            'extras=license,description',
            'sort=relevance',
            'text={}'.format(urllib2.quote(self.search_term)),
            'nojsoncallback=1',
            'safe_search=1'
        ])
        if self.option == 'common':
            base_args.append('is_commons=true')
        return base_args

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
        flickr_url = '?'.join([
            'https://www.flickr.com/services/rest/',
            self.request_args
        ]) 
        response = urllib2.urlopen(flickr_url)
        try:
            data = json.load(response)
        except ValueError:
            return None
        photo = self.find_photo(data=data) 
        return (photo, self.construct_url_for_photo(photo))
