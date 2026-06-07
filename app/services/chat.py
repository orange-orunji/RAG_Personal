from typing import AsyncIterator
from app.services.llm import get_rag_chain

async def stream_chat(message: str) -> AsyncIterator[bytes]:
  """
  流式输出接口
  """
  chain = get_rag_chain()
  async for token in chain.astream(message):
        yield token.encode("utf-8")
  yield " \ndata:[DONE]\n".encode("utf-8")
