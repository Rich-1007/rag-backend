# ingest.py
import sys
import os
from PyPDF2 import PdfReader
from chunker import chunk_text
from vector_store import store_chunks
from config import CHUNK_SIZE, CHUNK_OVERLAP

DATA_DIR = "data"
SAVED_TEXT_PATH = os.path.join(DATA_DIR, "sample.txt")


def load_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text = ""
    for i, page in enumerate(reader.pages):
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
        print(f"  Read page {i+1}/{len(reader.pages)}")
    return text


def load_text(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def save_extracted_text(text: str, source_filename: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    
    header = (
        f"{'='*60}\n"
        f"SOURCE FILE: {source_filename}\n"
        f"CHARACTERS: {len(text)}\n"
        f"{'='*60}\n\n"
    )
    
    mode = "a" if os.path.exists(SAVED_TEXT_PATH) else "w"
    
    with open(SAVED_TEXT_PATH, mode, encoding="utf-8") as f:
        if mode == "a":
            f.write("\n\n")
        f.write(header + text)
    
    print(f"  ✅ Text saved to {SAVED_TEXT_PATH}")
    return SAVED_TEXT_PATH


def ingest_file(file_path: str) -> dict:
    print(f"\n{'='*50}")
    print(f"INGESTING: {file_path}")
    print(f"{'='*50}")
    
    print("\n[1/4] Loading file...")
    if file_path.endswith(".pdf"):
        text = load_pdf(file_path)
    elif file_path.endswith(".txt"):
        text = load_text(file_path)
    else:
        raise ValueError("Unsupported file type. Use .pdf or .txt")
    
    print(f"  Extracted {len(text)} characters")
    
    print("\n[2/4] Saving extracted text to data/sample.txt...")
    source_name = os.path.basename(file_path)
    saved_path = save_extracted_text(text, source_name)
    
    print("\n[3/4] Reading from saved file & chunking...")
    saved_text = load_text(saved_path)
    chunks = chunk_text(saved_text, CHUNK_SIZE, CHUNK_OVERLAP)
    print(f"  Created {len(chunks)} chunks")
    
    print("\n[4/4] Embedding and storing in Supabase...")
    store_chunks(chunks, metadata={"source": source_name})
    
    result = {
        "file": file_path,
        "saved_to": saved_path,
        "characters": len(text),
        "chunks": len(chunks)
    }
    
    print(f"\n✅ Ingestion complete!")
    print(f"   Text saved to: {saved_path}")
    print(f"   Chunks stored: {len(chunks)}")
    return result


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3.12 ingest.py <file_path>")
        sys.exit(1)
    
    ingest_file(sys.argv[1])