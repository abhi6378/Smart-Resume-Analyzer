# modules/llm_reasoner.py

import google.generativeai as genai

import json
import re
# Global model reference
_MODEL = None


def configure_gemini(api_key: str):
    """
    Configure Gemini API using frontend-provided key.
    Must be called BEFORE any reasoning.
    """
    global _MODEL

    genai.configure(api_key=api_key)

    # Create model AFTER configuration
    _MODEL = genai.GenerativeModel(
        model_name="gemini-2.5-flash-lite"
    )


def get_skill_reasoning(matched_skills, missing_skills):
    if _MODEL is None:
        raise RuntimeError("Gemini is not configured")

    prompt = f"""
You are an AI career advisor.

Matched skills:
{matched_skills}

Missing skills:
{missing_skills}

Return ONLY valid JSON in this exact format:

{{
  "SkillName": {{
    "related_to": "skill or concept",
    "explanation": "clear explanation",
    "courses": [
      {{ "title": "course name", "provider": "platform" }},
      {{ "title": "course name", "provider": "platform" }}
    ]
  }}
}}
"""

    response = _MODEL.generate_content(prompt)
    text = response.text.strip()

    # 🔒 Extract JSON safely
    try:
        json_text = re.search(r"\{.*\}", text, re.S).group()
        parsed = json.loads(json_text)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}
