from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import save_item, get_all_items, find_item
from claude_service import extract_item_location, find_item_location


app = FastAPI()

# Request model
class LogItemRequest(BaseModel):
    text: str
    user_id: str = "neha123"  # hardcoded for now, auth comes Day 10

# Response model
class LogItemResponse(BaseModel):
    message: str
    item_name: str
    location: str
    room: str

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Item Tracker API is running!"}

@app.post("/log-item", response_model=LogItemResponse)
def log_item(request: LogItemRequest):
    try:
        # Step 1: Send text to Claude for extraction
        extracted = extract_item_location(request.text)
        
        # Step 2: Save to Firestore
        save_item(
            user_id=request.user_id,
            item_name=extracted["item_name"],
            location=extracted["location"],
            room=extracted["room"],
            raw_text=request.text
        )
        
        # Step 3: Return success response
        return LogItemResponse(
            message=f"Got it! I saved your {extracted['item_name']}",
            item_name=extracted["item_name"],
            location=extracted["location"],
            room=extracted["room"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/my-items")
def my_items(user_id: str = "neha123"):
    items = get_all_items(user_id)
    return {"items": items, "total": len(items)}

@app.get("/find-item")
def find_item_endpoint(query: str, user_id: str = "neha123"):
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))