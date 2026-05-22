from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# GET endpoint - just reads and returns data
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Item Tracker API is running!"}

# This defines what data we expect in POST request
class HelloRequest(BaseModel):
    name: str

# POST endpoint - accepts data and returns a response
@app.post("/hello")
def say_hello(request: HelloRequest):
    return {"message": f"Hello {request.name}! Welcome to Item Tracker!"}