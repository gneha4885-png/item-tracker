from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel, validator
from database import save_item, get_all_items, find_item, delete_item
from claude_service import extract_item_location, find_item_location
from auth import register_user, login_user, verify_token
from typing import Optional

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

# Request model with validation
class LogItemRequest(BaseModel):
    text: str
    user_id: str = "neha123"

    @validator('text')
    def text_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Text cannot be empty')
        if len(v.strip()) < 5:
            raise ValueError('Text too short — please describe where you kept the item')
        if len(v) > 500:
            raise ValueError('Text too long — please keep it under 500 characters')
        return v.strip()

# Response model
class LogItemResponse(BaseModel):
    message: str
    item_name: str
    location: str
    room: str

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Item Tracker API is running!",
        "version": "1.0.0"
    }

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

        # Step 3: Save to Firestore
        save_item(
            user_id=request.user_id,
            item_name=extracted["item_name"],
            location=extracted["location"],
            room=extracted["room"],
            raw_text=request.text
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

@app.get("/find-item")
def find_item_endpoint(query: str, user_id: str = "neha123"):
    # Validate query
    if not query or not query.strip():
        raise HTTPException(
            status_code=400,
            detail="Please ask a question like 'where are my keys?'"
        )

    try:
        # Step 1: Get all items for this user
        items = find_item(user_id, query)

        # Step 2: Ask Claude to find the best match
        answer = find_item_location(query, items)

        # Step 3: Return the answer
        return {
            "query": query,
            "answer": answer,
            "total_items_searched": len(items)
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")

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
    
# Auth models
class AuthRequest(BaseModel):
    email: str
    password: str

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
    
@app.delete("/items/{item_id}")
def delete_item_endpoint(item_id: str, user_id: str):
    success = delete_item(item_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}
