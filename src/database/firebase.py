import firebase_admin
from firebase_admin import db
import json

def init() -> db:
    if firebase_admin._apps:
        return db
    with open('config/config.json', 'r') as f:
        config = json.load(f)

    cred_obj = firebase_admin.credentials.Certificate('config/firebase.json')
    firebase_admin.initialize_app(cred_obj, {'databaseURL': config['firebase']})

    return db
