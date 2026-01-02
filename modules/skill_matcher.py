# modules/skill_matcher.py

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import numpy as np

# Load semantic model once (VERY IMPORTANT for performance & accuracy)
SEMANTIC_MODEL = SentenceTransformer("all-mpnet-base-v2")


def evaluate_candidate(
    resume_text: str,
    resume_skills: list,
    jd_text: str,
    jd_skills: list,
):
    """
    Evaluates a candidate against a job description using:
    - TF-IDF similarity (keyword level)
    - Semantic similarity (meaning level)
    - Skill overlap with semantic tolerance
    """

    # -------------------------------
    # 1. TF-IDF Similarity (baseline)
    # -------------------------------
    tfidf = TfidfVectorizer(stop_words="english")
    tfidf_matrix = tfidf.fit_transform([resume_text, jd_text])
    tfidf_score = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:2]
    )[0][0]

    # -----------------------------------
    # 2. Semantic Similarity (PRIMARY)
    # -----------------------------------
    embeddings = SEMANTIC_MODEL.encode(
        [resume_text, jd_text],
        convert_to_numpy=True
    )

    semantic_score = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    # -----------------------------------
    # 3. Skill Matching (SMART LOGIC)
    # -----------------------------------
    matched_skills = []
    missing_skills = []

    resume_skills_lower = [s.lower() for s in resume_skills]

    for jd_skill in jd_skills:
        jd_skill_lower = jd_skill.lower()

        # Direct keyword match
        if jd_skill_lower in resume_skills_lower:
            matched_skills.append(jd_skill)
            continue

        # Semantic skill match (sub-skill tolerance)
        skill_embeddings = SEMANTIC_MODEL.encode(
            [jd_skill_lower] + resume_skills_lower,
            convert_to_numpy=True
        )

        jd_emb = skill_embeddings[0]
        resume_embs = skill_embeddings[1:]

        similarities = cosine_similarity(
            [jd_emb],
            resume_embs
        )[0]

        # Threshold tuned for MAX accuracy
        if np.max(similarities) >= 0.70:
            matched_skills.append(jd_skill)
        else:
            missing_skills.append(jd_skill)

    return {
        "tfidf_score": round(float(tfidf_score), 4),
        "semantic_score": round(float(semantic_score), 4),
        "matched_skills": sorted(list(set(matched_skills))),
        "missing_skills": sorted(list(set(missing_skills))),
    }
