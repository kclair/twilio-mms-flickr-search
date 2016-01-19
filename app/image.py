import app_base

class Image(app_base.db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flickr_id = app_base.db.Column(app_base.db.String(30))
    image_url = app_base.db.Column(app_base.db.String(255))

    phone_number_id = db.Column(
        db.Integer, db.ForeignKey('phone_number.phone_number'))
    phone_number = db.relationship('PhoneNumber',
        backref=db.backref('phone_numbers', lazy='dynamic')) 

    def __init__(self, flickr_id, image_url, phone_number):
        self.flickr_id = flickr_id
        self.image_url = image_url
        self.phone_number = phone_number

