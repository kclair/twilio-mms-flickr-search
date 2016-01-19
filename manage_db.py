import os
import sys

from app.app_base import db
from app.phone_number import PhoneNumber
from app.image import Image

if sys.argv[1] == 'create':
    db.create_all()
elif sys.argv[1] == 'drop':
    db.drop_all()
elif sys.argv[1] == 'show':
    print PhoneNumber.query.all()
    print Image.query.all()
