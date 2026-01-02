"""
parser.py (cloud-safe, high-accuracy)

- Uses pdfplumber instead of PyMuPDF (Streamlit Cloud compatible)
- Uses spaCy transformer model (en_core_web_trf) if available
- Falls back to en_core_web_md
- Uses phonenumbers for robust phone extraction
- Optional semantic skill detection using sentence-transformers
"""

from typing import List, Dict, Optional
import re
import json
import logging

# -----------------------------
# PDF Parsing (CLOUD SAFE)
# -----------------------------
import pdfplumber

# -----------------------------
# Phone number extraction
# -----------------------------
import phonenumbers

# -----------------------------
# spaCy (NER)
# -----------------------------
import spacy
try:
    nlp = spacy.load("en_core_web_trf")
    logging.info("Loaded spaCy transformer model: en_core_web_trf")
except Exception:
    try:
        nlp = spacy.load("en_core_web_md")
        logging.warning("en_core_web_trf not available, falling back to en_core_web_md")
    except Exception as e:
        raise RuntimeError(
            "spaCy model not found. Install en_core_web_trf or en_core_web_md"
        ) from e

# -----------------------------
# sentence-transformers (semantic skills)
# -----------------------------
try:
    from sentence_transformers import SentenceTransformer, util
    SBERT_AVAILABLE = True
    EMB_MODEL = SentenceTransformer("all-mpnet-base-v2")
except Exception:
    SBERT_AVAILABLE = False
    EMB_MODEL = None

# -----------------------------
# Regex patterns
# -----------------------------
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")


# =========================================================
# PDF TEXT EXTRACTION
# =========================================================
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using pdfplumber (cloud-safe)."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


# =========================================================
# CONTACT DETAILS
# =========================================================
def extract_email(text: str) -> Optional[str]:
    match = EMAIL_REGEX.search(text)
    return match.group(0) if match else None


def extract_phone(text: str, default_region: str = "IN") -> Optional[str]:
    if not text:
        return None

    for match in phonenumbers.PhoneNumberMatcher(text, default_region):
        num = match.number
        if phonenumbers.is_valid_number(num):
            return phonenumbers.format_number(
                num, phonenumbers.PhoneNumberFormat.E164
            )

    # fallback regex
    regex = re.compile(r"(\+?\d{1,3}[-.\s]?)?(\d{10})")
    m = regex.search(text)
    return m.group(0) if m else None


# =========================================================
# NAME EXTRACTION
# =========================================================
def extract_name(text: str) -> Optional[str]:
    if not text:
        return None

    header = "\n".join(text.splitlines()[:15])
    doc = nlp(header)

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            return ent.text.strip()

    # fallback: full scan
    doc_full = nlp(text)
    for ent in doc_full.ents:
        if ent.label_ == "PERSON":
            return ent.text.strip()

    return None


# =========================================================
# SKILL EXTRACTION
# =========================================================
def _normalize_skill(s: str) -> str:
    return s.strip().lower()


def extract_skills_by_keyword(text: str, skills_list: List[str]) -> List[str]:
    text_low = text.lower()
    found = []

    for s in skills_list:
        if _normalize_skill(s) in text_low:
            found.append(s)

    # deduplicate
    return list(dict.fromkeys(found))


def extract_skills_semantic(
    text: str,
    skills_list: List[str],
    threshold: float = 0.68
) -> List[str]:
    if not SBERT_AVAILABLE:
        return []

    resume_emb = EMB_MODEL.encode(text, convert_to_tensor=True)
    skill_embs = EMB_MODEL.encode(skills_list, convert_to_tensor=True)

    scores = util.cos_sim(resume_emb, skill_embs)[0].cpu().tolist()
    return [skills_list[i] for i, score in enumerate(scores) if score >= threshold]


# =========================================================
# MAIN RESUME PARSER
# =========================================================
def parse_resume(
    file_path: str,
    skills_list: List[str],
    use_semantic: bool = True
) -> Dict:
    raw_text = extract_text_from_pdf(file_path)

    name = extract_name(raw_text)
    email = extract_email(raw_text)
    phone = extract_phone(raw_text)

    keyword_skills = extract_skills_by_keyword(raw_text, skills_list)

    semantic_skills = []
    if use_semantic and SBERT_AVAILABLE:
        semantic_skills = extract_skills_semantic(raw_text, skills_list)

    combined_skills = list(dict.fromkeys(semantic_skills + keyword_skills))

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": combined_skills,
        "raw_text": raw_text
    }


# =========================================================
# JD SKILL EXTRACTION
# =========================================================
def extract_skills_from_text(text: str, skill_list: list):
    text_lower = text.lower()
    return list({
        skill for skill in skill_list if skill.lower() in text_lower
    })


# =========================================================
# CLI TEST
# =========================================================
if __name__ == "__main__":
    SKILLS = [
        "Python", "Machine Learning", "Deep Learning", "NLP",
        "TensorFlow", "PyTorch", "Flask", "Django", "SQL",
        "Tableau", "Power BI"
    ]

    sample = "../data/resumes/sample_resume.pdf"
    res = parse_resume(sample, SKILLS, use_semantic=True)

    print(json.dumps(
        {k: v for k, v in res.items() if k != "raw_text"},
        indent=2
    ))
