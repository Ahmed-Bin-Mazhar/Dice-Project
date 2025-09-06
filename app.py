import requests
import streamlit as st
from Agents.app_graph import build_app

# -----------------------------
# Streamlit Config
# -----------------------------
st.set_page_config(
    page_title="DB & KB Chatbot", 
    page_icon="🤖", 
    layout="wide"
)
st.title("🤖 Chatbot with Database & Knowledge Base Agents")

API_URL = "http://localhost:8000/ingestion-pipeline"  # Update with deployed API URL

# -----------------------------
# Sidebar: Knowledge Base Ingestion
# -----------------------------
with st.sidebar:
    st.header("📂 Knowledge Base Ingestion")
    st.write("""
        Upload `.txt`, `.pdf`, or `.docx` files to update the knowledge base.
        After uploading, the chatbot will be able to answer questions based on these files.
    """)
    
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
                    try:
                        detail = response.json().get("detail", "Unknown error")
                    except Exception:
                        detail = response.text
                    st.error(f"❌ Failed to ingest {f.name}: {detail}")

            except Exception as e:
                st.error(f"⚠️ Error during ingestion of {f.name}: {e}")

            progress.progress(i / len(uploaded_files))
        st.balloons()  # Celebration animation

# -----------------------------
# Build Graph
# -----------------------------
graph = build_app()

# -----------------------------
# Initialize Chat History
# -----------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -----------------------------
# Layout: Chat & Controls
# -----------------------------
chat_col, control_col = st.columns([3, 1])

# -----------------------------
# Chat Column
# -----------------------------
with chat_col:
    st.subheader("💬 Chat with the Knowledge Base")

    # Display conversation as chat bubbles
    for idx, chat in enumerate(st.session_state.chat_history, start=1):
        st.chat_message("user").markdown(chat['question'])
        st.chat_message("assistant").markdown(chat['answer'].get('answer', ''))

        if chat["answer"].get("sql_query"):
            with st.expander(f"🔎 SQL Query (Q{idx})"):
                st.code(chat["answer"]["sql_query"], language="sql")

# -----------------------------
# Control Column
# -----------------------------
with control_col:
    st.subheader("Controls")
    with st.form("chat_form"):
        q = st.text_input("Ask a question")
        submitted = st.form_submit_button("Send")

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
            # Save to chat history (page auto-refreshes)
            st.session_state.chat_history.append({"question": q, "answer": res})

    # Clear chat history
    if st.button("🗑️ Clear Chat History"):
        st.session_state.chat_history = []
        st.success("Chat history cleared!")
