from pathlib import Path
from functools import lru_cache
import json
import fitz

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma

from app.config import (
    BOOKS_DIR,
    CHROMA_DIR,
    CHROMA_INDEX_MANIFEST,
    EMBEDDING_MODEL,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K,
)

def _embedding_kwargs():
    # Keep the model load fully local so the app does not depend on network access.
    return {"local_files_only": True}


@lru_cache(maxsize=1)
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs=_embedding_kwargs(),
    )


@lru_cache(maxsize=1)
def get_db():
    return Chroma(
        persist_directory=str(CHROMA_DIR),
        embedding_function=get_embeddings(),
    )


def _iter_subject_dirs():
    if not BOOKS_DIR.exists():
        return []
    return [folder for folder in sorted(BOOKS_DIR.iterdir()) if folder.is_dir()]


def _source_pdf_snapshot():
    """Return a lightweight snapshot of the source PDFs on disk."""

    snapshot = []

    for subject_folder in _iter_subject_dirs():
        for pdf in sorted(subject_folder.rglob("*.pdf")):
            if pdf.name.lower() == "contents.pdf":
                continue

            stat = pdf.stat()
            snapshot.append(
                {
                    "subject": subject_folder.name,
                    "path": str(pdf.relative_to(BOOKS_DIR)),
                    "size": stat.st_size,
                    "mtime_ns": stat.st_mtime_ns,
                }
            )

    return snapshot


def _load_index_manifest():
    try:
        return json.loads(CHROMA_INDEX_MANIFEST.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except Exception:
        return None


def _save_index_manifest(snapshot):
    CHROMA_INDEX_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    CHROMA_INDEX_MANIFEST.write_text(
        json.dumps(snapshot, ensure_ascii=True, indent=2),
        encoding="utf-8",
    )


def index_is_stale() -> bool:
    """Check whether the local Chroma index matches the current PDF set."""

    current_snapshot = _source_pdf_snapshot()
    saved_snapshot = _load_index_manifest()
    return saved_snapshot != current_snapshot


def ensure_index_current():
    """Rebuild Chroma only when the index is empty."""

    db = get_db()
    try:
        has_docs = db._collection.count() > 0
    except Exception:
        has_docs = False

    if has_docs:
        return db

    if _source_pdf_snapshot():
        print("\nDetected empty Chroma index. Rebuilding from PDFs...\n")
        rebuild_database()
    return get_db()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP
)


def read_pdf(pdf_path: Path):
    """Read a PDF and return one Document per page."""

    documents = []

    pdf = fitz.open(pdf_path)

    for page_number, page in enumerate(pdf, start=1):

        text = page.get_text().strip()

        if not text:
            continue

        documents.append(
            Document(
                page_content=text,
                metadata={
                    "page": page_number
                }
            )
        )

    pdf.close()

    return documents


def load_all_books():
    """Read every PDF from the books folder."""

    all_documents = []

    for subject_folder in _iter_subject_dirs():

        if not subject_folder.is_dir():
            continue

        print(f"\nSubject : {subject_folder.name}")

        for pdf in sorted(subject_folder.glob("*.pdf")):

            if pdf.name.lower() == "contents.pdf":
                continue

            print(f"Reading : {pdf.name}")

            docs = read_pdf(pdf)

            for doc in docs:

                doc.metadata["subject"] = subject_folder.name
                doc.metadata["chapter"] = pdf.stem

            all_documents.extend(docs)

    return all_documents


def build_database(documents=None):

    print("\nLoading PDFs...\n")

    if documents is None:
        documents = load_all_books()

    print(f"\nPages loaded : {len(documents)}")

    print("\nSplitting into chunks...")

    chunks = splitter.split_documents(documents)

    print(f"Chunks created : {len(chunks)}")

    print("\nBuilding Chroma database...")

    try:
        existing_db = get_db()
        existing_db.delete_collection()
        get_db.cache_clear()
        print("Existing Chroma collection cleared.")
    except Exception:
        get_db.cache_clear()

    db = Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        persist_directory=str(CHROMA_DIR)
    )

    get_db.cache_clear()
    _save_index_manifest(_source_pdf_snapshot())

    print("\nKnowledge base created successfully.")

    return db


def rebuild_database():
    """Clear and rebuild the Chroma database from the current PDF set."""

    return build_database()


def discover_subjects():
    """Return subjects from both the filesystem and the indexed metadata."""

    subjects = {folder.name for folder in _iter_subject_dirs()}

    try:
        db = get_db()
        data = db.get(include=["metadatas"])
        for metadata in data.get("metadatas", []):
            if metadata and metadata.get("subject"):
                subjects.add(metadata["subject"])
    except Exception:
        pass

    return sorted(subjects)


def retrieve_documents(question: str, subject: str = "", top_k: int = TOP_K):
    db = ensure_index_current()

    search_kwargs = {"k": top_k}
    if subject:
        search_kwargs["filter"] = {"subject": subject}

    results = db.similarity_search_with_score(question, **search_kwargs)

    if not results and subject:
        results = db.similarity_search_with_score(question, k=top_k)

    docs = [doc for doc, _ in results]
    context = "\n\n".join(doc.page_content for doc in docs)

    seen = set()
    sources = []
    for doc in docs:
        source = {
            "subject": doc.metadata.get("subject", ""),
            "chapter": doc.metadata.get("chapter", ""),
            "page": doc.metadata.get("page", ""),
        }
        key = (source["subject"], source["chapter"], source["page"])
        if key in seen:
            continue
        seen.add(key)
        sources.append(source)

    return {
        "docs": docs,
        "context": context,
        "sources": sources,
    }


if __name__ == "__main__":
    build_database()
