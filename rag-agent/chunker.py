# chunker.py

def chunk_text(text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list[str]:
    if not text or not text.strip():
        return []
    
    text = text.strip()
    text = " ".join(text.split())
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        if end < len(text):
            last_period = chunk.rfind('. ')
            last_newline = chunk.rfind('\n')
            break_point = max(last_period, last_newline)
            
            if break_point > chunk_size * 0.3:
                chunk = chunk[:break_point + 1]
                end = start + break_point + 1
        
        chunk = chunk.strip()
        if chunk:
            chunks.append(chunk)
        
        step = max(len(chunk) - chunk_overlap, 1)
        start += step
    
    return chunks