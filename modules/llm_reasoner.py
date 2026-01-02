# modules/llm_reasoner.py

import google.generativeai as genai

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
    """
    Uses Gemini to explain missing skills and recommend courses.
    Assumes configure_gemini() has already been called.
    """

    if _MODEL is None:
        raise RuntimeError(
            "Gemini is not configured. Call configure_gemini() first."
        )

    prompt = f"""
You are an AI career advisor.

Matched skills:
{matched_skills}

Missing skills:
{missing_skills}

For each missing skill:
1. Explain how it relates to the matched skills (if applicable)
2. Explain why it is important
3. Suggest 2 learning courses (Coursera / Udemy)

Respond ONLY in valid JSON with this format:

{{
  "skill_name": {{
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

    # Gemini returns text → parse safely
    try:
        return eval(response.text)
    except Exception:
        return {
            "error": "Failed to parse Gemini response",
            "raw_response": response.text
        }
