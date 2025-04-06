import pandas as pd
import re

# Load the RoleSkills.csv file which contains the technical skills
skills_df = pd.read_csv('RoleSkills.csv')

# Strip any leading/trailing spaces from column names
skills_df.columns = skills_df.columns.str.strip()

# Use the correct column name 'Skills' for technical skills
skills_list = skills_df['Skills'].dropna().tolist()

# Split the skills by commas and clean up extra spaces
skills_list = [skill.strip() for skills in skills_list for skill in skills.split(',')]

# Sample job description (this should be replaced with actual input)
job_description = """
Responsibilities:

Primary responsibilities include developing monitoring solutions, troubleshooting/debugging and implementing the fix for internally developed code (Perl, C/C++, JAVA).
Performing SQL queries, improving our systems that gather metrics on our features, updating, tracking and resolving technical challenges. 
Responsibilities also include working alongside development on Corporate and Divisional Software projects, updating/enhancing our current software, automation of support processes and documentation of our systems. 

Job Qualifications:

The ideal candidate is interested in a career in software development and is looking to utilize and expand their coding skills and gain exposure to a wide variety of software applications. 
They must be detail oriented, have superior verbal and written communication skills, strong organizational skills, are able to work independently and can maintain professionalism under pressure. 

Preferred coding skills: 

Perl, C/C++ and/or Java. 
Other desired technical skills include Mason, Perl CGI, Oracle SQL, HTML, UNIX/LINUX. 
A Computer Science or equivalent technical degree and 2-5 years of relevant experience is required.

"""

# Function to extract skills from job description
def extract_skills(description, skills):
    # Convert description to lowercase for case-insensitive matching
    description_lower = description.lower()

    # Use regular expressions to match full skills (not partial matches)
    extracted_skills = set()  # Use a set to avoid duplicates
    for skill in skills:
        if re.search(r'\b' + re.escape(skill.lower()) + r'\b', description_lower):
            extracted_skills.add(skill)  # Add skill to set (ensures no duplicates)
    
    return list(extracted_skills)

# Extract skills from the job description
extracted_skills = extract_skills(job_description, skills_list)

# Print the extracted skills
print("Extracted Skills:", extracted_skills)
