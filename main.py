from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from database import save_item, get_all_items, find_item, delete_item, upload_photo
from claude_service import extract_item_location, find_item_location
from auth import register_user, login_user
from typing import Optional
from database import save_item, get_all_items, find_item, delete_item, upload_photo, update_item

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

class LogItemRequest(BaseModel):
    text: str
    user_id: str = "neha123"
    photo_url: str = ""    # ← is this line there?

# ── Response Models ───────────────────────────────────────────
class LogItemResponse(BaseModel):
    message: str
    item_name: str
    location: str
    room: str

# ── Health ────────────────────────────────────────────────────
@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Item Tracker API is running!",
        "version": "1.0.0"
    }

# ── Upload Photo ──────────────────────────────────────────────
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
        # Step 1: Send text to Claude for extraction
        extracted = extract_item_location(request.text)

        # Step 2: Check if extraction was meaningful
        if extracted["item_name"] == "unknown" and extracted["location"] == "unknown":
            raise HTTPException(
                status_code=400,
                detail="I couldn't understand what item or location you mentioned. Try something like 'I kept my keys in the kitchen drawer'"
            )

        # Step 3: Save to Firestore with photo_url
        save_item(
    user_id=request.user_id,
    item_name=extracted["item_name"],
    location=extracted["location"],
    room=extracted["room"],
    raw_text=request.text,
    photo_url=request.photo_url,
    reminder_time=request.reminder_time,  # ← ADD THIS
)

        # Step 4: Return success response
        return LogItemResponse(
            message=f"Got it! I saved your {extracted['item_name']} 📍",
            item_name=extracted["item_name"],
            location=extracted["location"],
            room=extracted["room"]
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


# ── Update Item ───────────────────────────────────────────
class UpdateItemRequest(BaseModel):
    user_id: str
    text: str

@app.patch("/items/{item_id}")
def update_item_endpoint(item_id: str, request: UpdateItemRequest):
    try:
        success = update_item(item_id, request.user_id, {
            'item_name': request.text,
            'raw_text': request.text
        })
        if not success:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"message": "Item updated successfully!"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))