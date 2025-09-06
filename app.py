import requests
import streamlit as st
from Agents.app_graph import build_app

st.set_page_config(page_title="DB & KB Chatbot", page_icon="🤖", layout="wide")
st.title("🤖 Chatbot with Database & Knowledge Base Agents")

API_URL = "http://localhost:8000/ingestion-pipeline"

# -----------------------------
# Graph (Cached)
# -----------------------------
@st.cache_resource
def get_graph():
    return build_app()

graph = get_graph()

# -----------------------------
# Session State Initialization
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "upload_progress" not in st.session_state:
    st.session_state.upload_progress = 0

if "uploading_files" not in st.session_state:
    st.session_state.uploading_files = False

# -----------------------------
# Sidebar: File Upload
# -----------------------------
with st.sidebar:
    st.header("📂 Knowledge Base Ingestion")
    uploaded_files = st.file_uploader(
        "Upload Files", type=["txt", "docx", "pdf"], accept_multiple_files=True
    )

    def ingest_files(files):
        st.session_state.uploading_files = True
        for i, f in enumerate(files, start=1):
            try:
                files_data = {"file": (f.name, f.read(), f.type)}
                response = requests.post(API_URL, files=files_data)
                if response.status_code == 200:
                    st.success(f"✅ {f.name} ingested successfully!")
                else:
                    detail = response.json().get("detail", response.text)
                    st.error(f"❌ Failed to ingest {f.name}: {detail}")
            except Exception as e:
                st.error(f"⚠️ Error ingesting {f.name}: {e}")
            st.session_state.upload_progress = i / len(files)
        st.balloons()
        st.session_state.upload_progress = 0
        st.session_state.uploading_files = False

    if uploaded_files:
        if not st.session_state.uploading_files:
            st.button("Start Upload", on_click=ingest_files, args=(uploaded_files,))
        if st.session_state.upload_progress > 0:
            st.progress(st.session_state.upload_progress)

# -----------------------------
# Chat Layout
# -----------------------------
chat_col, control_col = st.columns([3, 1])

with chat_col:
    st.subheader("💬 Chat with Knowledge Base")
    for idx, chat in enumerate(st.session_state.chat_history, start=1):
        st.chat_message("user").markdown(chat["question"])
        st.chat_message("assistant").markdown(chat["answer"].get("answer", ""))
        if chat["answer"].get("sql_query"):
            with st.expander(f"🔎 SQL Query (Q{idx})"):
                st.code(chat["answer"]["sql_query"], language="sql")

# -----------------------------
# Control Column
# -----------------------------
with control_col:
    st.subheader("Controls")

    # Form with clear_on_submit=True automatically clears input
    with st.form("chat_form", clear_on_submit=True):
        q = st.text_input("Ask a question", key="chat_input")
        submitted = st.form_submit_button("Send")

        if submitted and q.strip():
            with st.spinner("🤔 Thinking..."):
                res = graph.invoke({
                    "question": q.strip(),
                    "route": "",
                    "answer": "",
                    "sql_query": "",
                    "query_result": "",
                    "query_rows": []
                })
            st.session_state.chat_history.append({"question": q.strip(), "answer": res})

    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.success("Chat history cleared!")
