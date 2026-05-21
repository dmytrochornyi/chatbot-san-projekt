#!/usr/bin/env python3
"""
Load PDFs from data/raw/, chunk them, embed with Ollama, store in pgvector.
Run once before starting the app: uv run python scripts/ingest.py
"""
import os
import sys
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGVector

DATA_DIR = Path(__file__).parent.parent / "data" / "raw"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/san_chatbot")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")


def main():
    pdf_files = sorted(DATA_DIR.glob("*.pdf"))
    if not pdf_files:
        print(f"No PDFs found in {DATA_DIR}")
        sys.exit(1)

    docs = []
    for path in pdf_files:
        print(f"  Loading {path.name}...")
        docs.extend(PyPDFLoader(str(path)).load())
    print(f"Loaded {len(docs)} pages from {len(pdf_files)} PDFs")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks")

    embeddings = OllamaEmbeddings(base_url=OLLAMA_BASE_URL, model=OLLAMA_EMBED_MODEL)

    print("Storing in pgvector (this may take a while)...")
    PGVector.from_documents(
        documents=chunks,
        embedding=embeddings,
        collection_name="san_docs",
        connection=DATABASE_URL,
        pre_delete_collection=True,
    )
    print("Done.")


if __name__ == "__main__":
    main()
