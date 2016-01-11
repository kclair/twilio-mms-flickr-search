import app_base

class PhoneNumber(app_base.db.Model):
    phone_number = app_base.db.Column(app_base.db.String(30), primary_key=True)

    def __init__(self, phone_number):
        self.phone_number = phone_number

def lookup_number(number):
    phone_number = PhoneNumber.query.filter_by(phone_number=number).first()
    if not phone_number:
        phone_number = PhoneNumber(phone_number=number)
        db.session.add(phone_number)
        db.session.commit()
        return None
    return phone_number

