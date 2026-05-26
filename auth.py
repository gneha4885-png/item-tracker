import requests
import os
from dotenv import load_dotenv
from firebase_admin import auth

load_dotenv()

FIREBASE_WEB_API_KEY = os.getenv("FIREBASE_WEB_API_KEY")

def register_user(email: str, password: str) -> dict:
    """Register a new user with Firebase Auth"""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_WEB_API_KEY}"
    
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    response = requests.post(url, json=payload)
    data = response.json()
    
    if "error" in data:
        raise Exception(data["error"]["message"])
    
    return {
        "user_id": data["localId"],
        "email": data["email"],
        "token": data["idToken"]
    }

def login_user(email: str, password: str) -> dict:
    """Login existing user and return token"""
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    response = requests.post(url, json=payload)
    data = response.json()
    
    if "error" in data:
        raise Exception(data["error"]["message"])
    
    return {
        "user_id": data["localId"],
        "email": data["email"],
        "token": data["idToken"]
    }

def verify_token(token: str) -> str:
    """Verify JWT token and return user_id"""
    try:
        decoded = auth.verify_id_token(token)
        return decoded["uid"]
    except Exception:
        raise Exception("Invalid or expired token")