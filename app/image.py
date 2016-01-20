import app_base
import phone_number as pn
from flickr_search import FlickrPhoto

class Image(app_base.db.Model):
    id = app_base.db.Column(app_base.db.Integer, primary_key=True)
    flickr_id = app_base.db.Column(app_base.db.String(30))
    image_url = app_base.db.Column(app_base.db.String(255))
    flickr_photopage = app_base.db.Column(app_base.db.String(255))

    phone_number_id = app_base.db.Column(
        app_base.db.Integer, app_base.db.ForeignKey('phone_number.id'))
    phone_number = app_base.db.relationship('PhoneNumber',
        backref=app_base.db.backref('phone_numbers', lazy='dynamic')) 

    def __init__(self, flickr_id, image_url, flickr_photopage, phone_number):
        self.flickr_id = flickr_id
        self.image_url = image_url
        self.flickr_photopage = flickr_photopage
        self.phone_number = phone_number
    
    def __repr__(self):
        return '<Image %r, %r, %r>' % (
            self.flickr_id, self.image_url, self.phone_number)

def store_image(photo, image_url, from_number):
    phone_number = pn.PhoneNumber.query.filter_by(
        phone_number=from_number).first() 
    photo_data = FlickrPhoto(photo['id'])
    img = Image(photo['id'], image_url, photo_data.photopage, phone_number)
    app_base.db.session.add(img)
    app_base.db.session.commit()

def get_images_by_phone_number(number):
    phone_number = pn.lookup_number(number)
    images = Image.query.filter_by(phone_number=phone_number).all()
    image_sets = []
    for i in xrange(0, len(images), 3):
        image_sets.append(
            [ image for image in images[i:i+3] ] )
    return image_sets
