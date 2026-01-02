"""
parser.py (upgraded)

- Uses spaCy transformer model (en_core_web_trf) if available (fallback to en_core_web_sm).
- Uses phonenumbers for robust phone extraction.
- Optional semantic skill detection using sentence-transformers.
"""

from typing import List, Dict, Optional
import re
import fitz  # PyMuPDF
import json
import logging

# improved phone detection
import phonenumbers

# spaCy (transformer if available)
import spacy
try:
    # prefer transformer model for higher NER accuracy
    nlp = spacy.load("en_core_web_trf")
    logging.info("Loaded spaCy transformer model: en_core_web_trf")
except Exception:
    try:
        nlp = spacy.load("en_core_web_md")
        logging.warning("en_core_web_trf not available, falling back to en_core_web_sm")
    except Exception as e:
        raise RuntimeError("spaCy model not found. Install en_core_web_trf or en_core_web_md") from e

# sentence-transformers (optional, for semantic skill matching)
try:
    from sentence_transformers import SentenceTransformer, util
    SBERT_AVAILABLE = True
    EMB_MODEL = SentenceTransformer("all-mpnet-base-v2")  # high-accuracy embedding
except Exception:
    SBERT_AVAILABLE = False
    EMB_MODEL = None

# Basic email regex (robust)
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF using PyMuPDF."""
    text = ""
    with fitz.open(file_path) as pdf:
        for page in pdf:
            text += page.get_text("text")
    return text


def extract_email(text: str) -> Optional[str]:
    """Extract the first email address found."""
    match = EMAIL_REGEX.search(text)
    return match.group(0) if match else None


def extract_phone(text: str, default_region: str = "IN") -> Optional[str]:
    """
    Extract phone number using phonenumbers library for robust international parsing.
    Returns the first valid number in E.164 format if possible.
    """
    if not text:
        return None
    for match in phonenumbers.PhoneNumberMatcher(text, default_region):
        num = match.number
        if phonenumbers.is_valid_number(num):
            return phonenumbers.format_number(num, phonenumbers.PhoneNumberFormat.E164)
    # fallback: try simple regex (10 digits)
    regex = re.compile(r"(\+?\d{1,3}[-.\s]?)?(\d{10})")
    m = regex.search(text)
    if m:
        return m.group(0)
    return None


def extract_name(text: str) -> Optional[str]:
    """
    Extract name using spaCy's PERSON entity. Transformer model will give better accuracy.
    We return the first PERSON entity found near the top of the document (likely the candidate name).
    """
    if not text:
        return None
    # Consider only first N lines to prioritize header
    header = "\n".join(text.splitlines()[:15])
    doc = nlp(header)
    names = [ent.text.strip() for ent in doc.ents if ent.label_ == "PERSON"]
    if names:
        return names[0]
    # fallback: full doc scan
    doc_full = nlp(text)
    for ent in doc_full.ents:
        if ent.label_ == "PERSON":
            return ent.text.strip()
    return None


def _normalize_skill(s: str) -> str:
    return s.strip().lower()


def extract_skills_by_keyword(text: str, skills_list: List[str]) -> List[str]:
    """
    Extract skills by exact/substring keyword match (case-insensitive).
    This is fast and OK for obvious matches.
    """
    text_low = text.lower()
    found = []
    for s in skills_list:
        if _normalize_skill(s) in text_low:
            found.append(s)
    # deduplicate while preserving order
    seen = set()
    result = []
    for x in found:
        if x not in seen:
            result.append(x)
            seen.add(x)
    return result


def extract_skills_semantic(text: str, skills_list: List[str], threshold: float = 0.65) -> List[str]:
    """
    Use SBERT to compute semantic similarity between resume text and each skill label.
    Returns skills whose cosine similarity passes the threshold.
    Requires sentence-transformers installed.
    """
    if not SBERT_AVAILABLE:
        raise RuntimeError("sentence-transformers not installed. Install it to use semantic matching.")

    # encode resume as a short representation — we can either encode full text or important sentences
    resume_emb = EMB_MODEL.encode(text, convert_to_tensor=True)
    skill_texts = [s for s in skills_list]
    skill_embs = EMB_MODEL.encode(skill_texts, convert_to_tensor=True)

    cos_scores = util.cos_sim(resume_emb, skill_embs)[0].cpu().tolist()
    matched = [skill_texts[i] for i, score in enumerate(cos_scores) if score >= threshold]
    return matched


def parse_resume(file_path: str, skills_list: List[str], use_semantic: bool = True) -> Dict:
    """
    Parse resume and return structured data. If use_semantic=True and SBERT is available,
    semantic skill matching will be attempted and merged with keyword matches.
    """
    raw_text = extract_text_from_pdf(file_path)
    name = extract_name(raw_text)
    email = extract_email(raw_text)
    phone = extract_phone(raw_text)

    # Keyword matches (fast)
    keyword_skills = extract_skills_by_keyword(raw_text, skills_list)

    # Semantic matches (optional, better recall)
    semantic_skills = []
    if use_semantic and SBERT_AVAILABLE:
        try:
            semantic_skills = extract_skills_semantic(raw_text, skills_list, threshold=0.68)
        except Exception:
            semantic_skills = []

    # merge keyword + semantic, with semantic taking precedence for uniqueness
    combined = list(dict.fromkeys(semantic_skills + keyword_skills))

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": combined,
        "raw_text": raw_text
    }


# Quick CLI test
if __name__ == "__main__":
    SKILLS = [
        "Python", "Machine Learning", "Deep Learning", "NLP",
        "TensorFlow", "PyTorch", "Flask", "Django", "SQL", "Tableau", "Power BI"
    ]
    sample = "../data/resumes/sample_resume.pdf"
    res = parse_resume(sample, SKILLS, use_semantic=True)
    print(json.dumps({k: v for k, v in res.items() if k != "raw_text"}, indent=2))
# ---------------------------------------------------------
# Extract skills from JD text (simple keyword matching)
# ---------------------------------------------------------
def extract_skills_from_text(text: str, skill_list: list):
    """
    Extract skills from job description text using keyword matching.
    Returns: list of detected skills.
    """
    text_lower = text.lower()
    found = []

    for skill in skill_list:
        if skill.lower() in text_lower:
            found.append(skill)

    return list(set(found))