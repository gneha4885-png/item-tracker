import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# Connect to Firebase using your key file
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred)

# Get Firestore database
db = firestore.client()

# Save a test item
db.collection("items").add({
    "user_id": "neha123",
    "item_name": "passport",
    "location": "blue drawer",
    "room": "bedroom",
    "timestamp": datetime.now().isoformat()
})

print("Item saved to Firestore successfully!")

# Read it back
items = db.collection("items").get()
print(f"Total items in database: {len(items)}")
for item in items:
    print(item.to_dict())