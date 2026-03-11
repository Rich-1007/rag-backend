# agent.py
from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL
from retriever import retrieve, format_context

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """You are a helpful AI assistant that answers questions 
based on the provided context documents.

RULES:
1. Answer ONLY based on the provided context
2. If the context doesn't contain the answer, say: 
   "I don't have enough information in my knowledge base to answer that."
3. Quote relevant parts of the context when possible
4. Be concise but thorough
5. If the question is unclear, ask for clarification"""


def build_augmented_prompt(query: str, context: str) -> str:
    return f"""CONTEXT (retrieved from knowledge base):
{context}

---

USER QUESTION: {query}

Based on the context above, provide a helpful answer:"""


def ask(query: str, top_k: int = 5) -> dict:
    retrieved_chunks = retrieve(query, top_k=top_k)
    
    if not retrieved_chunks:
        return {
            "answer": "No relevant information found. Please upload documents first.",
            "sources": [],
            "chunks_used": 0
        }
    
    context = format_context(retrieved_chunks)
    augmented_prompt = build_augmented_prompt(query, context)
    
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": augmented_prompt}
        ],
        temperature=0.3,
        max_tokens=1024,
        top_p=0.9
    )
    
    answer = response.choices[0].message.content
    
    sources = list(set(
        chunk.get("metadata", {}).get("source", "unknown")
        for chunk in retrieved_chunks
    ))
    
    return {
        "answer": answer,
        "sources": sources,
        "chunks_used": len(retrieved_chunks)
    }


if __name__ == "__main__":
    print("╔══════════════════════════════════════╗")
    print("║       RAG Agent — CLI Mode           ║")
    print("║   Type 'quit' to exit                ║")
    print("╚══════════════════════════════════════╝")
    
    while True:
        query = input("\n📝 Your question: ").strip()
        
        if query.lower() in ('quit', 'exit', 'q'):
            print("Goodbye!")
            break
        
        if not query:
            continue
        
        print("🔍 Searching knowledge base...")
        result = ask(query)
        
        print(f"\n💡 Answer:\n{result['answer']}")
        print(f"\n📎 Sources: {', '.join(result['sources'])}")
        print(f"📊 Chunks used: {result['chunks_used']}")