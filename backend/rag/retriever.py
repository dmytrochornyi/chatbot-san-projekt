import os
from langchain_ollama import OllamaEmbeddings
from langchain_postgres import PGVector
from sqlalchemy.ext.asyncio import create_async_engine

COLLECTION_NAME = "san_docs"
_DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@db:5432/san_chatbot",
)


def _embeddings() -> OllamaEmbeddings:
    return OllamaEmbeddings(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
    )


def get_vector_store() -> PGVector:
    engine = create_async_engine(_DB_URL)
    return PGVector(
        embeddings=_embeddings(),
        collection_name=COLLECTION_NAME,
        connection=engine,
    )


def get_retriever():
    return get_vector_store().as_retriever(search_kwargs={"k": 5})
