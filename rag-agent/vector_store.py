# vector_store.py
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY
from embedder import get_embedding
import time

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def store_chunks(chunks: list[str], metadata: dict = None) -> None:
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        
        data = {
            "content": chunk,
            "metadata": metadata or {},
            "embedding": embedding
        }
        
        supabase.table("documents").insert(data).execute()
        print(f"  Stored chunk {i+1}/{len(chunks)}")
        time.sleep(0.1)


def search_similar(query: str, match_count: int = 5,
                   match_threshold: float = 0.3) -> list[dict]:
    query_embedding = get_embedding(query)
    
    result = supabase.rpc("match_documents", {
        "query_embedding": query_embedding,
        "match_threshold": match_threshold,
        "match_count": match_count
    }).execute()
    
    return result.data


def get_document_count() -> int:
    result = supabase.table("documents").select(
        "id", count="exact"
    ).execute()
    return result.count


def clear_all_documents() -> None:
    supabase.table("documents").delete().neq("id", 0).execute()
    print("All documents cleared.")