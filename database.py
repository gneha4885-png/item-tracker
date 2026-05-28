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

def save_item(user_id: str, item_name: str, location: str, room: str, raw_text: str):
    """Save an item location to Firestore"""
    doc_ref = db.collection("items").add({
        "user_id": user_id,
        "item_name": item_name,
        "location": location,
        "room": room,
        "raw_text": raw_text,
        "timestamp": datetime.now().isoformat()
    })
    return doc_ref

def get_all_items(user_id: str):
    """Get all items for a specific user"""
    items = db.collection("items")\
              .where("user_id", "==", user_id)\
              .get()
    return [item.to_dict() for item in items]

def find_item(user_id: str, query: str):
    """Get all items for a user to search through"""
    items = db.collection("items")\
              .where("user_id", "==", user_id)\
              .get()
    return [item.to_dict() for item in items]