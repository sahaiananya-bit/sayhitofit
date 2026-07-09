# SAYHITOFIT

Website + API for a natural movement training studio. A FastAPI backend serves a
static frontend and powers a **Body Analyzer**: body-composition math (BMI, US Navy
body fat, Mifflin-St Jeor BMR/TDEE, macros) plus a workout and simple diet plan
written by a Hugging Face language model, with a rule-based fallback so the site
works even without a model token.

## Stack

- **Backend** — Python, FastAPI, Pydantic ([main.py](main.py), [ai_analyzer.py](ai_analyzer.py), [ai_planner.py](ai_planner.py))
- **Frontend** — static HTML/CSS/JS in `src/` (no build step), vanilla JS + requestAnimationFrame for the scroll animations, Chart.js on the analyzer page
- **LLM plans** — Hugging Face serverless Inference API (`huggingface_hub`).
  Text plans: `Qwen/Qwen2.5-72B-Instruct`. Physique photo analysis: `Qwen/Qwen2.5-VL-72B-Instruct`.
  Both overridable via `HF_MODEL` / `HF_VISION_MODEL`. All body metrics (BMI, body fat,
  BMR, TDEE, macros) come from validated formulas, never from the model.

## Project structure

```
main.py            FastAPI app: contact API, analyzer API, serves src/ as the website
ai_analyzer.py     Body-composition formulas + rule-based plan generator
ai_planner.py      Hugging Face LLM plan generation (falls back to rules on any failure)
test_analyzer.py   Test cases for the analyzer
src/
  index.html       Home: hero, about, programs, BMI check, contact
  programs.html    Program details
  ai-analyzer.html Body Analyzer (calls the API)
  assets/css/main.css   The whole design system
  assets/js/main.js     Nav, animations, BMI calculator, contact form
  assets/js/analyzer.js Analyzer form + results rendering
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env         # then edit .env
```

In `.env`:

- `HF_TOKEN` — free token from https://huggingface.co/settings/tokens.
  With it, workout/diet plans are model-written; without it, rule-based plans are used.
- `ADMIN_TOKEN` — any secret string; required to read contact submissions via
  `GET /api/contacts` (send as `X-Admin-Token` header). Endpoint stays disabled if empty.

## Run

```bash
uvicorn main:app --reload
```

Open **http://localhost:8000/** — the API and the website are served together,
so no separate web server is needed.

## API

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/api/analyze-body-composition` | POST | Full analysis + workout & diet plans (`plan_source`: `ai` or `rules`) |
| `/api/bulk-vs-cut` | POST | Bulk vs cut recommendation |
| `/api/contact` | POST | Store a contact form message |
| `/api/contacts` | GET | List messages (requires `X-Admin-Token`) |
| `/api/health` | GET | Health + whether LLM plans are enabled |

Interactive docs: http://localhost:8000/docs

## Tests

```bash
python test_analyzer.py
```

## How it works

1. **You open http://localhost:8000/** — FastAPI serves the static site from `src/`
   and the API from `/api/*` in one process.
2. **The Body Analyzer form** posts your height/weight/age (plus optional waist,
   hip, neck measurements and a physique photo) to `/api/analyze-body-composition`.
3. **`ai_analyzer.py` computes every number** with validated formulas: BMI, body fat
   (US Navy circumference method, Deurenberg fallback), BMR (Mifflin-St Jeor),
   TDEE, calorie targets, macros, target weight range and timeline.
4. **`ai_planner.py` asks the Hugging Face model** (Qwen 2.5 72B) to write the weekly
   workout split and a simple everyday-food diet around those numbers. If a photo was
   uploaded, the vision model (Qwen 2.5 VL) estimates a body-fat *range* with coaching
   notes — the photo is analyzed in memory and never stored.
5. **Any model failure falls back silently** to the built-in rule-based plans, and the
   response's `plan_source` field tells the UI which one you got ("ai" or "rules").
6. **The frontend renders it all** — metric cards, calorie targets, a Chart.js macro
   doughnut, the training week, meals and pantry staples.

Key rule: the language model never produces the health numbers — only the plan text.

## Design

Frontend follows the standards in [CLAUDEwebdesign copy.md](CLAUDEwebdesign%20copy.md):
a clean white / near-black editorial base (layout adapted from the MONO reference
template) with ember `#ff6b35` as the single brand accent and full-color training
photography. Type system: Fraunces (display serif) / Inter (body) / JetBrains Mono
(labels, data). Signature moves: the scroll-scrubbed bento hero, numbered section
eyebrows, and a floating pill nav — all mobile-first with `prefers-reduced-motion`
respected.
