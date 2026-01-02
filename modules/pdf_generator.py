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


# modules/pdf_generator.py

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    ListFlowable,
    ListItem
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.units import inch


def generate_candidate_report(candidate_data: dict, output_path: str):
    """
    Generates a professional PDF report for a candidate.
    This function is hardened against malformed LLM output.
    """

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name="TitleStyle",
        fontSize=18,
        spaceAfter=14,
        alignment=TA_LEFT,
    )

    section_style = ParagraphStyle(
        name="SectionStyle",
        fontSize=13,
        spaceBefore=12,
        spaceAfter=6,
        bold=True,
    )

    normal_style = styles["Normal"]

    bullet_style = ParagraphStyle(
        name="BulletStyle",
        leftIndent=12,
        spaceAfter=4,
    )

    content = []

    # -------------------------------------------------
    # Title
    # -------------------------------------------------
    content.append(Paragraph("Candidate Resume Analysis Report", title_style))
    content.append(Spacer(1, 0.2 * inch))

    # -------------------------------------------------
    # Basic Information
    # -------------------------------------------------
    content.append(Paragraph("<b>Name:</b> " + candidate_data.get("name", "N/A"), normal_style))
    content.append(Paragraph("<b>Email:</b> " + candidate_data.get("email", "N/A"), normal_style))
    content.append(Paragraph("<b>Phone:</b> " + candidate_data.get("phone", "N/A"), normal_style))
    content.append(Spacer(1, 0.15 * inch))

    # -------------------------------------------------
    # Score
    # -------------------------------------------------
    score = candidate_data.get("final_score", 0)
    content.append(Paragraph("<b>Match Score:</b> {:.2f}%".format(score), normal_style))
    content.append(Spacer(1, 0.2 * inch))

    # -------------------------------------------------
    # Matched Skills
    # -------------------------------------------------
    content.append(Paragraph("Matched Skills", section_style))

    matched_skills = candidate_data.get("matched_skills", [])
    if matched_skills:
        content.append(
            ListFlowable(
                [ListItem(Paragraph(skill, normal_style)) for skill in matched_skills],
                bulletType="bullet",
            )
        )
    else:
        content.append(Paragraph("No matched skills identified.", normal_style))

    content.append(Spacer(1, 0.2 * inch))

    # -------------------------------------------------
    # Missing Skills
    # -------------------------------------------------
    content.append(Paragraph("Missing Skills", section_style))

    missing_skills = candidate_data.get("missing_skills", [])
    if missing_skills:
        content.append(
            ListFlowable(
                [ListItem(Paragraph(skill, normal_style)) for skill in missing_skills],
                bulletType="bullet",
            )
        )
    else:
        content.append(Paragraph("No missing skills identified.", normal_style))

    content.append(Spacer(1, 0.25 * inch))

    # -------------------------------------------------
    # AI Reasoning (HARDENED)
    # -------------------------------------------------
    content.append(Paragraph("AI Skill Gap Analysis & Course Recommendations", section_style))

    reasoning = candidate_data.get("reasoning", {})

    # Defensive check: reasoning must be dict
    if isinstance(reasoning, dict) and reasoning:
        for skill, details in reasoning.items():

            # Defensive check: details must be dict
            if not isinstance(details, dict):
                continue

            related_to = details.get("related_to", "N/A")
            explanation = details.get("explanation", "No explanation available.")
            courses = details.get("courses", [])

            content.append(Spacer(1, 0.1 * inch))
            content.append(Paragraph(f"<b>{skill}</b>", normal_style))
            content.append(Paragraph(f"Related to: {related_to}", bullet_style))
            content.append(Paragraph(explanation, normal_style))

            if isinstance(courses, list) and courses:
                content.append(Paragraph("Recommended Courses:", bullet_style))
                for course in courses:
                    if not isinstance(course, dict):
                        continue
                    title = course.get("title", "Unknown Course")
                    provider = course.get("provider", "Unknown Provider")
                    content.append(
                        Paragraph(f"- {title} ({provider})", bullet_style)
                    )
    else:
        content.append(
            Paragraph(
                "AI reasoning not available or could not be generated.",
                normal_style
            )
        )

    # ----------------------------------------------s---
    # Build PDF
    # -------------------------------------------------
    doc.build(content)
