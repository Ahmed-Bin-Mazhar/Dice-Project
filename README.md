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


### 2️⃣ Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows


###3️⃣ Install Dependencies
```bash
pip install -r requirements.txt

###Environment Variables
Create a .env file in the root folder and add your API keys:
```env
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
PINECONE_API_KEY=your_pinecone_api_key
INDEX_NAME=gen-ai
GROQ_API_KEY=your_groq_api_key

###Running the Project
Use the run_all.py script to start both FastAPI and Streamlit:

```bash
python run_all.py
FastAPI runs at: http://localhost:8000

Streamlit runs at: http://localhost:8501

###File Upload
```Upload PDF, DOCX, or TXT files via the sidebar. Files are processed, split into chunks, embedded, and added to Pinecone.

###Project Structure
```text
.
├── Dice-Project/
│   ├── app.py                 # Streamlit app
│   └── utils/
│       └── kbc-ingestion.py   # FastAPI ingestion & chatbot API
├── Agents/
│   ├── app_graph.py           # Graph-based agent routing
│   ├── KB_agent.py            # Knowledge base API interaction
│   ├── db_agent.py            # Database agent
│   └── router_agent.py        # Routing agent
├── run_all.py                 # Script to run FastAPI & Streamlit
├── customer_complaints.db     # SQLite database
├── requirements.txt           # Python dependencies
└── README.md                  # This file


###Requirements
```requirements.txt:

text
pandas
matplotlib
seaborn
SQLAlchemy
typing_extensions
pydantic
langchain-core
langgraph
pymysql
fastapi
streamlit
langchain_community
python-dotenv
pytest
langchain
sentence-transformers
pinecone
langchain-huggingface
pypdf
docx2txt
pinecone-client==5.0.1
tiktoken
uvicorn
langchain_groq
werkzeug
python-multipart


###Notes
```note
The FastAPI server must be running before using the Streamlit interface

Only PDF files are supported for ingestion in the current implementation

Groq LLM (llama-3.3-70b-versatile) is used for generating SQL queries and summarizing results

###License
```lisence
This project is licensed under the MIT License.

```text

You can save this content to a file named `README.md` in your project's root directory. This comprehensive documentation will help users understand and use your chatbot project effectively.
