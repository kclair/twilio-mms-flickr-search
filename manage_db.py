import os
import sys

from app import db

if sys.argv[1] == 'create':
    db.create_all()
elif sys.argv[1] == 'drop':
    db.drop_all()
