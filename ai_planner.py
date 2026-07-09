"""
LLM-powered workout and nutrition plan generator.

Calls a hosted instruct model on Hugging Face (serverless Inference API) to
write a personalized weekly workout plan and a simple, everyday-food diet.
If no HF_TOKEN is configured, or the API call / JSON parsing fails for any
reason, the caller falls back to the rule-based plans in ai_analyzer.py —
the site never breaks because the model is unavailable.

Configuration (environment / .env):
    HF_TOKEN        - Hugging Face access token (free account: https://huggingface.co/settings/tokens)
    HF_MODEL        - text model override, default Qwen/Qwen2.5-72B-Instruct
    HF_VISION_MODEL - vision model override, default Qwen/Qwen2.5-VL-72B-Instruct
"""

import json
import logging
import os
from typing import Optional, Tuple

from pydantic import BaseModel, ValidationError

from ai_analyzer import (
    BodyCompositionRequest,
    NutritionPlan,
    WorkoutPlan,
)


class PhotoAnalysis(BaseModel):
    """What the vision model can honestly say from a physique photo."""
    estimated_body_fat_range: str          # e.g. "18-22%"
    observations: list[str]                # short, neutral physique/posture notes
    confidence: str = "low"                # photos alone are never high confidence

logger = logging.getLogger("sayhitofit.ai_planner")

DEFAULT_MODEL = "Qwen/Qwen2.5-72B-Instruct"
DEFAULT_VISION_MODEL = "Qwen/Qwen2.5-VL-72B-Instruct"
REQUEST_TIMEOUT_S = 90

SYSTEM_PROMPT = """You are a certified strength coach and nutritionist writing plans for a \
fitness studio's clients. You answer with a single JSON object and nothing else - no \
markdown fences, no commentary.

The JSON must have exactly this shape:
{
  "workout_plan": {
    "split_name": "short name of the weekly split",
    "weekly_schedule": [
      {
        "day": "Monday",
        "focus": "what this session trains",
        "exercises": [
          {"name": "Exercise", "sets": "3", "reps": "8-10", "rest": "90s"}
        ]
      }
    ]
  },
  "nutrition_plan": {
    "template_name": "short name of the eating approach",
    "daily_meals": [
      {"meal": "Breakfast", "suggestions": ["option 1", "option 2"]}
    ],
    "pantry_staples": ["item 1", "item 2"]
  }
}

Rules for the workout plan:
- Match training days to the client's activity level (sedentary/light: 3 days, moderate: 4, very/extra active: 5).
- 3 to 5 exercises per day, real exercise names, sensible sets/reps/rest for the goal.
- Respect the client's goal (fat loss, muscle gain, or maintenance).

Rules for the nutrition plan - KEEP IT SIMPLE:
- Breakfast, Lunch, Dinner, and one Snack. Two suggestions each.
- Only common, affordable foods a beginner can cook: eggs, oats, rice, lentils, beans,
  chicken, fish, paneer/tofu, yogurt, vegetables, fruit, nuts. No exotic ingredients,
  no supplements unless the goal is muscle gain (whey is then allowed).
- Each suggestion is one short plain sentence, no recipes.
- 6 to 8 pantry staples."""


def _build_user_prompt(request: BodyCompositionRequest, analysis: dict) -> str:
    measurements = []
    if request.waist_cm:
        measurements.append(f"waist {request.waist_cm} cm")
    if request.hip_cm:
        measurements.append(f"hip {request.hip_cm} cm")
    if request.neck_cm:
        measurements.append(f"neck {request.neck_cm} cm")

    return (
        f"Client profile:\n"
        f"- Age {request.age}, {request.gender.value}\n"
        f"- Height {request.height_cm} cm, weight {request.weight_kg} kg\n"
        f"- Activity level: {request.activity_level.value}\n"
        f"- Goal: {request.fitness_goal.value}\n"
        f"- BMI {analysis.get('bmi')} ({analysis.get('bmi_category')})"
        + (f", estimated body fat {analysis['body_fat_percentage']}%" if analysis.get("body_fat_percentage") else "")
        + (f"\n- Measurements: {', '.join(measurements)}" if measurements else "")
        + f"\n- Daily calorie target: {analysis.get('daily_calories')} kcal, "
        f"protein target {analysis.get('protein_g')} g\n\n"
        "Write the workout_plan and nutrition_plan JSON for this client."
    )


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of the model's reply."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("no JSON object in model reply")
    return json.loads(text[start : end + 1])


def generate_llm_plans(
    request: BodyCompositionRequest,
    analysis: dict,
) -> Optional[Tuple[WorkoutPlan, NutritionPlan]]:
    """
    Ask the Hugging Face model for personalized plans.
    Returns (workout_plan, nutrition_plan) on success, None on any failure
    so the caller can fall back to the rule-based generator.
    """
    token = os.getenv("HF_TOKEN")
    if not token:
        logger.info("HF_TOKEN not set - using rule-based plans")
        return None

    model = os.getenv("HF_MODEL", DEFAULT_MODEL)

    try:
        from huggingface_hub import InferenceClient

        client = InferenceClient(model=model, token=token, timeout=REQUEST_TIMEOUT_S)
        response = client.chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(request, analysis)},
            ],
            max_tokens=1600,
            temperature=0.6,
        )
        raw = response.choices[0].message.content
        data = _extract_json(raw)
        workout = WorkoutPlan.model_validate(data["workout_plan"])
        nutrition = NutritionPlan.model_validate(data["nutrition_plan"])
        return workout, nutrition
    except (KeyError, ValueError, ValidationError) as exc:
        logger.warning("Model reply was not valid plan JSON (%s) - falling back to rules", exc)
        return None
    except Exception as exc:  # network errors, rate limits, auth failures
        logger.warning("Hugging Face call failed (%s: %s) - falling back to rules", type(exc).__name__, exc)
        return None


VISION_PROMPT = """You are an experienced fitness coach assessing a client's physique photo.
The photo is analyzed once and never stored. Reply with a single JSON object, nothing else:

{
  "estimated_body_fat_range": "a realistic range like 18-22%",
  "observations": ["3 to 5 short, neutral, encouraging coaching notes about visible muscle
                    development, proportions or posture"],
  "confidence": "low" or "medium"
}

Rules:
- Be honest: a photo only supports a rough body-fat RANGE, never an exact number.
  Use "medium" confidence only if the photo clearly shows the torso in decent lighting.
- If the image is not a human physique photo (or is unusable), reply instead with:
  {"error": "short reason"}
- Neutral and professional: describe the body like a coach, never mock or judge.
- Do not guess age, identity, or health conditions."""


def analyze_physique_photo(
    photo_data_url: str,
    request: BodyCompositionRequest,
) -> Optional[PhotoAnalysis]:
    """
    Ask the vision model for a rough body-fat range and coaching notes from a
    physique photo (a data: URL). The photo is sent to the model once and never
    written to disk. Returns None when the model is unconfigured/unavailable or
    the reply is unusable.
    """
    token = os.getenv("HF_TOKEN")
    if not token:
        logger.info("HF_TOKEN not set - photo analysis unavailable")
        return None

    model = os.getenv("HF_VISION_MODEL", DEFAULT_VISION_MODEL)

    try:
        from huggingface_hub import InferenceClient

        client = InferenceClient(model=model, token=token, timeout=REQUEST_TIMEOUT_S)
        response = client.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": photo_data_url}},
                        {
                            "type": "text",
                            "text": VISION_PROMPT
                            + f"\n\nContext the client entered: {request.gender.value}, "
                            f"age {request.age}, {request.height_cm} cm, {request.weight_kg} kg.",
                        },
                    ],
                }
            ],
            max_tokens=500,
            temperature=0.3,
        )
        data = _extract_json(response.choices[0].message.content)
        if "error" in data:
            logger.info("Vision model rejected the photo: %s", data["error"])
            return None
        return PhotoAnalysis.model_validate(data)
    except (KeyError, ValueError, ValidationError) as exc:
        logger.warning("Vision reply was not usable (%s)", exc)
        return None
    except Exception as exc:
        logger.warning("Vision model call failed (%s: %s)", type(exc).__name__, exc)
        return None
