import json
import logging
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr

from ai_analyzer import BodyCompositionRequest, analyzer
from ai_planner import analyze_physique_photo, generate_llm_plans

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sayhitofit")

app = FastAPI(title="SAYHITOFIT API", version="2.0")

# Comma-separated list of allowed origins, e.g. "https://sayhitofit.com".
# "*" is acceptable for local development only.
allowed_origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "*").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

CONTACTS_FILE = Path("contacts.json")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN")


class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    message: str


def load_contacts():
    if CONTACTS_FILE.exists():
        with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_contacts(contacts):
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2)


@app.post("/api/contact")
async def submit_contact(contact: ContactMessage):
    """Handle contact form submissions"""
    try:
        contacts = load_contacts()
        new_contact = {
            "id": max((c.get("id", 0) for c in contacts), default=0) + 1,
            "name": contact.name,
            "email": contact.email,
            "message": contact.message,
            "timestamp": datetime.now().isoformat(),
        }
        contacts.append(new_contact)
        save_contacts(contacts)
        return {
            "success": True,
            "message": "Your message has been recorded successfully!",
            "contact_id": new_contact["id"],
        }
    except Exception:
        logger.exception("Failed to store contact submission")
        raise HTTPException(status_code=500, detail="Could not store your message, please try again.")


@app.get("/api/contacts")
async def get_contacts(x_admin_token: str | None = Header(default=None)):
    """Retrieve all contact submissions. Requires the X-Admin-Token header."""
    if not ADMIN_TOKEN:
        raise HTTPException(status_code=503, detail="Admin access is not configured (set ADMIN_TOKEN).")
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid admin token.")
    contacts = load_contacts()
    return {"success": True, "count": len(contacts), "contacts": contacts}


# Sync endpoint on purpose: FastAPI runs it in a threadpool, so the
# (blocking) Hugging Face call doesn't stall the event loop.
@app.post("/api/analyze-body-composition")
def analyze_body_composition(request: BodyCompositionRequest):
    """
    Analyze body composition and return personalized recommendations.
    Workout and nutrition plans are written by a Hugging Face language
    model when HF_TOKEN is configured; otherwise (or on any model
    failure) the built-in rule-based plans are returned.
    """
    if request.photo_data_url and not request.photo_data_url.startswith("data:image/"):
        raise HTTPException(status_code=400, detail="photo_data_url must be a data: URL with an image type.")

    try:
        result = analyzer.analyze(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    llm_plans = generate_llm_plans(
        request,
        {
            "bmi": result.bmi,
            "bmi_category": result.bmi_category,
            "body_fat_percentage": result.body_fat_percentage,
            "daily_calories": result.caloric_recommendation.maintenance,
            "protein_g": result.macro_breakdown["protein"]["grams"],
        },
    )
    if llm_plans:
        result.workout_plan, result.nutrition_plan = llm_plans
        result.plan_source = "ai"

    data = result.model_dump()

    # Optional physique photo: analyzed in-memory by the vision model, never stored.
    if request.photo_data_url:
        photo_result = analyze_physique_photo(request.photo_data_url, request)
        if photo_result:
            data["photo_analysis"] = photo_result.model_dump()
        else:
            data["photo_analysis"] = {
                "unavailable": True,
                "reason": "Photo analysis needs the AI model (HF_TOKEN) and a clear physique photo.",
            }

    return {"success": True, "data": data}


@app.post("/api/bulk-vs-cut")
def bulk_vs_cut_recommendation(request: BodyCompositionRequest):
    """Provide a specific bulk vs cut recommendation based on body composition"""
    try:
        analysis = analyzer.analyze(request)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    bmi = analysis.bmi
    body_fat = analysis.body_fat_percentage

    recommendation = {
        "current_bmi": bmi,
        "body_fat_percentage": body_fat,
        "recommendation": "",
        "reasoning": [],
    }

    if bmi < 18.5:
        recommendation["recommendation"] = "BULK (Build Muscle)"
        recommendation["reasoning"].append("Your BMI is in underweight range")
        recommendation["reasoning"].append("Prioritize caloric surplus and strength training")
    elif bmi > 30 or (body_fat and body_fat > 30):
        recommendation["recommendation"] = "CUT (Lose Fat)"
        recommendation["reasoning"].append("Your BMI/body fat is elevated")
        recommendation["reasoning"].append("Focus on 300-500 calorie deficit")
    elif body_fat and body_fat > 25:
        recommendation["recommendation"] = "CUT (Lose Fat)"
        recommendation["reasoning"].append(f"Body fat at {body_fat}% is above ideal range")
        recommendation["reasoning"].append("Reducing fat will improve body composition")
    elif body_fat and body_fat < 15:
        recommendation["recommendation"] = "BULK (Build Muscle)"
        recommendation["reasoning"].append(f"Body fat at {body_fat}% is lean - good for gaining")
        recommendation["reasoning"].append("You can handle a caloric surplus")
    else:
        recommendation["recommendation"] = "MAINTENANCE + RECOMP (Maintain weight, Build muscle)"
        recommendation["reasoning"].append("Your body composition is balanced")
        recommendation["reasoning"].append("Focus on strength training with maintenance calories")

    return {"success": True, "recommendation": recommendation}


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0",
        "llm_plans": "enabled" if os.getenv("HF_TOKEN") else "disabled (rule-based fallback)",
    }


# Serve the website itself. Mounted last so /api/* routes take priority.
# html=True makes "/" serve src/index.html directly.
app.mount("/", StaticFiles(directory="src", html=True), name="site")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
