# 🧠 Smart Resume Analyzer  
### AI-Powered Resume Screening using NLP, Semantic Search & LLMs

Smart Resume Analyzer is an **AI-driven Applicant Tracking System (ATS)** that automatically analyzes resumes, compares them with a job description, ranks candidates, explains skill gaps using a Large Language Model, and generates professional PDF reports — all through a clean Streamlit dashboard.

This project combines **Natural Language Processing (NLP)**, **semantic embeddings**, and **LLM reasoning** to deliver accurate, explainable, and scalable resume screening.

---

## 🚀 Key Features

- 📄 **Resume Parsing**
  - Extracts name, email, phone number, skills, and raw text from PDF resumes
- 📊 **Skill Matching & Candidate Ranking**
  - TF-IDF similarity
  - Semantic similarity using Sentence-BERT
  - Final weighted match score
- 🧠 **AI Reasoning (Gemini LLM)**
  - Explains missing skills
  - Identifies subskill relationships
  - Recommends relevant learning courses
- 📁 **Batch Resume Processing**
  - Upload multiple resumes
  - Upload ZIP folder containing resumes
- 🔎 **Live Resume Preview**
  - View extracted text of top candidate directly in the UI
- 📄 **Professional PDF Reports**
  - Auto-generated ATS-style candidate reports
  - Optional merged PDF for multiple candidates
- 🖥️ **Premium Streamlit Dashboard**
  - Multi-page navigation
  - Ranking tables
  - Progress bars
  - Download buttons

---

## 🏗️ System Architecture

Resume PDFs / ZIP
↓
Resume Parser (spaCy + PyMuPDF)
↓
Skill Matcher (TF-IDF + SBERT)
↓
LLM Reasoning (Gemini 2.5 Flash-Lite)
↓
PDF Generator (ReportLab)
↓
Streamlit Dashboard

markdown
Copy code

---

## 🧰 Tech Stack

### Frontend / UI
- **Streamlit**

### NLP & Parsing
- **spaCy** (`en_core_web_trf`, fallback: `en_core_web_md`)
- **PyMuPDF (fitz)** — PDF text extraction
- **phonenumbers** — phone normalization

### Machine Learning
- **TF-IDF** (scikit-learn)
- **Sentence-BERT** (`all-mpnet-base-v2`)
- **Cosine Similarity**

### LLM
- **Gemini 2.5 Flash-Lite**
  - Skill gap explanation
  - Course recommendations

### Reporting
- **ReportLab** — professional PDF generation

---

## 📁 Project Structure

smart-resume-analyzer/
│
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
│
├── data/
│ ├── resumes/ # Uploaded resumes (ignored in Git)
│ └── outputs/ # Generated PDF reports (ignored in Git)
│
└── modules/
├── parser.py
├── skill_matcher.py
├── llm_reasoner.py
├── pdf_generator.py
├── utils.py
└── init.py

yaml
Copy code

---

## ⚠️ Python Version Requirement (IMPORTANT)

This project **requires Python 3.10 or 3.11**.

❌ **Python 3.12 is NOT supported** due to PyMuPDF (`fitz`) incompatibility.

### ✅ Recommended
Python 3.11.x

yaml
Copy code

---

## 🔧 Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/smart-resume-analyzer.git
cd smart-resume-analyzer
2️⃣ Create virtual environment (Python 3.11)
bash
Copy code
python3.11 -m venv venv
source venv/bin/activate
3️⃣ Install dependencies
bash
Copy code
pip install -r requirements.txt
4️⃣ Download spaCy models
bash
Copy code
python -m spacy download en_core_web_trf
python -m spacy download en_core_web_md
5️⃣ (Optional) Set Gemini API Key
bash
Copy code
export GEMINI_API_KEY="your_api_key_here"
▶️ Run the Application
bash
Copy code
streamlit run app.py
Then open:

arduino
Copy code
http://localhost:8501
🧪 How It Works (Workflow)
Upload resume PDFs or ZIP folder

Paste job description

Click Analyze Candidates

System performs:

Resume parsing

Skill extraction

TF-IDF similarity

Semantic similarity

Final match score

AI reasoning (if enabled)

View ranked candidates

Preview resume text

Download professional PDF reports

📄 Output Examples
✔ Candidate match percentage

✔ Matched and missing skills

✔ AI explanation of skill gaps

✔ Course recommendations

✔ Individual and merged PDF reports

🎯 Use Cases
HR resume screening

Campus placement analysis

Internship candidate filtering

Final-year engineering project

AI / NLP portfolio project

🔮 Future Enhancements
Skill highlighting inside resume preview

Radar charts for skill visualization

Resume similarity heatmaps

Authentication & role-based access

Cloud deployment

📜 License
This project is for educational and academic use.

👨‍💻 Author
Developed as an AI + NLP project demonstrating real-world ATS automation using modern AI techniques.

⭐ If you find this project useful, please star the repository!







