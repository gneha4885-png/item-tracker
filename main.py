from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from database import save_item, get_all_items, find_item, delete_item, upload_photo,db, update_item, send_push_notification
from claude_service import extract_item_location, find_item_location
from auth import register_user, login_user
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timezone




app = FastAPI(
    title="Item Tracker API",
    description="AI powered item location tracker",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request Models ────────────────────────────────────────────
class LogItemRequest(BaseModel):
    text: str
    user_id: str = "neha123"
    photo_url: str = ""
    reminder_time: str = ""
    is_medicine: bool = False
    reminder_times: list[str] = []   # e.g. ["08:00", "14:00", "21:00"]
    repeat_type: str = ""             # "daily" or "" for one-time

    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty')
        if len(v.strip()) < 5:
            raise ValueError('Text too short — please describe where you kept the item')
        if len(v) > 500:
            raise ValueError('Text too long — please keep it under 500 characters')
        return v.strip()

class AuthRequest(BaseModel):
    email: str
    password: str

class UploadPhotoRequest(BaseModel):
    photo_base64: str
    user_id: str

class UpdateItemRequest(BaseModel):
    user_id: str
    text: str
    reminder_time: str = ""
    is_medicine: bool = False
    reminder_times: list[str] = []
    repeat_type: str = ""

# ── Response Models ───────────────────────────────────────────
class LogItemResponse(BaseModel):
    message: str
    item_name: str
    location: str
    room: str
    reminder_time: str = ""

# ── Health ────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Item Tracker API is running!",
        "version": "1.0.0"
    }

# ── Upload Photo ──────────────────────────────────────────────
@app.post("/upload-photo")
def upload_photo_endpoint(request: UploadPhotoRequest):
    try:
        photo_url = upload_photo(request.photo_base64, request.user_id)
        if not photo_url:
            raise HTTPException(status_code=500, detail="Photo upload failed")
        return {"photo_url": photo_url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Photo upload error: {str(e)}")

# ── Log Item ──────────────────────────────────────────────────
@app.post("/log-item", response_model=LogItemResponse)
def log_item(request: LogItemRequest):
    try:
        extracted = extract_item_location(request.text)

        if extracted["item_name"] == "unknown" and extracted["location"] == "unknown":
            raise HTTPException(
                status_code=400,
                detail="I couldn't understand what item or location you mentioned. Try something like 'I kept my keys in the kitchen drawer'"
            )

        save_item(
            user_id=request.user_id,
            item_name=extracted["item_name"],
            location=extracted["location"],
            room=extracted["room"],
            raw_text=request.text,
            photo_url=request.photo_url,
            reminder_time=request.reminder_time,
            is_medicine=request.is_medicine,
            reminder_times=request.reminder_times,
            repeat_type=request.repeat_type,
        )

        return LogItemResponse(
            message=f"Got it! I saved your {extracted['item_name']} 📍",
            item_name=extracted["item_name"],
            location=extracted["location"],
            room=extracted["room"],
            reminder_time=request.reminder_time  # ← add this
)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")

# ── Find Item ─────────────────────────────────────────────────
@app.get("/find-item")
def find_item_endpoint(query: str, user_id: str = "neha123"):
    if not query or not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Please ask a question like 'where are my keys?'"
        )
    try:
        items = find_item(user_id, query)
        answer = find_item_location(query, items)
        return {
            "query": query,
            "answer": answer,
            "total_items_searched": len(items)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")

# ── My Items ──────────────────────────────────────────────────
@app.get("/my-items")
def my_items(user_id: str = "neha123"):
    try:
        items = get_all_items(user_id)
        return {
            "items": items,
            "total": len(items)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")

# ── Auth ──────────────────────────────────────────────────────
@app.post("/register")
def register(request: AuthRequest):
    try:
        result = register_user(request.email, request.password)
        return {
            "message": "Account created successfully!",
            "user_id": result["user_id"],
            "email": result["email"],
            "token": result["token"]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login")
def login(request: AuthRequest):
    try:
        result = login_user(request.email, request.password)
        return {
            "message": "Login successful!",
            "user_id": result["user_id"],
            "email": result["email"],
            "token": result["token"]
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

# ── Delete Item ───────────────────────────────────────────────
@app.delete("/items/{item_id}")
def delete_item_endpoint(item_id: str, user_id: str):
    success = delete_item(item_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}



#---------------------------------------
class FcmTokenRequest(BaseModel):
    user_id: str
    fcm_token: str

@app.post("/save-fcm-token")
def save_fcm_token(request: FcmTokenRequest):
    try:
        db.collection("users").document(request.user_id).set(
            {"fcm_token": request.fcm_token},
            merge=True
        )
        return {"message": "Token saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ── Update Item ───────────────────────────────────────────────
@app.patch("/items/{item_id}")
def update_item_endpoint(item_id: str, request: UpdateItemRequest):
    try:
        updates = {
            'item_name': request.text,
            'raw_text': request.text
        }
        if request.reminder_time:
            updates['reminder_time'] = request.reminder_time
        if request.is_medicine:
            updates['is_medicine'] = request.is_medicine
            updates['reminder_times'] = request.reminder_times
            updates['repeat_type'] = request.repeat_type
        success = update_item(item_id, request.user_id, updates)
        if not success:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message": "Item updated successfully!"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # ── Reminder Scheduler — checks every minute for due reminders ──
def check_and_send_reminders():
    """Runs every minute. Checks for due reminders and sends push notifications."""
    try:
        now = datetime.now(timezone.utc)
        now_iso = now.isoformat()

        # ── One-time reminders ──
        items_ref = db.collection("items").where("reminder_sent", "==", False)
        for doc in items_ref.stream():
            data = doc.to_dict()
            reminder_time = data.get("reminder_time")
            if not reminder_time:
                continue
            if reminder_time <= now_iso:
                user_doc = db.collection("users").document(data["user_id"]).get()
                if user_doc.exists:
                    fcm_token = user_doc.to_dict().get("fcm_token")
                    if fcm_token:
                        send_push_notification(
                            fcm_token,
                            "⏰ Keeep Reminder",
                            f"\"{data.get('item_name','Item')}\" is in {data.get('location','its location')}. Time to use it!"
                        )
                doc.reference.update({"reminder_sent": True})

        # ── Medicine reminders (recurring daily) ──
        medicine_items = db.collection("items").where("is_medicine", "==", True).stream()
        current_hhmm = now.strftime("%H:%M")
        for doc in medicine_items:
            data = doc.to_dict()
            reminder_times = data.get("reminder_times", [])
            if current_hhmm in reminder_times:
                last_sent_key = f"last_sent_{current_hhmm.replace(':','')}"
                last_sent_date = data.get(last_sent_key, "")
                today_str = now.strftime("%Y-%m-%d")
                if last_sent_date != today_str:
                    user_doc = db.collection("users").document(data["user_id"]).get()
                    if user_doc.exists:
                        fcm_token = user_doc.to_dict().get("fcm_token")
                        if fcm_token:
                            send_push_notification(
                                fcm_token,
                                "💊 Medicine Time!",
                                f"Time to take \"{data.get('item_name','medicine')}\" — kept in {data.get('location','its location')}"
                            )
                    doc.reference.update({last_sent_key: today_str})
    except Exception as e:
        print(f"Scheduler error: {e}")

scheduler = BackgroundScheduler()
scheduler.add_job(check_and_send_reminders, 'interval', minutes=1)
scheduler.start()