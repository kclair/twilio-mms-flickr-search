import app_base

class PhoneNumber(app_base.db.Model):
    id = app_base.db.Column(app_base.db.Integer, primary_key=True)   
    phone_number = app_base.db.Column(app_base.db.String(30), unique=True)
    access_code = app_base.db.Column(app_base.db.String(6))
    access_code_ts = app_base.db.Column(app_base.db.DateTime)

    def __init__(self, phone_number):
        self.phone_number = phone_number

def lookup_number(number):
    phone_number = PhoneNumber.query.filter_by(phone_number=number).first()
    if not phone_number:
        phone_number = PhoneNumber(phone_number=number)
        app_base.db.session.add(phone_number)
        app_base.db.session.commit()
        return None
    return phone_number

