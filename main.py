from fastapi import FastAPI
from app.api.chat import router as chat_router
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI(title="RAG Personal API")

# 添加拦截器
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由(将聊天接口加到主路由上)
app.include_router(chat_router,prefix="/api/chat",tags=["对话接口"])




