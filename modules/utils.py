# utils.py

# Master skill list for matching in parser + analyzer
# Add more as needed — this list is used in parser and matcher
SKILL_LIST = [
    "python", "java", "javascript", "typescript", "c++", "c", "c#",
    "html", "css", "react", "node", "express", "angular",
    "flask", "django", "fastapi",

    "machine learning", "deep learning", "nlp", "data science",
    "computer vision", "data analysis", "statistics", "sql",

    "tensorflow", "pytorch", "keras", "scikit-learn",

    "docker", "kubernetes", "aws", "azure", "gcp",

    "git", "github", "devops",

    "communication", "leadership"
]

# Clean skill text helper
def normalize_skill(skill: str) -> str:
    return skill.strip().lower()
