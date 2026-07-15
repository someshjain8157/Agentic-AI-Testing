from app.rag import build_database, load_all_books


def main():
    print("=" * 60)
    print("Akanksh AI 1.0 - Refresh Books and Rebuild Chroma")
    print("=" * 60)

    documents = load_all_books()
    subjects = sorted({doc.metadata.get("subject", "") for doc in documents if doc.metadata.get("subject")})

    print("\nDiscovered subjects:")
    for subject in subjects:
        print(f"- {subject}")

    print("\nRebuilding the vector database...")
    build_database(documents)

    print("\nDone. New folders under books/ are now included as subjects in Chroma.")


if __name__ == "__main__":
    main()
