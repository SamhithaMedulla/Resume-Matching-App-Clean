import requests
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

def test_huggingface_api():
    API_URL = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}
    data = {
        "inputs": {
            "source_sentence": "Sample resume text.",
            "sentences": ["Sample job description."]
        }
    }
    response = requests.post(API_URL, headers=headers, json=data)
    print("Hugging Face Response:", response.json())

if __name__ == "__main__":
    test_huggingface_api()
