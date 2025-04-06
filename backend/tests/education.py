from io import BytesIO
from pdfminer.high_level import extract_text
from docx import Document
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to extract text from a resume file (PDF or DOCX)
def extract_text_from_file(file_path):
    try:
        logger.info(f"Extracting text from file: {file_path}")
        if file_path.endswith(".pdf"):
            return extract_text(file_path)
        elif file_path.endswith(".docx"):
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            logger.error(f"Unsupported file format for file: {file_path}")
            return None
    except Exception as e:
        logger.error(f"❌ Error extracting text: {e}")
        return None

# Function to preprocess text (clean up formatting issues)
def preprocess_text(raw_text):
    return "\n".join(line.strip() for line in raw_text.splitlines() if line.strip())

# Function to extract the education section
def extract_education(text):
    try:
        logger.info("Extracting education section...")
        education_keywords = ["Education", "Qualifications", "Academic Background", "Degree", "Diploma"]
        education_text = ""

        # Split text into lines
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if any(keyword.lower() in line.lower() for keyword in education_keywords):
                logger.info(f"Education section found: {line}")
                # Capture inline content if present
                if ":" in line:
                    education_text += line.split(":", 1)[1].strip() + "\n"
                # Gather subsequent lines until a new section heading or empty line
                for subsequent_line in lines[i + 1:]:
                    if subsequent_line.strip() == "" or any(keyword.lower() in subsequent_line.lower() for keyword in ["Experience", "Skills", "Certifications"]):
                        break
                    education_text += subsequent_line.strip() + "\n"
                break

        if not education_text.strip():
            logger.warning("No content found under the 'Education' section heading.")
        return education_text.strip() if education_text else "Education section not found."
    except Exception as e:
        logger.error(f"❌ Error extracting education: {e}")
        return "Error extracting education section."

# Main script
if __name__ == "__main__":
    # Provide the file path to the resume
    file_path = r"C:\Users\samhi\OneDrive\Documents\flask-project\backend\uploads\Samhitha_Medulla_Resume.pdf"

    # Extract and preprocess the text
    resume_text = extract_text_from_file(file_path)
    if resume_text:
        resume_text = preprocess_text(resume_text)
        # Extract education section
        education_section = extract_education(resume_text)
        print("Extracted Education Section:")
        print(education_section)
    else:
        logger.error("Failed to extract resume text.")

