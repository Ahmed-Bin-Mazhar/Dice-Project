import requests
import streamlit as st
from Agents.app_graph import build_app

# -----------------------------
# Streamlit Config
# -----------------------------
st.set_page_config(page_title="DB & KB Chatbot", page_icon="🤖", layout="wide")
st.title("🤖 Chatbot with Database & Knowledge Base Agents")

API_URL = "http://localhost:8000/ingestion-pipeline"  # Update with deployed API URL

# -----------------------------
# Sidebar: Ingestion
# -----------------------------
with st.sidebar:
    st.header("📂 Knowledge Base Ingestion")
    st.write("Upload `.txt`, `.pdf`, or `.docx` files to update the knowledge base.")

    uploaded_files = st.file_uploader(
        "Upload Files",
        type=["txt", "docx", "pdf"],
        accept_multiple_files=True
    )

    if uploaded_files:
        progress = st.progress(0)
        for i, f in enumerate(uploaded_files, start=1):
            try:
                files = {"file": (f.name, f.read(), f.type)}
                response = requests.post(API_URL, files=files)

                if response.status_code == 200:
                    st.success(f"✅ {f.name} ingested successfully!")
                else:
                    # Handle JSON and non-JSON error responses
                    try:
                        detail = response.json().get("detail", "Unknown error")
                    except Exception:
                        detail = response.text
                    st.error(f"❌ Failed to ingest {f.name}: {detail}")

            except Exception as e:
                st.error(f"⚠️ Error during ingestion of {f.name}: {e}")

            progress.progress(i / len(uploaded_files))

# -----------------------------
# Build Graph
# -----------------------------
graph = build_app()

# -----------------------------
# Chat History
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -----------------------------
# Chat Form
# -----------------------------
with st.form("chat_form"):
    q = st.text_input("💬 Ask a question")
    submitted = st.form_submit_button("Ask")

    if submitted and q:
        with st.spinner("🤔 Thinking..."):
            res = graph.invoke({
                "question": q,
                "route": "",
                "answer": "",
                "sql_query": "",
                "query_result": "",
                "query_rows": []
            })
        # Save to history
        st.session_state.chat_history.append({"question": q, "answer": res})

# -----------------------------
# Display Conversation
# -----------------------------
if st.session_state.chat_history:
    st.subheader("Conversation")
    for idx, chat in enumerate(st.session_state.chat_history, start=1):
        st.markdown(f"**Q{idx}:** {chat['question']}")
        st.markdown(f"**A{idx}:** {chat['answer'].get('answer', '')}")

        if chat["answer"].get("sql_query"):
            with st.expander(f"🔎 SQL Query (Q{idx})"):
                st.code(chat["answer"]["sql_query"], language="sql")
