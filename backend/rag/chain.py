import os
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from rag.retriever import get_retriever

SYSTEM_PROMPT = """You are a helpful academic assistant for Społeczna Akademia Nauk (SAN) university.
Answer the student's question using only the provided context from university documents.
If the context does not contain enough information to answer, say so honestly.
Answer in the same language as the question.

Context:
{context}"""

_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}"),
])


def _format_docs(docs) -> str:
    return "\n\n".join(doc.page_content for doc in docs)


def get_chain():
    llm = ChatOllama(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model=os.getenv("OLLAMA_MODEL", "llama3.2"),
    )
    retriever = get_retriever()
    return (
        {"context": retriever | _format_docs, "question": RunnablePassthrough()}
        | _prompt
        | llm
        | StrOutputParser()
    )
