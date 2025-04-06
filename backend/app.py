from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from sentence_transformers import SentenceTransformer, util
from fastapi.middleware.cors import CORSMiddleware
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import List
from datetime import datetime
from fuzzywuzzy import fuzz, process
from dateutil import parser
from collections import Counter
from pydantic import BaseModel
import nltk
from nltk.corpus import stopwords
import spacy
import pymongo
import os
import requests
from bson import ObjectId
from dotenv import load_dotenv
from io import BytesIO
from pdfminer.high_level import extract_text
from docx import Document
import logging
import re
import torch
import json
import string
import numpy as np
import pandas as pd



# ✅ Load environment variables
load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# ✅ Initialize FastAPI app
app = FastAPI()


# ✅ CORS setup (only once!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Load NLP model
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("✅ NLP model loaded successfully!")
except Exception as e:
    logger.error(f"❌ Failed to load NLP model: {e}")
    raise HTTPException(status_code=500, detail="Failed to load NLP model")
nltk.download("stopwords")
common_words = set(stopwords.words("english"))


# ✅ MongoDB setup
try:
    client = pymongo.MongoClient(MONGODB_URI)
    db = client["resume_screening"]
    resumes_collection = db["resumes"]
    jobs_collection = db["jobs"]
    logger.info("✅ Connected to MongoDB successfully!")
except Exception as e:
    logger.error(f"❌ MongoDB Connection Failed: {e}")
    raise HTTPException(status_code=500, detail="Failed to connect to database")

# ✅ Helper: Extract Text from Resume
def extract_text_from_resume(file_bytes: bytes, filename: str):
    try:
        file_stream = BytesIO(file_bytes)
        if filename.endswith(".pdf"):
            # For PDF files, use pdfminer to extract text
            return extract_text(file_stream)
        elif filename.endswith(".docx"):
            # For DOCX files, use python-docx to extract text
            doc = Document(file_stream)
            return "\n".join([para.text for para in doc.paragraphs])
        return None  # Return None if the file format is unsupported
    except Exception as e:
        logger.error(f"❌ Error extracting text: {e}")
        return None


def extract_work_experience(text):
    """Extracts total years of work experience from resume text."""
    try:
        # Regex pattern to capture date ranges, handling different dash styles
        date_range_pattern = r"(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[ ]\d{4})\s*[-–]\s*(\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[ ]\d{4})"
        date_matches = re.findall(date_range_pattern, text)

        total_months = 0

        for start_date, end_date in date_matches:
            try:
                start = parser.parse(start_date, fuzzy=True)
                end = parser.parse(end_date, fuzzy=True)

                # Ensure start date is before end date
                if start > end:
                    continue  

                # Calculate duration in months
                months = (end.year - start.year) * 12 + (end.month - start.month) + 1  # +1 to count the last month
                total_months += max(0, months)  # Ensure non-negative values
            except Exception as e:
                print(f"⚠️ Error parsing dates: {e}")

        # Convert months to years
        total_years = round(total_months / 12, 1)  # One decimal precision

        return total_years

    except Exception as e:
        print(f"❌ Error extracting work experience: {e}")

    return 0  # Default to 0 if extraction fails


# ✅ Helper: Extract Education
# ✅ Helper: Extract Education Section Properly
def extract_education(text):
    try:
        education_keywords = ["Education", "Academic Background", "Degrees", "Certifications"]
        stop_keywords = ["Experience", "Work", "Projects", "Technical Skills", "Summary"]

        education_text = []
        capture = False
        lines = text.split("\n")

        for line in lines:
            if any(keyword.lower() in line.lower() for keyword in education_keywords):
                capture = True
                continue  # Skip the header itself
            elif any(keyword.lower() in line.lower() for keyword in stop_keywords) and capture:
                break  # Stop capturing when another section starts
            if capture:
                education_text.append(line.strip())

        # ✅ Ensure valid extraction
        if not education_text:
            logger.warning("⚠ No education section found.")
            return "Education section not found in resume."

        return "\n".join(education_text).strip()

    except Exception as e:
        logger.error(f"❌ Error extracting education: {e}")
        return "Error extracting education."

# ✅ Helper: Extract Skills
logger = logging.getLogger(__name__)

# ✅ Extract Skills from Resumes 
def extract_skills(text):
    try:
        logger.info("Extracting only 'Technical Skills' section...")

        skills_section = []
        capture = False
        lines = text.split("\n")

        for line in lines:
            line = line.strip()

            # ✅ Start capturing when 'Technical Skills' or similar sections are found
            if re.search(r"\b(technical skills|skills|technologies|expertise|proficiencies)\b", line, re.IGNORECASE):
                capture = True
                skills_section = []  # ✅ Reset to ensure previous summary is not included
                continue  
            elif capture:
                # ✅ Stop capturing when reaching another section
                if re.search(r"\b(work experience|education|projects|certifications|summary|professional experience|employment history)\b", line, re.IGNORECASE):
                    break  
                skills_section.append(line)

        if not skills_section:
            logger.warning("No skills section found.")
            return ["No skills found"]

        # ✅ Extract individual skills, remove unwanted headers
        extracted_skills = re.split(r",|\s-\s|\n|•", " ".join(skills_section))
        extracted_skills = [skill.strip() for skill in extracted_skills if skill.strip() and not re.search(r"\b(technical skills|skills|technologies|proficiencies|expertise)\b", skill, re.IGNORECASE)]

        # ✅ Trim the first two unwanted lines if necessary
        if len(extracted_skills) > 2:
            extracted_skills = extracted_skills[2:]

        return extracted_skills if extracted_skills else ["No skills found"]

    except Exception as e:
        logger.error(f"❌ Error extracting skills: {e}")
        return ["Error extracting skills"]


# Load the RoleSkills.csv file which contains the technical skills
skills_df = pd.read_csv('RoleSkills.csv')

# Strip any leading/trailing spaces from column names
skills_df.columns = skills_df.columns.str.strip()

# Use the correct column name 'Skills' for technical skills
skills_list = skills_df['Skills'].dropna().tolist()

# Split the skills by commas and clean up extra spaces, and ensure there are no empty strings
skills_list = [skill.strip() for skills in skills_list for skill in skills.split(',') if skill.strip()]

def extract_job_skills(description: str, skills: List[str]) -> List[str]:
    """
    Extract skills from the job description based on a list of predefined skills.
    
    Args:
        description (str): Job description text.
        skills (List[str]): List of technical skills to look for.

    Returns:
        List[str]: Extracted skills from the job description.
    """
    # Convert description to lowercase for case-insensitive matching
    description_lower = description.lower()

    # Use regular expressions to match full skills (not partial matches)
    extracted_skills = set()  # Use a set to avoid duplicates
    for skill in skills:
        if re.search(r'\b' + re.escape(skill.lower()) + r'\b', description_lower):
            extracted_skills.add(skill)  # Add skill to set (ensures no duplicates)
    
    return list(extracted_skills)


# ✅ Helper: Extract Experience from Text
def extract_experience(description: str) -> int:
    """
    Extracts required years of experience from job description using regex.
    Example: "At least 3+ years of experience in Python" → Extracts 3
    
    Args:
        description (str): Job description text.
    
    Returns:
        int: Extracted years of experience or 0 if not found.
    """
    match = re.search(r"(\d+)\+?\s*years?", description, re.IGNORECASE)
    if match:
        return int(match.group(1))  # Extracted years
    return 0  # Default if no experience found


# ✅ Improved Skill Matching Function
def compare_skills(job_skills, resume_skills):
    """
    Uses fuzzy matching to compare extracted job skills with resume skills.
    """
    job_skills_set = set(job_skills)
    resume_skills_set = set(resume_skills)

    matched_skills = set()
    missing_skills = set(job_skills_set)

    for job_skill in job_skills_set:
        best_match = process.extractOne(job_skill, resume_skills_set, scorer=fuzz.token_sort_ratio)
        
        if best_match and best_match[1] > 80:  # ✅ Adjusted fuzzy threshold for better matching
            matched_skills.add(job_skill)
            missing_skills.discard(job_skill)

    logger.info(f"✅ Matched Skills: {matched_skills}")
    logger.info(f"❌ Missing Skills: {missing_skills}")

    return list(missing_skills), list(matched_skills)

# ✅ Compute Match Percentage
def calculate_final_match_percentage(matched_skills, job_skills, candidate_experience, required_experience):
    """
    Calculates final match % by combining:
    - Skill match percentage
    - Experience penalty (if below required)
    - Small experience bonus (if equal or above)
    """
    if len(job_skills) == 0:
        return 0.0  # Prevent division by zero

    skill_match_percentage = round((len(matched_skills) / len(job_skills)) * 100, 2)

    # ✅ Experience-Based Adjustment
    if candidate_experience < required_experience:
        experience_penalty = (required_experience - candidate_experience) * 2  # -2% per missing year
        final_score = max(skill_match_percentage - experience_penalty, 0)  # Prevent going below 0%
    elif candidate_experience >= required_experience:
        experience_bonus = min((candidate_experience - required_experience) * 1, 5)  # Max +5% bonus
        final_score = min(skill_match_percentage + experience_bonus, 100)  # Prevent going above 100%
    else:
        final_score = skill_match_percentage  # No change if experience matches exactly

    return round(final_score, 2)

def process_resume(uploaded_file, filename):
    """
    Processes the uploaded resume and extracts text based on the file.
    """
    try:
        # Read the resume file bytes
        file_bytes = uploaded_file.read()

        # Extract text from the resume using filename
        extracted_text = extract_text_from_resume(file_bytes, filename)
        
        if not extracted_text:
            logger.warning(f"❌ No text extracted from the resume: {filename}")
            return []  # Return an empty list if text extraction fails

        # Add the filename and extracted text to the resume data
        logger.info(f"✅ Successfully processed resume: {filename}")
        return [{
            "filename": filename,
            "text": extracted_text
        }]
    
    except Exception as e:
        logger.error(f"❌ Error processing resume {filename}: {e}")
        return []


def rank_candidates(job_description, resumes, skills_list):
    try:
        job_skills = extract_job_skills(job_description, skills_list)
        required_experience = extract_experience(job_description) or 0
        logger.info(f"Job Skills Extracted: {job_skills}, Required Experience: {required_experience}")

        ranked_candidates = []

        for resume in resumes:
            resume_filename = resume.get("filename", "Unknown Filename")
            logger.info(f"Processing resume: {resume_filename}")

            extracted_resume_skills = extract_skills(resume.get("text", ""))
            candidate_experience = extract_work_experience(resume.get("text", "")) or 0
            candidate_education = resume.get("education", "Education not provided")

            if not extracted_resume_skills:
                logger.warning(f"❌ No skills found in resume {resume_filename}")
                missing_skills = job_skills
                matched_skills = []
            else:
                missing_skills, matched_skills = compare_skills(job_skills, extracted_resume_skills)

            match_percentage = float(calculate_final_match_percentage(matched_skills, job_skills, candidate_experience, required_experience))
            feedback = generate_feedback(missing_skills, matched_skills, candidate_experience, required_experience)

            ranked_candidates.append({
                "filename": resume_filename,
                "skills": extracted_resume_skills,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "candidate_experience": candidate_experience,
                "required_experience": required_experience,
                "education": candidate_education,
                "match_percentage": match_percentage,
                "feedback": feedback
            })

        ranked_candidates.sort(key=lambda x: float(x["match_percentage"]), reverse=True)
        return ranked_candidates

    except Exception as e:
        logger.error(f"❌ Error in ranking candidates: {type(e).__name__} - {str(e)}", exc_info=True)
        raise Exception(f"Error in ranking candidates: {type(e).__name__} - {str(e)}")


def generate_feedback(missing_skills, matched_skills, candidate_experience, required_experience):
    """
    Generates feedback based on:
    - Missing skills
    - Matched skills
    - Experience comparison
    """
    feedback = []

    if missing_skills:
        feedback.append(f"Missing skills: {', '.join(missing_skills)}")
    else:
        feedback.append("All required skills are present.")

    if candidate_experience < required_experience:
        feedback.append(f"Experience is {required_experience - candidate_experience} years below the required experience.")
    elif candidate_experience >= required_experience:
        feedback.append(f"Experience exceeds the required experience by {candidate_experience - required_experience} years.")

    if matched_skills:
        feedback.append(f"Matched skills: {', '.join(matched_skills)}")
    else:
        feedback.append("No skills matched.")

    return " | ".join(feedback)



# ✅ Helper: Validate ObjectId
def validate_objectid(id_str):
    if not ObjectId.is_valid(id_str.strip()):
        raise HTTPException(status_code=400, detail=f"{id_str} is not a valid ObjectId")
    return ObjectId(id_str)

# ✅ API: Add Job Description
class JobDescription(BaseModel):
    job_title: str
    job_description: str

# In-memory storage for job descriptions and associated skills
job_descriptions = {}


@app.post("/add_job/")
async def add_job(job: JobDescription):
    try:
        job_data = job.dict()

        # ✅ Extract skills from job description
        extracted_skills = extract_job_skills(job_data["job_description"], skills_list)
        job_data["extracted_skills"] = extracted_skills  # Store extracted skills in MongoDB

        # ✅ Extract experience from job description
        experience_years = extract_experience(job_data["job_description"])
        job_data["experience_years"] = experience_years  # Store experience in MongoDB

        # ✅ Insert into MongoDB
        inserted_job = jobs_collection.insert_one(job_data)  
        job_id = inserted_job.inserted_id  

        # ✅ Log and Print Job Data
        logger.info(f"✅ Job inserted successfully! Job ID: {job_id}, Experience: {experience_years}")
        print(f"✅ Job inserted successfully! Job ID: {job_id}, Experience: {experience_years}")

        return {
            "message": "Job added successfully!",
            "job_id": str(job_id),
            "extracted_skills": extracted_skills,
            "experience_years": experience_years
        }

    except Exception as e:
        logger.error(f"❌ Error adding job: {e}")
        raise HTTPException(status_code=500, detail=f"Error adding job: {str(e)}")

# ✅ API: Upload Resume
@app.post("/upload_resume/{job_id}")
async def upload_resume(job_id: str, file: UploadFile = File(...)):
    """
    Endpoint to upload a resume, extract key sections, and store it in MongoDB.
    """
    try:
        # ✅ Validate job_id
        job_id = validate_objectid(job_id)

        # ✅ Read and validate the file
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Empty or unsupported file format")
        if not file.filename.endswith(('.pdf', '.docx')):
            raise HTTPException(status_code=400, detail="Unsupported file format")

        # ✅ Extract text from resume
        extracted_text = extract_text_from_resume(file_bytes, file.filename)
        if not extracted_text:
            raise HTTPException(status_code=400, detail="Could not extract text from the resume")

        # ✅ Extract different sections
        extracted_skills = extract_skills(extracted_text)  # Extract only the 'Skills' section
        extracted_work_experience = extract_work_experience(extracted_text)  # Extract experience
        extracted_education = extract_education(extracted_text)  # Extract education

        # ✅ Store extracted details in MongoDB
        resume_data = {
            "job_id": str(job_id),
            "filename": file.filename,
            "text": extracted_text,
            "skills": extracted_skills,
            "work_experience": extracted_work_experience,
            "education": extracted_education
        }
        resume_id = resumes_collection.insert_one(resume_data).inserted_id

        return {
            "message": "Resume uploaded successfully!",
            "resume_id": str(resume_id),
            "extracted_data": {
                "skills": extracted_skills,
                "work_experience": extracted_work_experience,
                "education": extracted_education
            }
        }

    except Exception as e:
        logger.error(f"❌ Error uploading resume: {e}")
        raise HTTPException(status_code=500, detail=f"Error uploading resume: {str(e)}")


@app.get("/get_ranked_candidates_with_feedback/{job_id}")
async def get_ranked_candidates_with_feedback(job_id: str):
    try:
        job_id = ObjectId(job_id)
        job = jobs_collection.find_one({"_id": job_id})
        if not job:
            raise HTTPException(status_code=404, detail="Job not found.")

        resumes = list(resumes_collection.find({"job_id": str(job_id)}))
        if not resumes:
            return {"message": "No resumes uploaded for this job."}

        extracted_job_skills = extract_job_skills(job["job_description"], skills_list)
        required_experience = extract_experience(job["job_description"])

        resume_data = []
        for resume in resumes:
            filename = resume.get("filename", "Unknown Filename")
            if filename == "Unknown Filename":
                logging.warning(f"❌ Missing filename for resume with job_id: {job_id}")
            logging.info(f"Processing resume: {filename}")

            extracted_text = resume.get("text", "")
            if not extracted_text:
                logging.warning(f"❌ Resume text is missing for resume with job_id: {job_id} and filename: {filename}")
                continue

            extracted_resume_skills = extract_skills(extracted_text)
            candidate_experience = extract_work_experience(extracted_text)
            candidate_education = extract_education(extracted_text)

            resume_data.append({
                "filename": filename,
                "text": extracted_text,
                "skills": extracted_resume_skills,
                "experience": candidate_experience,
                "education": candidate_education
            })

        logging.info(f"Resume Data Prepared: {len(resume_data)} resumes.")
        for candidate in resume_data:
            logging.info(f"Resume Data for Ranking: {candidate}")

        ranked_candidates = rank_candidates(job["job_description"], resume_data, skills_list)

        response = {
            "extracted_job_skills": extracted_job_skills,
            "ranked_candidates": [
                {
                    "resume": candidate["filename"],
                    "extracted_resume_skills": candidate["skills"],
                    "matched_skills": candidate["matched_skills"],
                    "missing_skills": candidate["missing_skills"],
                    "candidate_experience": candidate["candidate_experience"],
                    "candidate_education": candidate["education"],
                    "required_experience": required_experience,
                    "overall_match_percentage": candidate["match_percentage"],
                    "feedback": candidate["feedback"]
                }
                for candidate in ranked_candidates
            ]
        }

        return response

    except Exception as e:
        logging.error(f"❌ Error ranking candidates: {type(e).__name__} - {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error ranking candidates: {type(e).__name__} - {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, debug=True)
