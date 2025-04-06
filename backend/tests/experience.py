from io import BytesIO
from pdfminer.high_level import extract_text
from docx import Document
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to extract text from resume file
def extract_text_from_file(file_path):
    try:
        logger.info(f"Extracting text from file: {file_path}")
        if file_path.endswith(".pdf"):
            return extract_text(file_path)
        elif file_path.endswith(".docx"):
            doc = Document(file_path)
            return "\n".join([para.text for para in doc.paragraphs])
        else:
            logger.error("Unsupported file format. Please use PDF or DOCX.")
            return None
    except Exception as e:
        logger.error(f"❌ Error extracting text: {e}")
        return None

# Function to extract experience section

def extract_work_experience(text):
    try:
        logger.info("Extracting work experience section...")
        # Keywords for identifying the work experience section
        work_experience_keywords = ["Work Experience", "Professional Experience", "Employment History", "Career History"]
        stop_keywords = ["Education", "Skills", "Certifications", "Projects", "Summary"]
        work_experience_text = ""

        # Split the text into lines
        lines = text.split("\n")
        for i, line in enumerate(lines):
            # Match the heading of the work experience section
            if any(keyword.lower() in line.lower() for keyword in work_experience_keywords):
                logger.info(f"Work experience section found: {line}")

                # Collect subsequent lines until a stopping keyword or empty line
                for subsequent_line in lines[i + 1:]:
                    if any(keyword.lower() in subsequent_line.lower() for keyword in stop_keywords):
                        break
                    # Allow for blank lines but trim unnecessary whitespace
                    work_experience_text += subsequent_line.strip() + "\n"
                break

        if not work_experience_text.strip():
            logger.warning("No content found under the 'Work Experience' section heading.")
        return work_experience_text.strip() if work_experience_text else "Work experience section not found."
    except Exception as e:
        logger.error(f"❌ Error extracting work experience section: {e}")
        return "Error extracting work experience section."

# Test the function with a real file
file_path = r"C:\Users\samhi\OneDrive\Documents\flask-project\backend\uploads\Samhitha_Medulla_Resume.pdf"
resume_text = extract_text_from_file(file_path)

if resume_text:
    experience_section = extract_work_experience(resume_text)
    print("Extracted Work Experience Section:")
    print(experience_section)
else:
    logger.error("Failed to extract resume text.")


