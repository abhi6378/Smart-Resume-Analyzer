"""
llm_reasoner.py

Uses Gemini 2.5 Flash-Lite to:
- Map missing skills to related skills
- Explain missing skills
- Provide course recommendations input (later paired with Coursera API)
"""

from typing import List, Dict
import google.generativeai as genai
import json


# -----------------------------------
# 1. Configure Gemini
# -----------------------------------
def configure_gemini(api_key: str):
    genai.configure(api_key="")


# -----------------------------------
# 2. Build Prompt
# -----------------------------------
def build_skill_reason_prompt(known_skills: List[str], missing_skills: List[str]) -> str:
    return f"""
You are an AI HR Analyst.

Given the candidate's known skills and missing job skills:

KNOWN SKILLS:
{known_skills}

MISSING SKILLS:
{missing_skills}

TASK:
For EACH missing skill:
1. Tell if this missing skill is a subskill, specialization, tool, or concept related to any known skills.
2. If related, describe HOW it relates.
3. Suggest 2 beginner-friendly online courses (Coursera/Udemy/Google) — ONLY course name & provider.
4. Return STRICT JSON following this schema:

{{
  "skill_name": {{
    "related_to": "skill from known skills OR 'not related'",
    "explanation": "why it is missing and how it relates",
    "courses": [
        {{"title": "string", "provider": "string"}},
        {{"title": "string", "provider": "string"}}
    ]
  }}
}}

IMPORTANT RULES:
- Return JSON ONLY. No extra words.
- Do not include markdown.
- Keep responses concise and accurate.
    """


# -----------------------------------
# 3. Call Gemini Model
# -----------------------------------
def get_skill_reasoning(known_skills: List[str], missing_skills: List[str]) -> Dict:
    prompt = build_skill_reason_prompt(known_skills, missing_skills)

    model = genai.GenerativeModel("gemini-2.5-flash-lite")

    response = model.generate_content(prompt)

    text = response.text.strip()

    # Parse JSON safely
    try:
        data = json.loads(text)
        return data
    except json.JSONDecodeError:
        # try to clean up common issues
        cleaned = text.replace("```json", "").replace("```", "")
        try:
            return json.loads(cleaned)
        except:
            return {"error": "Could not parse JSON", "raw_output": text}
