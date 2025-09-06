# DB & KB Chatbot with FastAPI and Streamlit

This repository contains a knowledge base and database chatbot powered by FastAPI, Streamlit, LangChain, Groq LLM, and Pinecone. The system allows users to:

- Upload PDFs, DOCX, or TXT files to a knowledge base (KB)
- Ask questions that are intelligently routed to either the database or the knowledge base
- Interactively chat with answers displayed in a clean Streamlit interface
- Generate SQL queries for structured database questions and summarize results

## Demo Video

[Watch the demo here](https://drive.google.com/file/d/1rx_alCBAl8GaFB6I1Si1B4xuhv2QsJc7/view?usp=drive_link)

## Features

### FastAPI Backend:
- `/ingestion-pipeline`: Ingest documents into Pinecone vector database
- `/chatbot`: Query KB or database via REST API
- `/test`: Simple health check endpoint

### Streamlit Frontend:
- Chat interface for database & KB questions
- Sidebar for uploading files and monitoring upload progress
- Maintains session state with chat history

### Database Agent:
- Converts natural language questions to SQL
- Executes queries on sqlite database (customer_complaints.db)
- Returns structured, human-readable summaries

### Knowledge Base Agent:
- Uses Pinecone vector store with embeddings from HuggingFace
- Answers questions based on uploaded documents

### Routing Agent:
- Determines if a question should go to DB agent or KB agent

## Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/db-kb-chatbot.git
cd db-kb-chatbot
