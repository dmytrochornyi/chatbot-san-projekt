import os
from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGVector

COLLECTION_NAME = "san_docs"


def get_vector_store() -> PGVector:
    embeddings = OllamaEmbeddings(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
    )
    return PGVector(
        embeddings=embeddings,
        collection_name=COLLECTION_NAME,
        connection=os.getenv("DATABASE_URL"),
    )


def get_retriever():
    return get_vector_store().as_retriever(search_kwargs={"k": 5})
