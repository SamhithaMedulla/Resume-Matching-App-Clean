# Import required modules
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Experience extraction function
def extract_experience(text):
    try:
        matches = re.findall(r'(\d+)\s*\+?\s*(?:years?|yrs?)|(\b(?:one|two|three|four|five|six|seven|eight|nine|ten)\b)\s*(?:years?|yrs?)', text, re.IGNORECASE)
        experience_years = []
        word_to_num = {
            "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
            "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
        }
        for match in matches:
            if match[0]:  # Numeric match
                experience_years.append(int(match[0]))
            elif match[1]:  # Word-based match
                experience_years.append(word_to_num.get(match[1].lower(), 0))
        return max(experience_years) if experience_years else 0
    except Exception as e:
        logger.error(f"Error extracting experience: {e}")
        return 0

# Education extraction function
def extract_education(text):
    try:
        education_keywords = [
            "Bachelor", "Master", "PhD", "B.Sc", "M.Sc", "B.Tech", "M.Tech",
            "B.E", "M.E", "MBA", "Doctorate"
        ]
        education_matches = re.findall(r'([^.]*?\b(?:' + '|'.join(education_keywords) + r')\b[^.]*)', text, re.IGNORECASE)
        return " | ".join(education_matches) if education_matches else "Not found"
    except Exception as e:
        logger.error(f"Error extracting education: {e}")
        return "Not found"

# Feedback generation function
def generate_feedback(skills, job_description, similarity_score):
    job_keywords = set(job_description.lower().split())
    matched_skills = [skill for skill in skills if skill.lower() in job_keywords]
    missing_skills = job_keywords - set(skill.lower() for skill in skills)

    feedback = {
        "strengths": f"Matched skills: {', '.join(matched_skills)}" if matched_skills else "No skills matched.",
        "improvements": f"Missing skills: {', '.join(missing_skills)}." if missing_skills else "No missing skills.",
        "match_score": f"Similarity score: {similarity_score:.2f}%."
    }
    return feedback

# Test cases for each function
if __name__ == "__main__":
    # Sample inputs
    sample_text = """
    John has over five years of experience in Python development and three years of experience in AWS and Docker.
    He graduated with a Bachelor of Science in Computer Science and an MBA in Technology Management.
    """
    job_description = "Python, Docker, AWS, SQL experience required"
    skills = ["Python", "Docker", "AWS"]

    # Test experience extraction
    print("Testing Experience Extraction:")
    experience = extract_experience(sample_text)
    print(f"Extracted Experience: {experience} years\n")

    # Test education extraction
    print("Testing Education Extraction:")
    education = extract_education(sample_text)
    print(f"Extracted Education: {education}\n")

    # Test feedback generation
    print("Testing Feedback Generation:")
    similarity_score = 75.43  # Example similarity score
    feedback = generate_feedback(skills, job_description, similarity_score)
    print(f"Feedback: {feedback}\n")
