import spacy
from skillNer.skill_extractor_class import SkillExtractor
from skillNer.general_params import SKILL_DB
from spacy.matcher import PhraseMatcher

# ✅ Load spaCy model with better accuracy
nlp = spacy.load("en_core_web_lg")

# ✅ Initialize PhraseMatcher
phrase_matcher = PhraseMatcher(nlp.vocab)

# ✅ Initialize Skill Extractor with Correct Parameters
skill_extractor = SkillExtractor(nlp, SKILL_DB, phrase_matcher)

# ✅ Test Job Description (Dynamic Extraction)
job_description = """
What This Role Requires: 

1-4 years of experience in software development using Java after your degree.
Must have Java or C# experience (one or the other).
Should understand basics of OOP (Object Oriented Programming) concepts.
Hands-on experience in XML, SQL, JavaScript, CSS, jQuery, HTML, or JSON preferred.
Familiarity with version control systems like Git.
Eagerness to learn and adapt to new technologies, frameworks, and best practices in the rapidly evolving Android ecosystem.
Basic understanding of computer science concepts like data structures, algorithms, software architecture, and design patterns.

To Qualify: 

You should be willing to relocate anywhere in the US on a client project-to-project basis, as this is an onsite, in-office position.
Strong English communication skills, both written and verbal.
Bachelor’s Degree in Computer Science, Information Systems, Electrical Engineering,
Mathematics, or a related quantitative field.
"""

# ✅ Extract Skills from Job Description
annotations = skill_extractor.annotate(job_description)

# ✅ Extract Exact Matches
extracted_skills = {skill['skill_name'] for skill in annotations['results']['full_matches']}

# ✅ Extract Contextual Skills (More Dynamic)
contextual_skills = {skill['skill_name'] for skill in annotations['results']['ngram_scored']}

# ✅ Merge Both Exact & Contextual Skills
final_extracted_skills = extracted_skills.union(contextual_skills)

# ✅ Filter out non-technical words (Ensures only actual skills are kept)
technical_skills = {skill for skill in final_extracted_skills if len(skill) > 2}  # Remove short words

print("🔍 Extracted Skills:", technical_skills)








