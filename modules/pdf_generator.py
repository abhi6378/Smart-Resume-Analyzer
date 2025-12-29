"""
pdf_generator.py

Generates a clean, professional HR-style PDF report for each candidate.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT
from reportlab.lib import colors
from typing import Dict, List


def generate_candidate_report(candidate: Dict, output_path: str):
    """
    Generates a clean, ATS-style PDF summary for a candidate.

    candidate dict must contain:
    - name
    - email
    - phone
    - final_score
    - matched_skills (list)
    - missing_skills (list)
    - reasoning (dict from Gemini)
    """

    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#222222"),
        spaceAfter=10
    )

    section_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#004aad"),
        spaceAfter=6
    )

    paragraph_style = ParagraphStyle(
        "Paragraph",
        parent=styles["BodyText"],
        fontSize=11,
        leading=16,
        textColor=colors.black,
        alignment=TA_LEFT
    )

    bullet_style = ParagraphStyle(
        "Bullet",
        parent=styles["BodyText"],
        fontSize=11,
        leading=14,
        leftIndent=20
    )

    content = []

    # ------------------------------------------------
    # Header
    # ------------------------------------------------
    content.append(Paragraph(f"Candidate Report: {candidate['name']}", title_style))
    content.append(Paragraph(f"Email: {candidate['email']}", paragraph_style))
    content.append(Paragraph(f"Phone: {candidate['phone']}", paragraph_style))
    content.append(Spacer(1, 10))

    # ------------------------------------------------
    # Match Score
    # ------------------------------------------------
    content.append(Paragraph("Overall Match Score", section_style))
    content.append(Paragraph(f"<b>{candidate['final_score']}% match</b>", paragraph_style))
    content.append(Spacer(1, 15))

    # ------------------------------------------------
    # Matched Skills
    # ------------------------------------------------
    content.append(Paragraph("Matched Skills", section_style))

    if candidate["matched_skills"]:
        for s in candidate["matched_skills"]:
            content.append(Paragraph(f"• {s}", bullet_style))
    else:
        content.append(Paragraph("No matched skills found.", paragraph_style))

    content.append(Spacer(1, 15))

    # ------------------------------------------------
    # Missing Skills
    # ------------------------------------------------
    content.append(Paragraph("Missing Skills", section_style))

    if candidate["missing_skills"]:
        for s in candidate["missing_skills"]:
            content.append(Paragraph(f"• {s}", bullet_style))
    else:
        content.append(Paragraph("None.", paragraph_style))

    content.append(Spacer(1, 15))

    # ------------------------------------------------
    # LLM Reasoning from Gemini
    # ------------------------------------------------
    content.append(Paragraph("AI Reasoning Summary", section_style))

    reasoning = candidate.get("reasoning", {})

    if reasoning:
        for skill, details in reasoning.items():
            content.append(Paragraph(f"<b>{skill}</b>", paragraph_style))
            content.append(Paragraph(f"Related to: {details['related_to']}", bullet_style))
            content.append(Paragraph(f"Explanation: {details['explanation']}", bullet_style))
            content.append(Spacer(1, 5))
    else:
        content.append(Paragraph("No reasoning available.", paragraph_style))

    content.append(Spacer(1, 15))

    # ------------------------------------------------
    # Course Recommendations
    # ------------------------------------------------
    content.append(Paragraph("Recommended Courses", section_style))

    if reasoning:
        for skill, details in reasoning.items():
            courses = details.get("courses", [])
            content.append(Paragraph(f"<b>{skill}</b>", paragraph_style))

            for c in courses:
                content.append(Paragraph(f"• {c['title']} ({c['provider']})", bullet_style))

            content.append(Spacer(1, 8))

    doc.build(content)
