from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client["resume_screening"]
collection = db["resumes"]

# Test inserting a document
result = collection.insert_one({"test": "connection successful"})
print(f"Inserted document ID: {str(result.inserted_id)}")

