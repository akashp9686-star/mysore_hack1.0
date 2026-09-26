"""Jai Ganesh's Gemini diagnostic agent, integrated as an advisory service.

The deterministic adaptive engine remains the source of truth for persisted
learning status and actions. This service enriches an attempt with an AI
explanation when an API key is configured.
"""

import json
import os

from dotenv import load_dotenv

from .prompts import ERROR_ANALYSIS_PROMPT

load_dotenv()
AI_API_KEY = os.getenv("AI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "gemini-3.8-flash")

client = None
try:
    from google import genai
    from google.genai import types
    if AI_API_KEY:
        client = genai.Client(api_key=AI_API_KEY)
except ImportError:
    types = None


def analyze_student_error(question: str, student_answer: str, correct_answer: str, concept: str) -> dict:
    fallback = {
        "error_type": "unknown",
        "identified_concept": concept,
        "confidence": 0.0,
        "explanation": "The response was recorded. The adaptive engine will use the student's answer pattern to choose the next step.",
        "recommended_action": "targeted_practice",
        "source": "fallback",
    }

    if not AI_API_KEY or client is None or types is None:
        return fallback

    try:
        prompt = ERROR_ANALYSIS_PROMPT.format(
            question=question,
            student_answer=student_answer,
            correct_answer=correct_answer,
            concept=concept,
        )
        response = client.models.generate_content(
            model=AI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        result = json.loads(response.text)
        result["source"] = "jai_ganesh_ai_agent"
        return result
    except Exception as exc:
        print(f"AI diagnostic unavailable: {exc}")
        return fallback


def answer_learning_question(message: str, evidence: dict) -> dict:
    """Answer student questions using only backend-provided learning evidence.

    The AI is advisory. It must not invent scores, concepts, attempts, or learning
    states. If the model is unavailable, a small evidence-based fallback keeps the
    core learning experience working.
    """
    weak = evidence.get("weak_concept") or {}
    student = evidence.get("student") or {}
    intervention = evidence.get("latest_intervention") or {}
    latest = evidence.get("latest_attempt") or {}

    fallback = {
        "answer": (
            f"Your current focus is {weak.get('name') or student.get('current_topic') or 'your current topic'}. "
            f"Your recorded accuracy for this concept is {round(float(weak.get('accuracy', 0)))}%. "
            f"The recommended next step is to follow the targeted learning step shown on your dashboard."
        ),
        "source": "fallback",
    }

    if not AI_API_KEY or client is None or types is None:
        return fallback

    prompt = f"""
You are the Learning Assistant inside a personalized learning platform.
Answer the learner's question using ONLY the backend evidence below.
Address the learner by the exact name in backend evidence when a name is useful.
You are advisory: never change learning state, scores, records, or recommendations.
Never invent student performance data. If evidence is missing, say so.
Use concise, encouraging language. Do not claim to have seen hidden working steps.
You may explain why a concept was flagged, what the learner should practice next,
or what improved, but the adaptive engine remains the source of truth.

Learner question:
{message}

Backend learning evidence (JSON):
{json.dumps(evidence, ensure_ascii=False)}

Return ONLY a JSON object with this shape:
{{"answer":"..."}}
"""
    try:
        response = client.models.generate_content(
            model=AI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        result = json.loads(response.text)
        answer = str(result.get("answer", "")).strip()
        if not answer:
            return fallback
        return {"answer": answer, "source": "jai_ganesh_ai_agent"}
    except Exception as exc:
        print(f"AI assistant unavailable: {exc}")
        return fallback
