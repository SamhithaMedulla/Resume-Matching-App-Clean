import os
from dotenv import load_dotenv

load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
if not HUGGINGFACE_API_KEY:
    print("❌ Hugging Face API key not loaded! Check your .env file.")
else:
    print("✅ Hugging Face API key loaded successfully!")
