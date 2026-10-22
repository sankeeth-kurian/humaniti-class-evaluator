# 🎓 Humaniti AI – 8×8 Class Quality Evaluator

An automated, AI-powered Streamlit web application built to evaluate online class recordings using a structured 8×8 quality rubric.

## ✨ Features

- **Multi-Format Input Support:**
  - Direct file uploads (`.vtt`, `.txt`, `.mp4`, `.mp3`)
  - Google Drive shared links (with automatic large-file cookie and download handling)
  - Public video/audio direct URLs

- **Structured Rubric Scoring:**

  Evaluates classes across **Rapport & Intro**, **Student Interaction**, and other key dimensions of teaching quality.

- **Actionable Feedback:**

  Generates a final classification rating (**Excellent**, **Good**, **Average**, **Needs Improvement**) along with detailed, actionable insights.

## 🛠️ Tech Stack

- **Frontend & UI:** Python and Streamlit
- **AI Core:** Google GenAI SDK (`gemini-3.8-flash` for multimodal video & text analysis)
- **Networking & Utilities:** `requests` and `gdown` for robust file stream handling

---

## 🚀 How to Run Locally

### 1. Clone or Download the Repository

```bash
git clone <your-repository-url>
cd humaniti-class-evaluator
```

### 2. Create and Activate a Virtual Environment

**On Windows:**

```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit App

```bash
streamlit run app.py
```

### 5. Use the App

1. Open the local URL provided by Streamlit in your browser (usually [http://localhost:8501](http://localhost:8501)).
2. Enter your **Gemini API Key** in the sidebar.
3. Choose your input method (upload a file or paste a link) and click **Evaluate Class Quality!**