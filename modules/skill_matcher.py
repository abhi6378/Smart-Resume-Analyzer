"""
skill_matcher.py

Advanced Skill Matching:
- TF-IDF Similarity (JD ↔ Resume)
- Semantic Similarity (Sentence Transformers)
- Combined Weighted Score
- Matched & Missing Skills
"""

from typing import List, Dict, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
import numpy as np

# High-accuracy semantic model
SEM_MODEL = SentenceTransformer("all-mpnet-base-v2")


# -----------------------------
# 1️⃣ TF-IDF Similarity
# -----------------------------
def compute_tfidf_similarity(text_a: str, text_b: str) -> float:
    """
    Compute TF-IDF cosine similarity between JD and Resume.
    """
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform([text_a, text_b])

    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    return round(float(similarity), 4)


# -----------------------------
# 2️⃣ Semantic Similarity (SBERT)
# -----------------------------
def compute_semantic_similarity(text_a: str, text_b: str) -> float:
    """
    Compute semantic similarity using Sentence-BERT.
    """
    emb_a = SEM_MODEL.encode(text_a, convert_to_tensor=True)
    emb_b = SEM_MODEL.encode(text_b, convert_to_tensor=True)

    similarity = util.cos_sim(emb_a, emb_b).cpu().numpy()[0][0]
    return round(float(similarity), 4)


# -----------------------------
# 3️⃣ Combined Similarity Score
# -----------------------------
def combined_score(tfidf_score: float, semantic_score: float, alpha: float = 0.5) -> float:
    """
    Weighted score:
    alpha = weight for TF-IDF
    (1 - alpha) = weight for semantic similarity
    """
    return round(alpha * tfidf_score + (1 - alpha) * semantic_score, 4)


# -----------------------------
# 4️⃣ Skill Gap Detection
# -----------------------------
def get_skill_gaps(resume_skills: List[str], jd_skills: List[str]) -> Tuple[List[str], List[str]]:
    """
    Return matched skills and missing skills.
    """
    resume_lower = {s.lower(): s for s in resume_skills}
    jd_lower = {s.lower(): s for s in jd_skills}

    matched = []
    missing = []

    for skill in jd_lower:
        if skill in resume_lower:
            matched.append(jd_lower[skill])
        else:
            missing.append(jd_lower[skill])

    return matched, missing


# -----------------------------
# 5️⃣ Main Function to Evaluate Candidate
# -----------------------------
def evaluate_candidate(resume_text: str, resume_skills: List[str], jd_text: str, jd_skills: List[str]) -> Dict:
    """
    Full Evaluation:
    - TF-IDF Similarity
    - Semantic Similarity
    - Combined Score
    - Matched vs Missing skills
    """
    tfidf_score = compute_tfidf_similarity(jd_text, resume_text)
    semantic_score = compute_semantic_similarity(jd_text, resume_text)
    final_score = combined_score(tfidf_score, semantic_score, alpha=0.4)

    matched, missing = get_skill_gaps(resume_skills, jd_skills)

    return {
        "tfidf_score": tfidf_score,
        "semantic_score": semantic_score,
        "final_score": round(final_score * 100, 2),  # convert to %
        "matched_skills": matched,
        "missing_skills": missing
    }
