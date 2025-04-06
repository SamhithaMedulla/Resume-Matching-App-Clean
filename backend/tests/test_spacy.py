import spacy

# ✅ Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# ✅ Sample resume text
resume_text = """
John Doe is a Software Engineer with 5 years of experience in Python, AWS, and Machine Learning.
He has worked for Google and Microsoft. He specializes in AI, data science, and cloud computing.
"""

# ✅ Process the resume text
doc = nlp(resume_text)

# ✅ Extract skills (Organizations & Technologies)
skills = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT"]]

# ✅ Extract experience (Based on keywords like "years" and "experience")
experience = len([token for token in doc if token.text.lower() in ["years", "experience"]])

# ✅ Print results
print("Extracted Skills:", skills)
print("Years of Experience:", experience)
