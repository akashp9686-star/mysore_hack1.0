"""Generate misconception-driven wrong answers for Class 8 algebra authoring.

The engine is used at question-authoring time. It never participates in the
student-facing adaptive decision loop. Teacher knowledge is the source of the
misconception tag; the engine turns that knowledge into a concrete distractor.

Common one-variable linear-equation mistakes are generated deterministically.
For a teacher description outside those supported transformations, Gemini can
be used as an authoring-time helper. The generated result is stored in the DB,
so student assessment never depends on AI being available.
"""

from __future__ import annotations

import json
import os
import re
import time
from fractions import Fraction
from typing import Any, Iterable, Mapping

from dotenv import load_dotenv

load_dotenv()
AI_API_KEY = os.getenv("AI_API_KEY")
AI_MODEL = os.getenv("AI_MODEL", "gemini-3.8-flash")

_client = None
_types = None
try:
    from google import genai
    from google.genai import types
    _types = types
    if AI_API_KEY:
        _client = genai.Client(api_key=AI_API_KEY)
except ImportError:
    pass


def _format_fraction(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _parse_linear_side(expression: str) -> tuple[Fraction, Fraction] | None:
    expr = expression.replace(" ", "")
    if not expr:
        return None
    if expr[0] not in "+-":
        expr = "+" + expr
    tokens = re.findall(r"[+-][^+-]+", expr)
    coefficient = Fraction(0)
    constant = Fraction(0)
    for token in tokens:
        sign = -1 if token[0] == "-" else 1
        value = token[1:]
        if "x" in value.lower():
            core = value.lower().replace("x", "")
            coeff = Fraction(1) if core in ("", "+") else Fraction(core)
            coefficient += sign * coeff
        else:
            constant += sign * Fraction(value)
    return coefficient, constant


def _parse_linear_equation(text: str) -> tuple[Fraction, Fraction, Fraction, Fraction] | None:
    if "=" not in text:
        return None
    text = re.sub(r"^\s*solve\s*:\s*", "", text, flags=re.I)
    left, right = text.split("=", 1)
    parsed_left = _parse_linear_side(left)
    parsed_right = _parse_linear_side(right)
    if parsed_left is None or parsed_right is None:
        return None
    a, b = parsed_left
    c, d = parsed_right
    return a, b, c, d


def _sign_error_answer(question_text: str, mistake_description: str, step_text: str) -> str | None:
    parsed = _parse_linear_equation(question_text) or _parse_linear_equation(step_text)
    if parsed is None:
        return None
    a, b, c, d = parsed
    description = mistake_description.lower()

    if "constant" in description or "number" in description:
        coefficient = a - c
        wrong_rhs = d + b
        if coefficient != 0:
            return f"x = {_format_fraction(wrong_rhs / coefficient)}"

    if "variable" in description or "x term" in description:
        wrong_coefficient = a + c
        wrong_rhs = d - b
        if wrong_coefficient != 0:
            return f"x = {_format_fraction(wrong_rhs / wrong_coefficient)}"

    return None


def _forget_division(steps: list[Mapping[str, Any]], step_number: int) -> str | None:
    def _step_value(item: Mapping[str, Any], key: str, default: Any = "") -> Any:
        try:
            return item[key]
        except (KeyError, TypeError, IndexError):
            return default

    step = next((s for s in steps if int(_step_value(s, "step_number", 0)) == step_number), None)
    text = str(_step_value(step, "step_text", "")) if step else ""
    match = re.search(r"([+-]?\d+(?:\.\d+)?)x\s*=\s*([+-]?\d+(?:\.\d+)?)", text, re.I)
    if not match:
        return None
    coefficient, rhs = match.groups()
    if coefficient in {"1", "+1", "-1"}:
        return None
    variable_match = re.search(r"([A-Za-z])", text)
    variable = variable_match.group(1) if variable_match else "x"
    return f"{variable} = {rhs}"


def _deterministic_wrong_answer(*, question_text: str, correct_answer: str, mistake_description: str, steps: list[Mapping[str, Any]], step_number: int) -> str | None:
    description = mistake_description.lower()
    step = next((s for s in steps if int(s["step_number"]) == step_number), None)
    step_text = str(step["step_text"]) if step else ""

    if "sign" in description or "transpose" in description or "moving" in description:
        value = _sign_error_answer(question_text, description, step_text)
        if value and value.casefold() != correct_answer.strip().casefold():
            return value

    if any(word in description for word in ("divide", "division", "coefficient of x", "coefficient")):
        value = _forget_division(steps, step_number)
        if value and value.casefold() != correct_answer.strip().casefold():
            return value

    return None


def _ai_generate(*, question_text: str, correct_answer: str, steps: list[Mapping[str, Any]], step_number: int, mistake_description: str) -> str | None:
    if _client is None or _types is None:
        return None
    prompt = f"""
You are an expert Class 8 school-algebra teacher-authoring assistant.

Create ONE plausible wrong FINAL ANSWER for this Class 8 Mathematics → Algebra
→ Linear Equations multiple-choice question.

Question:
{question_text}

Correct final answer:
{correct_answer}

Correct solution steps:
{json.dumps(steps, ensure_ascii=False)}

The teacher says the student makes this specific mistake at Step {step_number}:
{mistake_description}

Apply that exact mistake at that exact step, then continue the resulting
incorrect calculation to a final answer. Do not invent a different mistake.
The wrong final answer must be different from the correct answer.

Return ONLY JSON:
{{"wrong_final_answer":"..."}}
""".strip()
    delays = (0.6, 1.2, 2.0)
    for attempt in range(3):
        try:
            response = _client.models.generate_content(
                model=AI_MODEL,
                contents=prompt,
                config=_types.GenerateContentConfig(response_mime_type="application/json"),
            )
            payload = json.loads(response.text)
            value = str(payload.get("wrong_final_answer", "")).strip()
            if value and value.casefold() != correct_answer.strip().casefold():
                return value
        except Exception:
            if attempt < len(delays):
                time.sleep(delays[attempt])
    return None


def generate_wrong_answer(*, question_text: str, correct_answer: str, steps: Iterable[Mapping[str, Any]], step_number: int, mistake_description: str) -> str:
    """Generate a final-answer distractor from a teacher-tagged mistake."""
    step_list = list(steps)
    deterministic = _deterministic_wrong_answer(
        question_text=question_text,
        correct_answer=correct_answer,
        mistake_description=mistake_description,
        steps=step_list,
        step_number=step_number,
    )
    if deterministic:
        return deterministic

    generated = _ai_generate(
        question_text=question_text,
        correct_answer=correct_answer,
        steps=step_list,
        step_number=step_number,
        mistake_description=mistake_description,
    )
    if generated:
        return generated

    raise ValueError(
        "The wrong-option engine could not generate a valid distractor from that mistake. "
        "Describe the algebra mistake more specifically, such as 'forgets to change the sign when "
        "transposing the constant' or 'forgets to divide by the coefficient of x'."
    )
