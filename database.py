import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Initialize Firebase (only once)
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)

# Get database connection
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