from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import ChatRequest

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest):
    # TODO: wire up RAG chain and stream LLM response
    raise NotImplementedError
