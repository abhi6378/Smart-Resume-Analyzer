# app.py
import os
import streamlit as st
import pandas as pd
from io import BytesIO

from modules import parser, skill_matcher, llm_reasoner, pdf_generator, utils

# ---------------------------------------------------
# App Configuration
# ---------------------------------------------------
st.set_page_config(
    page_title="Smart Resume Analyzer",
    layout="wide",
    page_icon="🧠"
)

# ---------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------
MENU = [
    "🏠 Home",
    "📤 Upload Resumes",
    "📊 Analyze Candidates",
    "🔎 Top Candidate Preview",
    "🧠 AI Reasoning",
    "📁 Generate Reports",
    "⚙️ Settings",
]

choice = st.sidebar.selectbox("Navigate", MENU)

# ---------------------------------------------------
# Ensure directories exist
# ---------------------------------------------------
os.makedirs("data/resumes", exist_ok=True)
os.makedirs("data/outputs", exist_ok=True)

# ---------------------------------------------------
# Session State Initialization
# ---------------------------------------------------
if "resumes" not in st.session_state:
    st.session_state.resumes = []

if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = []

if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""

if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = ""

if "gemini_configured" not in st.session_state:
    st.session_state.gemini_configured = False


# ---------------------------------------------------
# PAGE: HOME
# ---------------------------------------------------
if choice == "🏠 Home":
    st.title("🧠 Smart Resume Analyzer")

    st.markdown("### 🔑 Gemini API Configuration (Required for AI Reasoning)")

    api_key = st.text_input(
        "Enter Gemini API Key",
        type="password",
        value=st.session_state.gemini_api_key,
        help="Required for skill reasoning and course recommendations"
    )

    if api_key and not st.session_state.gemini_configured:
        try:
            llm_reasoner.configure_gemini(api_key.strip())
            st.session_state.gemini_api_key = api_key.strip()
            st.session_state.gemini_configured = True
            st.success("Gemini API configured successfully ✅")
        except Exception as e:
            st.session_state.gemini_configured = False
            st.error(f"Invalid Gemini API key: {e}")

    if not st.session_state.gemini_configured:
        st.warning("⚠️ Please configure Gemini API key to continue.")
    else:
        st.success("System ready for analysis 🚀")

    st.markdown("""
    **Features Enabled**
    - Resume parsing
    - Semantic skill matching
    - AI reasoning
    - Course recommendations
    - PDF reports
    """)



# ---------------------------------------------------
# PAGE: UPLOAD RESUMES
# ---------------------------------------------------
elif choice == "📤 Upload Resumes":
    st.title("📤 Upload Resumes")

    uploaded_files = st.file_uploader(
        "Upload Resume PDFs",
        type=["pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        for f in uploaded_files:
            path = os.path.join("data/resumes", f.name)
            with open(path, "wb") as out:
                out.write(f.getbuffer())
            if path not in st.session_state.resumes:
                st.session_state.resumes.append(path)

        st.success(f"{len(uploaded_files)} resume(s) uploaded.")

    uploaded_zip = st.file_uploader(
        "Upload ZIP Folder (Multiple Resumes)",
        type=["zip"]
    )

    if uploaded_zip:
        import zipfile
        with zipfile.ZipFile(BytesIO(uploaded_zip.getvalue()), "r") as z:
            z.extractall("data/resumes")

        for file in os.listdir("data/resumes"):
            if file.lower().endswith(".pdf"):
                full_path = os.path.join("data/resumes", file)
                if full_path not in st.session_state.resumes:
                    st.session_state.resumes.append(full_path)

        st.success("ZIP file extracted and resumes added.")

    st.subheader("📄 Uploaded Resumes")
    if st.session_state.resumes:
        for r in st.session_state.resumes:
            st.write("•", os.path.basename(r))
    else:
        st.info("No resumes uploaded yet.")


# ---------------------------------------------------
# PAGE: ANALYZE CANDIDATES
# ---------------------------------------------------
if not st.session_state.gemini_configured:
    st.error("Gemini API key not configured. Please go to Home page.")
    st.stop()

elif choice == "📊 Analyze Candidates":
    st.title("📊 Analyze Candidates")

    jd_text = st.text_area(
        "Paste Job Description",
        value=st.session_state.jd_text,
        height=200
    )
    st.session_state.jd_text = jd_text

    semantic_weight = st.slider(
       "Semantic Weight (Higher = More Accurate)",
        0.5, 1.0, 0.85, 0.05
)


    if st.button("▶️ Run Analysis"):
        if not st.session_state.resumes:
            st.error("Upload resumes first.")
        elif not jd_text.strip():
            st.error("Paste a job description.")
        else:
            st.info("Analyzing resumes...")
            results = []
            progress = st.progress(0)
            total = len(st.session_state.resumes)

            for i, resume_path in enumerate(st.session_state.resumes):
                parsed = parser.parse_resume(
                    resume_path,
                    utils.SKILL_LIST,
                    use_semantic=True
                )

                resume_text = parsed["raw_text"]
                resume_skills = parsed["skills"]
                jd_skills = parser.extract_skills_from_text(jd_text, utils.SKILL_LIST)

                eval_result = skill_matcher.evaluate_candidate(
                    resume_text,
                    resume_skills,
                    jd_text,
                    jd_skills
                )

                final_score = (
                    (1 - semantic_weight) * eval_result["tfidf_score"]
                    + semantic_weight * eval_result["semantic_score"]
                ) * 100

                matched = eval_result["matched_skills"]
                missing = eval_result["missing_skills"]

                reasoning = {}
                if missing:
                    reasoning = llm_reasoner.get_skill_reasoning(
                       matched_skills=matched,
                       missing_skills=missing
                    )

                name = parsed["name"] or os.path.basename(resume_path)
                pdf_path = os.path.join(
                    "data/outputs",
                    f"{name.replace(' ', '_')}.pdf"
                )

                pdf_generator.generate_candidate_report({
                    "name": name,
                    "email": parsed.get("email", ""),
                    "phone": parsed.get("phone", ""),
                    "final_score": round(final_score, 2),
                    "matched_skills": matched,
                    "missing_skills": missing,
                    "reasoning": reasoning
                }, pdf_path)

                results.append({
                    "name": name,
                    "email": parsed.get("email"),
                    "phone": parsed.get("phone"),
                    "resume_path": resume_path,
                    "final_score": round(final_score, 2),
                    "matched_skills": matched,
                    "missing_skills": missing,
                    "reasoning": reasoning,
                    "report_path": pdf_path
                })

                progress.progress((i + 1) / total)

            st.session_state.analysis_results = results
            st.success("Analysis complete!")

    if st.session_state.analysis_results:
        df = pd.DataFrame([
            {
                "Name": r["name"],
                "Score (%)": r["final_score"],
                "Matched": len(r["matched_skills"]),
                "Missing": len(r["missing_skills"])
            }
            for r in st.session_state.analysis_results
        ]).sort_values(by="Score (%)", ascending=False)

        st.subheader("📊 Candidate Ranking")
        st.dataframe(df, use_container_width=True)


# ---------------------------------------------------
# PAGE: TOP CANDIDATE PREVIEW
# ---------------------------------------------------
elif choice == "🔎 Top Candidate Preview":
    st.title("🔎 Top Candidate Resume Preview")

    if not st.session_state.analysis_results:
        st.info("Run analysis first.")
    else:
        top = sorted(
            st.session_state.analysis_results,
            key=lambda x: x["final_score"],
            reverse=True
        )[0]

        text = parser.extract_text_from_pdf(top["resume_path"])
        preview = text[:1500] + ("..." if len(text) > 1500 else "")

        st.subheader(f"{top['name']} — {top['final_score']}%")
        with st.expander("View Resume Text"):
            st.text_area("Resume Preview", preview, height=350)


# ---------------------------------------------------
# PAGE: AI REASONING
# ---------------------------------------------------
elif choice == "🧠 AI Reasoning":
    st.title("🧠 AI Reasoning")

    if not st.session_state.analysis_results:
        st.info("Run analysis first.")
    else:
        for r in st.session_state.analysis_results:
            st.subheader(f"{r['name']} — {r['final_score']}%")
            if r["reasoning"]:
                st.json(r["reasoning"])
            else:
                st.write("No reasoning available.")


# ---------------------------------------------------
# PAGE: GENERATE REPORTS
# ---------------------------------------------------
elif choice == "📁 Generate Reports":
    st.title("📁 Download Reports")

    for r in st.session_state.analysis_results:
        with open(r["report_path"], "rb") as f:
            st.download_button(
                f"Download {r['name']} PDF",
                f,
                file_name=os.path.basename(r["report_path"])
            )


# ---------------------------------------------------
# PAGE: SETTINGS (FRONTEND API KEY ONLY)
# ---------------------------------------------------
elif choice == "⚙️ Settings":
    st.title("⚙️ Settings")

    st.info("Enter Gemini API key to enable AI reasoning and course recommendations.")

    api_key = st.text_input(
        "Gemini API Key",
        type="password",
        value=st.session_state.gemini_api_key
    )

    if st.button("Configure Gemini"):
        if not api_key.strip():
            st.error("API key cannot be empty.")
        else:
            try:
                llm_reasoner.configure_gemini(api_key.strip())
                st.session_state.gemini_api_key = api_key.strip()
                st.session_state.gemini_configured = True
                st.success("Gemini configured successfully!")
            except Exception as e:
                st.session_state.gemini_configured = False
                st.error(f"Configuration failed: {e}")
