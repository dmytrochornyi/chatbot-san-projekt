import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from models.schemas import ChatRequest
from rag.chain import get_chain

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest):
    question = request.messages[-1].content
    chain = get_chain()

    async def generate():
        async for chunk in chain.astream(question):
            yield f"0:{json.dumps(chunk)}\n"
        finish = json.dumps({"finishReason": "stop", "usage": {"promptTokens": 0, "completionTokens": 0}})
        yield f"e:{finish}\n"
        yield f"d:{finish}\n"

    return StreamingResponse(
        generate(),
        media_type="text/plain; charset=utf-8",
        headers={"X-Vercel-AI-Data-Stream": "v1"},
    )
