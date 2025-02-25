import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# API configuration
API_KEY = os.getenv("GROQ_API_KEY", "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")
MODEL_NAME = os.getenv("MODEL_NAME", "llama3-70b-8192")

# FastAPI configuration
FASTAPI_HOST = os.getenv("FASTAPI_HOST", "0.0.0.0")
FASTAPI_PORT = int(os.getenv("FASTAPI_PORT", 8000))