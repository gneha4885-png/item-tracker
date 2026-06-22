import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
import base64
import uuid
import firebase_admin.storage
from datetime import datetime, timezone
from firebase_admin import messaging as fcm_messaging

# Initialize Firebase
if not firebase_admin._apps:
    firebase_json = os.getenv("FIREBASE_CREDENTIALS")
    if firebase_json:
        cred_dict = json.loads(firebase_json)
        cred = credentials.Certificate(cred_dict)
    else:
        cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred, {
    'storageBucket': 'item-tracker-71e9c.firebasestorage.app'
})

db = firestore.client()

# ── Push notification sender ────────────────────────────────────
def send_push_notification(fcm_token: str, title: str, body: str):
    """Send a push notification via FCM to a specific device token."""
    try:
        message = fcm_messaging.Message(
            notification=fcm_messaging.Notification(
                title=title,
                body=body,
            ),
            token=fcm_token,
            webpush=fcm_messaging.WebpushConfig(
                notification=fcm_messaging.WebpushNotification(
                    icon="/logo192.png",
                ),
                fcm_options=fcm_messaging.WebpushFCMOptions(link="/log"),
            ),
        )
        response = fcm_messaging.send(message)
        return response
    except Exception as e:
        print(f"Push notification error: {e}")
        return None


# ── UPDATED save_item function ──────────────────────────────────
def save_item(user_id: str, item_name: str, location: str, 
              room: str, raw_text: str, photo_url: str = '', 
              reminder_time: str = '', is_medicine: bool = False,
              reminder_times: list = None, repeat_type: str = ''):
    
    if reminder_times is None:
        reminder_times = []
    
    doc_ref = db.collection("items").add({
        "user_id": user_id,
        "item_name": item_name,
        "location": location,
        "room": room,
        "raw_text": raw_text,
        "photo_url": photo_url,
        "reminder_time": reminder_time,        # one-time reminder (existing)
        "reminder_sent": False,
        "is_medicine": is_medicine,             # NEW
        "reminder_times": reminder_times,       # NEW — ["08:00","14:00","21:00"]
        "repeat_type": repeat_type,             # NEW — "daily" or ""
        "timestamp": datetime.now(timezone.utc).isoformat()
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
    
def upload_photo(photo_base64: str, user_id: str) -> str:
    try:
        print(f"DEBUG: user_id={user_id}")
        print(f"DEBUG: photo_base64 length={len(photo_base64)}")
        print(f"DEBUG: photo starts with={photo_base64[:50]}")
        # remove data URL prefix if exists
        if ',' in photo_base64:
            photo_base64 = photo_base64.split(',')[1]

        # fix base64 padding
        photo_base64 = photo_base64.strip()
        padding = 4 - len(photo_base64) % 4
        if padding != 4:
            photo_base64 += '=' * padding

        # decode base64 to bytes
        photo_bytes = base64.b64decode(photo_base64)

        # upload to Firebase Storage
        bucket = firebase_admin.storage.bucket()
        filename = f"photos/{user_id}/{uuid.uuid4()}.jpg"
        blob = bucket.blob(filename)
        blob.upload_from_string(photo_bytes, content_type='image/jpeg')
        blob.make_public()

        return blob.public_url

    except Exception as e:
        print(f"Photo upload error: {e}")
        return ''
    
def update_item(item_id: str, user_id: str, updates: dict):
    try:
        doc_ref = db.collection('items').document(item_id)
        doc = doc_ref.get()
        if doc.exists and doc.to_dict().get('user_id') == user_id:
            doc_ref.update(updates)
            return True
        return False
    except Exception as e:
        print(f"Update error: {e}")
        return False