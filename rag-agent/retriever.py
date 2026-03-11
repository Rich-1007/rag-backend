# retriever.py
from vector_store import search_similar


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    results = search_similar(
        query=query,
        match_count=top_k,
        match_threshold=0.3
    )
    
    if not results:
        return []
    
    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results


def format_context(chunks: list[dict]) -> str:
    if not chunks:
        return "No relevant information found."
    
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        similarity_pct = round(chunk["similarity"] * 100, 1)
        source = chunk.get("metadata", {}).get("source", "unknown")
        context_parts.append(
            f"[Source: {source} | Relevance: {similarity_pct}%]\n"
            f"{chunk['content']}"
        )
    
    return "\n\n---\n\n".join(context_parts)