from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from datetime import datetime
import json
import os
from pathlib import Path

app = FastAPI()

# Add CORS middleware to allow requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to store contact submissions
CONTACTS_FILE = Path("contacts.json")

# Pydantic model for validation
class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    message: str

def load_contacts():
    """Load existing contacts from JSON file"""
    if CONTACTS_FILE.exists():
        with open(CONTACTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_contacts(contacts):
    """Save contacts to JSON file"""
    with open(CONTACTS_FILE, 'w') as f:
        json.dump(contacts, f, indent=2)

@app.post("/api/contact")
async def submit_contact(contact: ContactMessage):
    """Handle contact form submissions"""
    try:
        # Load existing contacts
        contacts = load_contacts()
        
        # Create new contact entry with timestamp
        new_contact = {
            "id": len(contacts) + 1,
            "name": contact.name,
            "email": contact.email,
            "message": contact.message,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to list and save
        contacts.append(new_contact)
        save_contacts(contacts)
        
        return {
            "success": True,
            "message": "Your message has been recorded successfully!",
            "contact_id": new_contact["id"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/contacts")
async def get_contacts():
    """Retrieve all contacts (for admin purposes)"""
    try:
        contacts = load_contacts()
        return {
            "success": True,
            "count": len(contacts),
            "contacts": contacts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "SAYHITOFIT Contact API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
