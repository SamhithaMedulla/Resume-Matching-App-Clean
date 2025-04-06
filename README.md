## 🧠 Resume Matching App — FastAPI + React

Welcome to the **Resume Matching App** — a full-stack application designed to match resumes with job descriptions using intelligent skill extraction and fuzzy logic-based scoring.

---

### 🚀 Features

- 📄 Upload job descriptions and resumes (PDF/DOCX)
- 🧠 Extracts key details from resumes — skills, experience, education
- 🔍 Matches resumes to job descriptions using NLP + fuzzy matching
- 📊 Ranks candidates based on match percentage and feedback
- 💬 Highlights missing and matched skills + experience alignment

---

### ⚙️ Tech Stack

| Layer      | Technologies |
|------------|--------------|
| **Frontend** | ReactJS, Axios |
| **Backend**  | FastAPI (Python), NLP (spaCy, fuzzywuzzy, NLTK), PDF/DOCX parsing |
| **Database** | MongoDB (via MongoDB Atlas) |
| **Other**    | Pandas, dotenv, SentenceTransformers |

---

### 📦 How to Run the App Locally

> 🐍 Make sure Python 3.8+ and Node.js are installed.

#### 🔧 Backend (FastAPI)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
uvicorn app:app --reload
```

#### 💻 Frontend (React)

```bash
cd resume-matching-frontend/job-resume-matcher
npm install
npm start
```

---

### 📁 File Uploads

- Supports `.pdf` and `.docx` formats
- Automatically extracts text and parses sections

---

### 💡 Future Improvements

- Deploy as a cloud app (Azure/GCP)
- UI improvements with filtering/sorting
- Admin panel for managing jobs/resumes
- Integration with HuggingFace for enhanced NLP

---

### 📌 Screenshots (Optional)
> _Add UI screenshots here later for visual impact!_

---

### 🤝 Let's Connect

Feel free to fork, explore, and share feedback!  
Built with 💙 by [@SamhithaMedulla](https://github.com/SamhithaMedulla)

---

### 🔗 Project Repository

👉 [GitHub Repo](https://github.com/SamhithaMedulla/Resume-Matching-App-Clean)
