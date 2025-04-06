import requests
import os
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Get API Key from .env
huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")

if not huggingface_api_key:
    raise ValueError("❌ ERROR: HUGGINGFACE_API_KEY is missing. Make sure it's in your .env file.")

# ✅ Hugging Face API URL
API_URL = "https://api-inference.huggingface.co/models/facebook/blenderbot-400M-distill"

# ✅ Set Authorization Header
headers = {"Authorization": f"Bearer {huggingface_api_key}"}

# ✅ Function to Get AI Response
def get_ai_response(prompt):
    data = {"inputs": prompt}
    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.json()}

# ✅ Test the AI Model
user_input = "What is AI?"
ai_response = get_ai_response(user_input)

print("🔹 AI Response:", ai_response)



