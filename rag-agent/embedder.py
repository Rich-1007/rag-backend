# embedder.py
import google.generativeai as genai
from config import GOOGLE_API_KEY, EMBEDDING_MODEL
import time

genai.configure(api_key=GOOGLE_API_KEY)


def get_embedding(text: str) -> list[float]:
    result = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=text
    )
    return result['embedding']


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    embeddings = []
    
    for i, text in enumerate(texts):
        try:
            embedding = get_embedding(text)
            embeddings.append(embedding)
        except Exception as e:
            print(f"  Error on chunk {i}: {e}")
            print("  Waiting 60s for rate limit reset...")
            time.sleep(60)
            embedding = get_embedding(text)
            embeddings.append(embedding)
        
        if (i + 1) % 50 == 0:
            print(f"  Processed {i+1}/{len(texts)} embeddings...")
            time.sleep(1)
    
    return embeddings