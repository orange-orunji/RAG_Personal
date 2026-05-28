from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest
from app.services.chat import stream_chat as stream_chat_service
router = APIRouter()

"""
流式输出接口
"""
@router.post("/stream")
async def stream_chat(request : ChatRequest) ->  StreamingResponse:
    return StreamingResponse(
        stream_chat_service(request.message),
        media_type="text/event-stream"
    )