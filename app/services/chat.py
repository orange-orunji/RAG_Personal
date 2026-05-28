
from typing import AsyncIterator

async def stream_chat(message : str) -> AsyncIterator[bytes]:
  """
  流式输出接口
  """
  text = f"你输入的内容是{message}"
  for i in range(0,len(text),2):
    content = text[i:i+2]
    yield f"data:{content}\n\n".encode("utf-8")
  yield "data:[DONE]\n\n".encode("utf-8")
