import streamlit as st
import requests
import uuid

st.set_page_config(page_title="企业智能知识库", layout="wide")
st.title("📚 企业文档智能问答")

# ---------- 通过 URL 参数保持 session_id ----------
query_params = st.query_params
# 如果 URL 中有 session_id，则使用它；否则生成新的并更新 URL
if "session_id" in query_params:
    session_id = query_params["session_id"]
    # 确保 session_state 中有这个 id
    if "current_session" not in st.session_state:
        st.session_state.current_session = session_id
else:
    # 没有 URL 参数，生成新 ID 并设置
    if "current_session" not in st.session_state:
        new_id = str(uuid.uuid4())[:8]
        st.session_state.current_session = new_id
        st.query_params["session_id"] = new_id
    else:
        # 以防万一，同步到 URL
        st.query_params["session_id"] = st.session_state.current_session

current_session = st.session_state.current_session

# 初始化当前会话的消息缓存（仍然用 st.session_state 暂存）
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------- 侧边栏 ----------
with st.sidebar:
    st.header("📂 会话管理")

    # 新建会话按钮
    if st.button("➕ 新建会话", use_container_width=True):
        new_id = str(uuid.uuid4())[:8]
        st.session_state.current_session = new_id
        st.session_state.messages = []        # 清空消息
        st.query_params["session_id"] = new_id
        st.rerun()

    st.divider()

    # ---------- 根据 ID 查询历史会话 ----------
    st.subheader("🔍 查询会话")
    with st.form("search_form"):
        search_id = st.text_input("输入会话 ID", placeholder="例如：abc123")
        submitted = st.form_submit_button("切换到此会话")
        if submitted and search_id:
            # 验证 ID 是否合法（可选）
            search_id = search_id.strip()
            if search_id:
                # 直接切换到输入的 ID，不论后端是否有历史（没有历史就显示空）
                st.session_state.current_session = search_id
                st.session_state.messages = []
                st.query_params["session_id"] = search_id
                st.rerun()
    st.divider()

    # 当前会话显示
    st.caption(f"当前会话ID: `{current_session}`")

    # 上传文件
    st.divider()
    st.header("📄 上传文档")
    uploaded_file = st.file_uploader("选择 PDF/TXT/MD 文件", type=["pdf", "txt", "md"])
    if uploaded_file is not None:
        with st.spinner("正在解析并入库..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
            resp = requests.post("http://127.0.0.1:8000/api/document/upload", files=files)
            st.success(resp.json().get("data", "上传成功"))

    st.divider()
    st.caption("支持多轮对话，历史自动持久化")

# ---------- 从后端加载当前会话的历史（首次加载时）----------
if not st.session_state.messages:
    with st.spinner("加载历史记录..."):
        resp = requests.get(f"http://127.0.0.1:8000/api/chat/history/{current_session}")
        if resp.status_code == 200:
            st.session_state.messages = resp.json().get("messages", [])

# ---------- 主聊天区 ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("输入你的问题..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("thinking..."):
            resp = requests.post(
                "http://127.0.0.1:8000/api/chat/stream",
                json={"question": prompt, "session_id": current_session},
                stream=True
            )
            placeholder = st.empty()
            full_response = ""
            for chunk in resp.iter_lines(decode_unicode=True):
                if chunk:
                    text = chunk[6:] if chunk.startswith("data: ") else chunk
                    full_response += text
                    placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})