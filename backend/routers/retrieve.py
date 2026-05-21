from fastapi import APIRouter
from pydantic import BaseModel
from rag.retriever import get_retriever

router = APIRouter()


class RetrieveRequest(BaseModel):
    question: str


@router.post("/retrieve")
async def retrieve(request: RetrieveRequest) -> dict:
    retriever = get_retriever()
    docs = await retriever.ainvoke(request.question)
    context = "\n\n".join(doc.page_content for doc in docs)
    return {"context": context}
