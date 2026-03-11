# config.py
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

EMBEDDING_MODEL = "models/gemini-embedding-001"
LLM_MODEL = "llama-3.3-70b-versatile"
EMBEDDING_DIMENSION = 3072

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50