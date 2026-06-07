import streamlit as st
import requests

st.set_page_config(page_title="企业智能知识库", layout="wide")
st.title("📚 企业文档智能问答")

# 侧边栏：上传文件
with st.sidebar:
    st.header("上传文档")
    uploaded_file = st.file_uploader("选择 PDF/TXT/MD 文件", type=["pdf", "txt", "md"])
    if uploaded_file is not None:
        with st.spinner("正在解析并入库..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            resp = requests.post("http://127.0.0.1:8000/api/document/upload", files=files)
            st.success(resp.json().get("data", "上传成功"))

    st.divider()
    st.caption("支持多轮对话，上下文已自动保持")

# 主区域：聊天
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 输入问题
if prompt := st.chat_input("输入你的问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("思考中..."):
            resp = requests.post(
                "http://127.0.0.1:8000/api/chat/stream",
                json={"question": prompt, "session_id": "default"},
                stream=True
            )
            placeholder = st.empty()
            full_response = ""
            for chunk in resp.iter_lines(delimiter=b'\n'):
                if chunk:
                    decoded = chunk.decode('utf-8')
                    # 去除 SSE 的 "data:" 前缀（如果有）
                    if decoded.startswith("data: "):
                        text = decoded[6:]
                    else:
                        text = decoded
                    full_response += text
                    placeholder.markdown(full_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})