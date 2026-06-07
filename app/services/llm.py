
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from app.config.settings import get_settings
from collections.abc import AsyncIterator
from openai import AsyncOpenAI,APIError

from app.services.KnowledgeBase_md5_service import KnowledgeBaseService


# 获取模型API相关的信息
def _client() -> AsyncOpenAI:
  c = get_settings()
  return AsyncOpenAI(
    api_key= c.SILICON_API_KEY,
    base_url= c.SILICON_BASE_URL
  )


def build_content(message: str) -> list[dict[str, str]]:
    return [{"role": "user", "content": message}]


async def stream_llm(messages: list[dict[str, str]]) -> AsyncIterator[str]:
    s = get_settings()
    client = _client()
    try:
        stream = await client.chat.completions.create(
            model=s.SILICON_MODEL,
            messages=messages,
            stream=True,
        )
        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    except APIError:
        yield "【服务异常】请检查 API Key、模型名或网络"
        return


def get_rag_chain():
    s = get_settings()

    retriever = KnowledgeBaseService().chroma.as_retriever()

    llm = ChatOpenAI(
        model=s.SILICON_MODEL,
        api_key=s.SILICON_API_KEY,
        base_url=s.SILICON_BASE_URL,
        streaming=True,
        callbacks=[]
    )

    prompt = ChatPromptTemplate.from_messages(
            messages=[
                ("system","以提供的已知参考资料为主,"
                 "简洁和专业的回答用户问题，参考资料:{content}"),
                ("system","并且更根据历史信息来回答"),
                # MessagesPlaceholder("history"),
                ("human","问题:{input}")
            ]
        )



    chain = (
        {
            "input": RunnablePassthrough(),
            "content": retriever | __format_content
        } | prompt | llm | StrOutputParser()
    )

    return chain

def __format_content(documents):
    if not documents:
        return "无相关参考资料"
    else:
        document_str=""
        for doc in documents:
            document_str += f"文档片段：{doc.page_content}\n"
        return document_str

if __name__ == '__main__':
    chain = get_rag_chain()
    stream = chain.stream("什么是高考")
    for chunk in stream:
        print(chunk)
