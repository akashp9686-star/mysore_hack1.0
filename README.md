# HackMysore 1.0 — Personalized Learning Platform

Integrated MVP for the HackMysore Personalized Learning Platform.

## Included

- Adinath's SQLite database layer and seeded demo data
- FastAPI backend and deterministic adaptive-learning engine
- Jai Ganesh AI diagnostic service behind the backend
- HTML/CSS/JavaScript frontend
- Supabase Google OAuth wiring with a local demo-login fallback
- School Classes 5–9 learning path only
- Separate Mathematics curriculum for Classes 5, 6, 7, 8 and 9
- General Concepts space with Communication Skills, Spell Talk, Chess Learning and Brainstorm placeholders
- Class-specific basic video links + schedulable MCQ sessions
- Progress-aware MCQ selection that prioritizes concepts needing more practice
- Diagnostic MCQs → weak concept → targeted practice → reassessment → progress → facilitator flow
- Liquid Glass-inspired responsive UI based on the supplied UI/UX material
- Supplied UI/UX design system kept under `design-system-reference/`

## Architecture

`Frontend → FastAPI REST API → SQLite`

AI is called only by the backend. The frontend never accesses SQLite or the AI provider directly.

The adaptive engine is the source of truth for learning state and next action. AI is advisory and the core learning flow continues if AI is unavailable. Mathematics MCQ sessions are separated by class curriculum, and question selection uses the learner's recorded concept progress.

## VS Code setup

Open this folder in VS Code.

### 1. Create virtual environment

```powershell
python -m venv venv
```

### 2. Activate it

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure AI

Copy `.env.example` to `.env` and add the AI key supplied by the team.

Do not commit `.env`.

### 5. Seed/check the database

```powershell
python backend/database/seed.py
```

### 6. Start FastAPI

```powershell
uvicorn backend.main:app --reload
```

### 7. Open the website

`http://localhost:8000`

API docs:

`http://localhost:8000/docs`

## Google login

See `SUPABASE_SETUP.md`.

The frontend is ready for Supabase Google OAuth, but your Supabase project URL/publishable key and Google provider configuration must be supplied by the team. These are project-specific settings and are not invented or committed into the repository.

## GitHub workflow

```powershell
git init
git add .
git commit -m "Integrate personalized learning platform"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

Check `git status` before every commit and make sure `.env` is ignored.

## Tests

```powershell
pytest -q
```

Current integrated backend test result during packaging: **19 passed**.

JavaScript syntax was also checked with Node.js.

## Floating Learning Assistant
Every page includes a floating **✦ Learning Assistant** button. Open it whenever you want to ask about the learner's current weakness, recommendation, next step, or improvement. The assistant calls `POST /api/ai/assistant` and receives only backend learning evidence. The adaptive engine remains the source of truth; AI is advisory and the learning flow continues if AI is unavailable.
