from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BOOKS_DIR = PROJECT_ROOT / "books"
CHROMA_DIR = PROJECT_ROOT / "chromadb"
CHROMA_INDEX_MANIFEST = CHROMA_DIR / "index_manifest.json"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
OLLAMA_MODEL = "phi3:mini"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 4
