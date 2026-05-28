import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os
import json

# Initialize Firebase
if not firebase_admin._apps:
    firebase_json = os.getenv("FIREBASE_CREDENTIALS")
    if firebase_json:
        # Running on Render — use environment variable
        cred_dict = json.loads(firebase_json)
        cred = credentials.Certificate(cred_dict)
    else:
        # Running locally — use key file
        cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()