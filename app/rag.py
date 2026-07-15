from pathlib import Path
from functools import lru_cache
import fitz

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma

from app.config import (
    BOOKS_DIR,
    CHROMA_DIR,
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

    for subject_folder in sorted(BOOKS_DIR.iterdir()):

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

    print("\nKnowledge base created successfully.")

    return db


def retrieve_documents(question: str, subject: str = "", top_k: int = TOP_K):
    db = get_db()

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
