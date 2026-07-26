# CLAUDE.md — SAYHITOFIT project reference

Fitness studio website + API. FastAPI serves both the static site and the API from one
process. The "Body Analyzer" computes body-composition metrics with validated formulas,
then a Hugging Face LLM writes the workout plan + simple diet (rule-based fallback).

## Run

```
venv\Scripts\python.exe -m uvicorn main:app --port 8000
```

Site + API at http://localhost:8000/ (docs at /docs). Preview config: `.claude/launch.json`
(name `sayhitofit`). **Backend .py changes need a server restart** (no --reload in launch
config); files in `src/` are served from disk, browser reload is enough.

Tests: `PYTHONIOENCODING=utf-8 venv/Scripts/python.exe test_analyzer.py`
(the env var matters — the script prints emoji, cp1252 console crashes without it).

## Architecture

- `main.py` — FastAPI app. Endpoints: POST `/api/analyze-body-composition` (main one,
  sync-def on purpose so the blocking HF call runs in a threadpool), POST `/api/bulk-vs-cut`,
  POST `/api/contact` (stores to `contacts.json`), GET `/api/contacts` (requires
  `X-Admin-Token` header == `ADMIN_TOKEN` env; 503 if unset), GET `/api/health` (shows if
  LLM enabled). Static site mounted LAST at `/` with html=True.
- `ai_analyzer.py` — all body math (BMI, US Navy body fat, Mifflin-St Jeor BMR, TDEE,
  macros) + rule-based workout/nutrition plans. Pydantic models live here.
  `BodyCompositionResponse.plan_source` = "rules" | "ai".
- `ai_assistant.py` — site chatbot. POST `/api/chat` takes `{messages:[{role,content}]}`
  (stateless, client sends history; server keeps last 10, 1000 chars each, 400 reply tokens).
  System prompt hardcodes the 3 programs + prices and FORBIDS computing anyone's personal
  numbers (redirects to the analyzer) — keep that rule. Never errors: returns
  `OFFLINE_MESSAGE` with `source:"offline"` when the model is unreachable.
- `ai_planner.py` — Hugging Face calls via `huggingface_hub.InferenceClient.chat_completion`.
  `generate_llm_plans()` (text) and `analyze_physique_photo()` (vision, takes a data: URL,
  never stores the image). Both return None on ANY failure → caller falls back to rules.
  Timeout 90s (72B on free tier is slow; 60s was observed timing out).

## Config (.env, gitignored; template in .env.example)

- `HF_TOKEN` — set and working (fine-grained, only "Make calls to Inference Providers").
  Was pasted in chat once — suggest rotation if user worries.
- `HF_MODEL` = Qwen/Qwen2.5-72B-Instruct (text plans)
- `HF_VISION_MODEL` = Qwen/Qwen2.5-VL-72B-Instruct (photo → body-fat RANGE + notes only;
  never claims exact numbers from photos — keep it that way, it's a deliberate honesty rule)
- `ADMIN_TOKEN` — empty (contacts endpoint disabled)

Key product rule: **metrics never come from the LLM** — formulas compute all numbers;
models only write plan text / photo notes. Don't change this.

## Frontend (src/, no build step)

- **Pivoted to a monochrome design (2026-07-07)**, adapted from a "MONO" Next.js/Tailwind
  reference template the user supplied (light theme variant). One stylesheet:
  `src/assets/css/main.css`. Tokens: --background #FFFFFF, --foreground #0A0A0A,
  --surface #F5F5F5, --muted #737373, --border #E5E5E5. **Zero accent color** — the old
  ember (#ff6b35) brand is gone, this was an explicit user-directed pivot, not a mistake.
  Radius 0 everywhere except pills (nav CTA, buttons, mobile menu panel).
  Fonts: Fraunces (display serif, swap-in for the reference's paid "PP Editorial New") /
  Inter (body) / JetBrains Mono (eyebrows, data, nav labels).
  `CLAUDEwebdesign copy.md`'s hard bans (no purple, no gradient headlines, etc.) still
  apply and aren't violated by this palette.
  **Update 2026-07-09: ember #ff6b35 reinstated as the single accent** (user asked for
  orange back): `--ember` token used on primary pill buttons, nav CTA, eyebrows,
  program numbers, BMI category, plan-source.ai badge, spinner, unit toggle,
  selection, and the protein slice of the macro chart (#ff6b35 / #0a0a0a / #e5e5e5).
- Signature interactions, all vanilla JS + rAF (no GSAP dependency for these — GSAP is
  gone from main.js entirely now):
  - **Floating pill header** (`header` fixed top:1rem, centered, rounded-full,
    goes translucent+blurred+shadowed past 50px scroll).
  - **Hero scroll-scrubbed bento** (`#hero-track`, 220vh) — giant word "SAYHITOFIT"
    (15vw) fades out over the first 15% of scrub progress while a center IMAGE
    (`hero-center.jpg`, olympic lifter — replaced the old hero.mp4 video for scroll
    smoothness) shrinks 100%→20% width and two photo columns slide in 15%→60%, then
    HOLD assembled for the rest of the scrub. Progress divisor must be
    `track.offsetHeight - innerHeight` (NOT innerHeight*2 — that bug made assembly
    never complete on screen). Word sits behind the media (opacity-linked inverse).
  - **Method section 3D headline rotation** (`#method-track`, 220vh sticky) — three short
    phrases rotateX in/out tied to scroll progress, ported from philosophy-section.tsx.
  - **Blur-word paragraph reveal** — words sharpen from blur(12px)→0 word-by-word as their
    container scrolls into view (`#method-paragraph`).
  - Photos: 8 processed JPEGs in src/assets/images (hero-1..4, hero-center, bento-1..2,
    quote-wide), AI-generated by the user via Gemini, watermarks removed (the Gemini
    sparkle sits ~130-330px from the bottom-right corner at FIXED pixel offset — crop
    the bottom 330px, or side-crop when the subject would be cut). Keep original color
    (user rejected grayscale). Raw Gemini_*.png sources are gitignored/deleted;
    old fundamentals.jpg/advanced.jpg and hero.mp4 are deleted.
- `index.html` (bento hero, method/rotating-headline, programs strip, bento gallery,
  full-bleed quote section, analyzer callout, BMI calc, contact), `programs.html`,
  `ai-analyzer.html` (form + results, includes photo upload).
- `src/assets/js/main.js` — nav/mobile menu, header scroll pill, hero scroll-scrub, method
  rotation/blur, IntersectionObserver reveal-up for plain sections, BMI calc, contact form.
  `analyzer.js` — analyzer form, photo picker (client-side downscale to ≤768px JPEG data
  URL), results rendering incl. Chart.js macro doughnut (slice colors now monochrome:
  #0a0a0a / #a3a3a3 / #e5e5e5 — legend swatches must match, see `.swatch` class).
- All API calls are relative (`/api/...`) — site must be opened through FastAPI, not file://.

## History / gotchas

- Repo folder may be `Sayhitofir` (typo) or `sayhitofit` — user was renaming it.
  If venv breaks after the rename: `python -m venv venv --clear` + reinstall requirements.
- Old bugs already fixed (don't reintroduce): estimate_body_fat_percentage once referenced
  an undefined `height_cm`; female Navy formula needs waist+hip+neck or falls back to
  Deurenberg BMI formula.
- Deleted as dead code: src/components/*.js (React leftovers), src/assets/css/styles.css.
- `AI_ANALYZER_README.md`, `API_DOCUMENTATION.md`, `WEBPAGE_DOCUMENTATION.md` are STALE
  (pre-redesign); README.md is current.
- Nothing committed yet beyond the initial commit — the entire feature set is uncommitted
  working tree as of 2026-07-03.
