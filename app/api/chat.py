from fastapi import APIRouter
from app.schemas.chat import ChatRequest
router = APIRouter()


@router.post("/")
async def chat(request : ChatRequest) ->  dict:
    return {"message":f"你问了{request.message}"}
