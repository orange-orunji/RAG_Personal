from fastapi.responses import StreamingResponse
from app.schemas.chat import ChatRequest
from app.services.history_service import get_file_chat_history
from app.services.llm import get_rag_chain

import os
from fastapi import APIRouter, Depends
from app.utils.auth import get_current_user
from app.config.settings import get_settings
router = APIRouter()

"""
流式输出接口
"""
@router.post("/stream")
async def stream_chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user["user_id"]
    async def event_stream():
        try:
            chain = get_rag_chain(user_id)
            async for chunk in chain.astream(
                {"input": request.question},
                config={"configurable": {"session_id": request.session_id, "user_id": user_id}}
            ):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            # 发送错误消息给前端，避免连接突然中断
            yield f"data: 【系统错误】{str(e)}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@router.get("/history/{session_id}")
async def get_history(session_id: str, current_user: dict = Depends(get_current_user)):
    history = get_file_chat_history(session_id,user_id=current_user["user_id"])
    # 将 BaseMessage 列表转为可序列化的字典列表
    messages = []
    for msg in history.messages:
        messages.append({
            "role": "human" if msg.type == "human" else "assistant",
            "content": msg.content
        })
    return {"messages": messages}

@router.get("/sessions")
async def get_user_sessions(current_user: dict = Depends(get_current_user)):
    """对话管理"""
    user_id = str(current_user["user_id"])
    storage_path = get_settings().CHAT_HISTORY_STORAGY_PATH
    user_dir = os.path.join(storage_path, user_id)

    if not os.path.exists(user_dir):
        return {"sessions": []}

    # 列出该目录下所有 .json 文件，提取会话 ID（去掉 .json 后缀）
    sessions = [
        f.replace('.json', '')
        for f in os.listdir(user_dir)
        if f.endswith('.json')
    ]
    return {"sessions": sessions}