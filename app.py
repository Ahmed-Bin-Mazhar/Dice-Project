import os
import requests
from pathlib import Path
import streamlit as st

# from graph.app_graph import build_app


st.set_page_config(page_title="DB & KB Chatbot", page_icon="🤖", layout="wide")
st.title("Chatbot with Database & Knowledge Base Agents")

API_URL = "http://localhost:8000/ingestion-pipeline"  # Replace with your deployed API URL

with st.sidebar:
    st.header("Ingestion")
    st.write("Drop .txt, .pdf, or .docx files to ingest into the knowledge base")

    uploaded = st.file_uploader(
        "Update Knowledge Base",
        type=["txt", "docx", "pdf"],
        accept_multiple_files=True
    )

    if uploaded:
        for f in uploaded:
            try:
                # Call FastAPI ingestion endpoint for each file
                files = {"file": (f.name, f.read(), f.type)}
                response = requests.post(API_URL, files=files)

                if response.status_code == 200:
                    st.success(f"{f.name} ingested successfully!")
                else:
                    st.error(f"Failed to ingest {f.name}: {response.json().get('detail')}")

            except Exception as e:
                st.error(f"Error during ingestion of {f.name}: {e}")

# -----------------------------
# Build knowledge graph / LLM graph
# -----------------------------
# graph = build_app()

# -----------------------------
# Chat form
# -----------------------------
with st.form("chat_form"):
    q = st.text_input("Ask a question")
    submitted = st.form_submit_button("Ask")

# if submitted and q:
#     with st.spinner("Thinking..."):
#         res = graph.invoke({"question": q, "route": "", "answer": "", "sql": ""})
#     st.subheader("Answer")
#     st.write(res.get("answer", ""))
#     if res.get("sql"):
#         st.subheader("SQL")
#         st.code(res.get("sql"))
