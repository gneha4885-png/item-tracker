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
    items = db.collection("items")\
              .where("user_id", "==", user_id)\
              .get()
    result = []
    for item in items:
        data = item.to_dict()
        data['id'] = item.id    # ← is this line there?
        result.append(data)
    return result

def find_item(user_id: str, query: str):
    """Get all items for a user to search through"""
    items = db.collection("items")\
              .where("user_id", "==", user_id)\
              .get()
    return [item.to_dict() for item in items]


def delete_item(item_id: str, user_id: str):
    try:
        doc_ref = db.collection('items').document(item_id)
        doc = doc_ref.get()
        if doc.exists and doc.to_dict().get('user_id') == user_id:
            doc_ref.delete()
            return True
        return False
    except Exception as e:
        print(f"Delete error: {e}")
        return False