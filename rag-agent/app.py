# app.py
from flask_cors import CORS
from flask import Flask, request, jsonify
from agent import ask
from ingest import ingest_file, SAVED_TEXT_PATH, DATA_DIR
from vector_store import get_document_count, clear_all_documents
import os
import tempfile

app = Flask(__name__)
CORS(app)  # ← add this line


@app.route("/", methods=["GET"])
def health():
    doc_count = get_document_count()
    local_file_exists = os.path.exists(SAVED_TEXT_PATH)
    return jsonify({
        "status": "running",
        "message": "RAG Agent API is live!",
        "documents_stored": doc_count,
        "local_text_backup": local_file_exists
    })


@app.route("/ask", methods=["POST"])
def ask_question():
    data = request.get_json()
    if not data or "query" not in data:
        return jsonify({"error": "Send JSON with 'query' field"}), 400
    query = data["query"].strip()
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400
    top_k = data.get("top_k", 5)
    try:
        result = ask(query, top_k=top_k)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/upload", methods=["POST"])
def upload_document():
    if "file" not in request.files:
        return jsonify({"error": "No file provided. Use form-data key 'file'"}), 400
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    allowed = ('.pdf', '.txt')
    if not file.filename.lower().endswith(allowed):
        return jsonify({"error": f"Only {allowed} files supported"}), 400
    os.makedirs(DATA_DIR, exist_ok=True)
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name
    try:
        result = ingest_file(tmp_path)
        return jsonify({
            "message": f"Successfully ingested '{file.filename}'",
            "saved_to": SAVED_TEXT_PATH,
            "details": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        os.unlink(tmp_path)


@app.route("/saved-text", methods=["GET"])
def view_saved_text():
    if not os.path.exists(SAVED_TEXT_PATH):
        return jsonify({"error": "No text saved yet. Upload a file first."}), 404
    with open(SAVED_TEXT_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    return jsonify({
        "file": SAVED_TEXT_PATH,
        "characters": len(content),
        "content": content
    })


@app.route("/clear", methods=["DELETE"])
def clear_documents():
    try:
        clear_all_documents()
        if os.path.exists(SAVED_TEXT_PATH):
            os.remove(SAVED_TEXT_PATH)
            print(f"  Deleted {SAVED_TEXT_PATH}")
        return jsonify({"message": "All documents cleared (Supabase + local file)"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)