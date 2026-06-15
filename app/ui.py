import uuid
import streamlit as st
import requests
from streamlit_cookies_manager import EncryptedCookieManager

# ---------- Cookie 管理器 ----------
# 初始化加密 Cookie 管理器（密码自己设一个，用于加密 Cookie 值）
cookies = EncryptedCookieManager(password="your-secret-password")
if not cookies.ready():
    st.stop()      # 等待 Cookie 准备就绪，此时不能执行其他 Streamlit 命令

# ---------- 页面配置 ----------
st.set_page_config(page_title="企业智能知识库", layout="wide")

# ---------- 从 Cookie 恢复登录状态 ----------
if "access_token" not in st.session_state:
    # 尝试从 Cookie 中读取之前保存的 token
    saved_token = cookies.get("access_token")
    saved_user = cookies.get("user")
    if saved_token:
        # 直接把 token 和用户写入 session_state
        st.session_state.access_token = saved_token
        st.session_state.user = saved_user
    else:
        st.session_state.access_token = None
        st.session_state.user = None

# ---------- 未登录时的登录/注册界面 ----------
if st.session_state.access_token is None:
    st.title("🔐 企业知识库 - 请先登录")
    auth_mode = st.radio("选择操作", ["登录", "注册"], horizontal=True)

    with st.form("auth_form"):
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        submitted = st.form_submit_button("提交")

        if submitted:
            if auth_mode == "登录":
                resp = requests.post(
                    "http://127.0.0.1:8000/api/auth/login",
                    json={"username": username, "password": password}
                )
                if resp.status_code == 200:
                    data = resp.json()
                    token = data["access_token"]
                    # 写入 Session
                    st.session_state.access_token = token
                    st.session_state.user = username
                    # 写入加密 Cookie，7 天有效
                    cookies["access_token"] = token
                    cookies["user"] = username
                    cookies.save()
                    st.success("登录成功！")
                    st.rerun()
                else:
                    st.error("登录失败：" + resp.json().get("detail", "未知错误"))
            else:  # 注册
                resp = requests.post(
                    "http://127.0.0.1:8000/api/auth/register",
                    json={"username": username, "password": password}
                )
                if resp.status_code == 200:
                    st.success("注册成功，请切换到登录并登录")
                else:
                    st.error("注册失败：" + resp.json().get("detail", "未知错误"))
    st.stop()   # 未登录，阻止加载后面的界面

# ---------- 已登录：侧边栏显示用户信息 + 退出按钮 ----------
st.sidebar.success(f"✅ 已登录: {st.session_state.user}")
if st.sidebar.button("退出登录"):
    # 清空 Session
    st.session_state.access_token = None
    st.session_state.user = None
    # 清空 Cookie
    del cookies["access_token"]
    del cookies["user"]
    cookies.save()
    st.rerun()

# ---------- 后续所有请求都要带的 header ----------
auth_headers = {"Authorization": f"Bearer {st.session_state.access_token}"}



st.set_page_config(page_title="企业智能知识库", layout="wide")
st.title("📚 企业文档智能问答")

# ===================== 工具函数 =====================
def format_message(text: str) -> str:
    """
    1. 清洗 HTML 换行标签
    2. 将字符串中的 \\n 还原为真正的换行符 \n
    3. 将单个 \n 替换为两个 \n（Markdown 分段）
    """
    text = text.replace('<br>', '\n').replace('<br/>', '\n').replace('&lt;br&gt;', '\n')
    text = text.replace('\\n', '\n')   # 关键：把转义的 \n 变成真正的换行
    text = text.replace('\n', '\n\n')
    return text

# ===================== 会话管理 =====================
query_params = st.query_params
if "session_id" in query_params:
    session_id = query_params["session_id"]
    if "current_session" not in st.session_state:
        st.session_state.current_session = session_id
else:
    if "current_session" not in st.session_state:
        new_id = str(uuid.uuid4())[:8]
        st.session_state.current_session = new_id
        st.query_params["session_id"] = new_id
    else:
        st.query_params["session_id"] = st.session_state.current_session

current_session = st.session_state.current_session

if "messages" not in st.session_state:
    st.session_state.messages = []

# ===================== 侧边栏 =====================
with st.sidebar:
    st.header("📂 会话管理")

    if st.button("➕ 新建会话", use_container_width=True):
        new_id = str(uuid.uuid4())[:8]
        st.session_state.current_session = new_id
        st.session_state.messages = []
        st.query_params["session_id"] = new_id
        st.rerun()

    st.divider()

    st.subheader("🔍 查询会话")
    with st.form("search_form"):
        search_id = st.text_input("输入会话 ID", placeholder="例如：abc123")
        submitted = st.form_submit_button("切换到此会话")
        if submitted and search_id:
            search_id = search_id.strip()
            if search_id:
                st.session_state.current_session = search_id
                st.session_state.messages = []
                st.query_params["session_id"] = search_id
                st.rerun()
    st.divider()

    st.caption(f"当前会话ID: `{current_session}`")

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

# ===================== 加载历史记录 =====================
if not st.session_state.messages:
    with st.spinner("加载历史记录..."):
        resp = requests.get(f"http://127.0.0.1:8000/api/chat/history/{current_session}")
        if resp.status_code == 200:
            st.session_state.messages = resp.json().get("messages", [])

# ===================== 显示历史消息 =====================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        formatted = format_message(msg["content"])
        st.markdown(formatted)

# ===================== 提问与流式回答 =====================
if prompt := st.chat_input("输入你的问题..."):
    # 添加用户消息
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
                    placeholder.text(full_response)   # 打字机效果

            # ----- 调试代码 -----
            # 查看原始文本的前 200 字符（包含转义符）
            st.text(repr(full_response[:200]))
            # 格式化后的文本
            formatted = format_message(full_response)
            st.text(repr(formatted[:200]))
            # ----- 调试结束 -----

            # 最终渲染
            placeholder.markdown(formatted)

    # 保存助手消息（原始内容）
    st.session_state.messages.append({"role": "assistant", "content": full_response})