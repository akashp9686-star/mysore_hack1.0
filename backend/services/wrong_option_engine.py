"""Generate misconception-driven wrong answers for Class 8 algebra authoring.

Teacher-entered misconceptions are the trusted source. The deterministic
engine handles common one-variable linear-equation mistakes without requiring
AI. Gemini remains an authoring-time fallback for descriptions that cannot be
resolved deterministically.

This module does not participate in the student adaptive decision loop.
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
    """Return a clean school-algebra representation."""
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _clean_description(text: str) -> str:
    """Normalize teacher wording so equivalent descriptions are recognized."""
    text = str(text or "").strip().lower()
    text = text.replace("−", "-")
    text = text.replace("–", "-")
    text = text.replace("’", "'")
    text = re.sub(r"\s+", " ", text)
    return text


def _parse_linear_side(expression: str) -> tuple[Fraction, Fraction] | None:
    """
    Parse a linear expression into:

        coefficient_of_x, constant

    Examples:
        2x + 4 -> (2, 4)
        -3x - 6 -> (-3, -6)
        x + 5 -> (1, 5)
        7 -> (0, 7)
    """
    expr = str(expression or "").replace(" ", "")

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

            if core in ("", "+"):
                coeff = Fraction(1)
            elif core == "-":
                coeff = Fraction(-1)
            else:
                try:
                    coeff = Fraction(core)
                except (ValueError, ZeroDivisionError):
                    return None

            coefficient += sign * coeff
        else:
            try:
                constant += sign * Fraction(value)
            except (ValueError, ZeroDivisionError):
                return None

    return coefficient, constant


def _parse_linear_equation(
    text: str,
) -> tuple[Fraction, Fraction, Fraction, Fraction] | None:
    """
    Parse:

        ax + b = cx + d

    into:

        a, b, c, d
    """
    if "=" not in str(text or ""):
        return None

    text = re.sub(
        r"^\s*solve\s*:\s*",
        "",
        str(text),
        flags=re.IGNORECASE,
    )

    left, right = text.split("=", 1)

    parsed_left = _parse_linear_side(left)
    parsed_right = _parse_linear_side(right)

    if parsed_left is None or parsed_right is None:
        return None

    a, b = parsed_left
    c, d = parsed_right

    return a, b, c, d


def _extract_variable(text: str) -> str:
    """Return the variable used in a solution step, defaulting to x."""
    match = re.search(r"\b([A-Za-z])\b", str(text or ""))
    if match:
        return match.group(1)

    match = re.search(r"([A-Za-z])", str(text or ""))
    if match:
        return match.group(1)

    return "x"


def _step_value(
    item: Mapping[str, Any] | None,
    key: str,
    default: Any = "",
) -> Any:
    if item is None:
        return default

    try:
        return item[key]
    except (KeyError, TypeError, IndexError):
        return default


def _find_step(
    steps: Iterable[Mapping[str, Any]],
    step_number: int,
) -> Mapping[str, Any] | None:
    for step in steps:
        try:
            if int(_step_value(step, "step_number", 0)) == int(step_number):
                return step
        except (TypeError, ValueError):
            continue

    return None


def _sign_error_answer(
    question_text: str,
    mistake_description: str,
    step_text: str,
) -> str | None:
    """
    Generate a final answer caused by forgetting a sign while transposing.

    Two important cases are supported:

    1. Constant/number transposition:
         ax + b = cx + d
         wrong: ax - cx = d + b

    2. Variable/x-term transposition:
         ax + b = cx + d
         wrong: ax + cx = d - b
    """
    parsed = (
        _parse_linear_equation(question_text)
        or _parse_linear_equation(step_text)
    )

    if parsed is None:
        return None

    a, b, c, d = parsed
    description = _clean_description(mistake_description)

    constant_words = (
        "constant",
        "number",
        "term",
        "right side",
        "left side",
    )

    variable_words = (
        "variable",
        "x term",
        "variable term",
        "x-term",
        "xterm",
    )

    # Constant/sign mistake.
    if any(word in description for word in constant_words):
        coefficient = a - c
        wrong_rhs = d + b

        if coefficient != 0:
            return f"x = {_format_fraction(wrong_rhs / coefficient)}"

    # Variable/x-term sign mistake.
    if any(word in description for word in variable_words):
        wrong_coefficient = a + c
        wrong_rhs = d - b

        if wrong_coefficient != 0:
            return f"x = {_format_fraction(wrong_rhs / wrong_coefficient)}"

    return None


def _forget_division(
    steps: list[Mapping[str, Any]],
    step_number: int,
) -> str | None:
    """
    Generate the answer obtained by stopping before dividing by the
    coefficient of x.

    Example:
        4x = 16
        wrong final answer -> x = 16
    """
    step = _find_step(steps, step_number)

    if step is None:
        return None

    text = str(_step_value(step, "step_text", ""))

    match = re.search(
        r"([+-]?\d+(?:\.\d+)?)\s*x\s*=\s*([+-]?\d+(?:\.\d+)?)",
        text,
        re.IGNORECASE,
    )

    if not match:
        return None

    coefficient_text, rhs_text = match.groups()

    try:
        coefficient = Fraction(coefficient_text)
    except (ValueError, ZeroDivisionError):
        return None

    if coefficient in (Fraction(1), Fraction(-1)):
        return None

    variable = _extract_variable(text)

    return f"{variable} = {rhs_text}"


def _wrong_arithmetic_answer(
    question_text: str,
    correct_answer: str,
    mistake_description: str,
) -> str | None:
    """
    Handle common arithmetic-wording mistakes where a teacher says that a
    student combines/adds/subtracts the terms incorrectly.

    This is deliberately conservative. It only generates a result when the
    equation has a simple integer solution and the teacher explicitly refers
    to arithmetic or combining terms.
    """
    description = _clean_description(mistake_description)

    arithmetic_words = (
        "arithmetic",
        "calculate",
        "calculation",
        "combine",
        "combining",
        "addition",
        "subtraction",
        "subtract",
        "add incorrectly",
        "adds incorrectly",
        "subtracts incorrectly",
        "simplify incorrectly",
    )

    if not any(word in description for word in arithmetic_words):
        return None

    parsed = _parse_linear_equation(question_text)

    if parsed is None:
        return None

    a, b, c, d = parsed
    coefficient = a - c
    rhs = d - b

    if coefficient == 0:
        return None

    correct_value = rhs / coefficient

    # A small, deterministic arithmetic slip.
    if correct_value.denominator == 1:
        candidate = correct_value + 1
    else:
        candidate = correct_value + Fraction(1, 2)

    candidate_text = f"x = {_format_fraction(candidate)}"

    if candidate_text.casefold() == correct_answer.strip().casefold():
        return None

    return candidate_text


def _deterministic_candidates(
    *,
    question_text: str,
    correct_answer: str,
    steps: list[Mapping[str, Any]],
    step_number: int,
    mistake_description: str,
) -> list[str]:
    """
    Produce deterministic candidates for one teacher-described mistake.

    The first candidate is the preferred answer. Additional candidates are
    useful to the authoring layer when it needs to fill remaining MCQ slots.
    """
    description = _clean_description(mistake_description)
    candidates: list[str] = []

    def add(value: str | None) -> None:
        if not value:
            return

        value = str(value).strip()

        if not value:
            return

        if value.casefold() == correct_answer.strip().casefold():
            return

        if any(existing.casefold() == value.casefold() for existing in candidates):
            return

        candidates.append(value)

    step = _find_step(steps, step_number)
    step_text = str(_step_value(step, "step_text", ""))

    # Sign/transposition mistakes.
    if any(
        word in description
        for word in ("sign", "transpose", "transposing", "moving", "move across")
    ):
        add(
            _sign_error_answer(
                question_text,
                description,
                step_text,
            )
        )

    # Forgetting to divide by the coefficient.
    if any(
        word in description
        for word in (
            "divide",
            "division",
            "coefficient of x",
            "coefficient",
            "dividing",
        )
    ):
        add(_forget_division(steps, step_number))

    # Arithmetic/combining-term mistake.
    add(
        _wrong_arithmetic_answer(
            question_text,
            correct_answer,
            description,
        )
    )

    return candidates


def generate_wrong_answers(
    *,
    question_text: str,
    correct_answer: str,
    steps: Iterable[Mapping[str, Any]],
    step_number: int,
    mistake_description: str,
    maximum: int = 3,
) -> list[str]:
    """
    Generate up to `maximum` distinct wrong final answers.

    This is the multi-option interface used by the enhanced authoring layer.
    It is deterministic whenever the teacher description matches a supported
    algebra misconception. Gemini is used only when deterministic generation
    cannot produce an answer.
    """
    if maximum < 1:
        return []

    step_list = list(steps)

    candidates = _deterministic_candidates(
        question_text=question_text,
        correct_answer=correct_answer,
        steps=step_list,
        step_number=step_number,
        mistake_description=mistake_description,
    )

    if len(candidates) >= maximum:
        return candidates[:maximum]

    generated = _ai_generate(
        question_text=question_text,
        correct_answer=correct_answer,
        steps=step_list,
        step_number=step_number,
        mistake_description=mistake_description,
        existing_answers=candidates,
    )

    if generated:
        for value in generated:
            if value.casefold() == correct_answer.strip().casefold():
                continue

            if any(
                existing.casefold() == value.casefold()
                for existing in candidates
            ):
                continue

            candidates.append(value)

            if len(candidates) >= maximum:
                break

    return candidates[:maximum]


def generate_wrong_answer(
    *,
    question_text: str,
    correct_answer: str,
    steps: Iterable[Mapping[str, Any]],
    step_number: int,
    mistake_description: str,
) -> str:
    """
    Backwards-compatible single-distractor API.

    Existing teacher-authoring code can continue calling this function.
    """
    candidates = generate_wrong_answers(
        question_text=question_text,
        correct_answer=correct_answer,
        steps=steps,
        step_number=step_number,
        mistake_description=mistake_description,
        maximum=1,
    )

    if candidates:
        return candidates[0]

    raise ValueError(
        "The wrong-option engine could not generate a valid distractor from "
        "that mistake. Describe the algebra mistake more specifically, such "
        "as 'forgets to change the sign when transposing the constant', "
        "'forgets to change the sign when transposing the x term', or "
        "'forgets to divide by the coefficient of x'."
    )


def _ai_generate(
    *,
    question_text: str,
    correct_answer: str,
    steps: list[Mapping[str, Any]],
    step_number: int,
    mistake_description: str,
    existing_answers: list[str] | None = None,
) -> list[str]:
    """Use Gemini only as an authoring-time fallback."""
    if _client is None or _types is None:
        return []

    existing = existing_answers or []

    prompt = f"""
You are an expert Class 8 school-algebra teacher-authoring assistant.

Create up to 3 plausible WRONG FINAL ANSWERS for this Class 8 Mathematics
-> Algebra -> Linear Equations multiple-choice question.

Question:
{question_text}

Correct final answer:
{correct_answer}

Correct solution steps:
{json.dumps(steps, ensure_ascii=False)}

The teacher says students make this specific mistake at Step {step_number}:
{mistake_description}

Apply that exact mistake at that exact step, then continue the resulting
incorrect calculation to a final answer.

Do not invent a different misconception.
Every returned answer must be different from the correct answer.
Do not repeat any existing generated answers.

Existing generated answers:
{json.dumps(existing, ensure_ascii=False)}

Return ONLY JSON in this exact form:
{{"wrong_final_answers":["...", "...", "..."]}}
""".strip()

    delays = (0.6, 1.2, 2.0)

    for attempt in range(3):
        try:
            response = _client.models.generate_content(
                model=AI_MODEL,
                contents=prompt,
                config=_types.GenerateContentConfig(
                    response_mime_type="application/json"
                ),
            )

            payload = json.loads(response.text)

            values = payload.get("wrong_final_answers", [])

            if not isinstance(values, list):
                return []

            results: list[str] = []

            for value in values:
                value = str(value).strip()

                if not value:
                    continue

                if value.casefold() == correct_answer.strip().casefold():
                    continue

                if any(
                    existing_value.casefold() == value.casefold()
                    for existing_value in results
                ):
                    continue

                if any(
                    existing_value.casefold() == value.casefold()
                    for existing_value in existing
                ):
                    continue

                results.append(value)

                if len(results) >= 3:
                    break

            return results

        except Exception:
            if attempt < len(delays):
                time.sleep(delays[attempt])

    return []
