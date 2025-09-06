import os
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import pinecone
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain.vectorstores import Pinecone
from langchain.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()

class QueryRequest(BaseModel):
    query: str

# Set environment variables (replace with your own keys)
os.environ["HUGGINGFACEHUB_API_TOKEN"] = os.getenv("HUGGINGFACEHUB_API_TOKEN")
os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
os.environ["PINECONE_ENV"] = "us-east-1"
os.environ["INDEX_NAME"] =  os.getenv("INDEX_NAME", "gen-ai") 
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY") 

# Initialize components once at app startup
hugging_face_embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

vectorstore = Pinecone.from_existing_index(
    index_name="gen-ai", embedding=hugging_face_embeddings
)
retriever = vectorstore.as_retriever()
print("[+]  RETRIEVER Loaded")
llm = ChatGroq(
    temperature=0.7,
    model_name="llama-3.3-70b-versatile",
)
print("[+]  LLM Loaded")

# Create the folder if it doesn't exist
folder_name = "Documents"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Step 4 : Initailize FastApi
app = FastAPI()

#Step 5 Get an endpoint 

@app.get("/test")
def testing():
    msg="Deployment Response"
    return JSONResponse(content={"message": msg})


# POST endpoint to handle file ingestion
@app.post("/ingestion-pipeline")
async def upload_file(file: UploadFile = File(...)):
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file provided")

        # Check file type
        file_type = file.content_type
        if file_type != "application/pdf":
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

        # Generate unique filename BEFORE saving
        unique_filename = f"temp_pdf_{uuid.uuid4().hex}.pdf"
        file_path = os.path.join(folder_name, unique_filename)

        # Save uploaded file into Documents folder
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Load PDF
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        # Split into smaller chunks
        splitted_texts = text_splitter.split_documents(documents)

        # Insert into Pinecone Vector Database
        Pinecone.from_documents(
            splitted_texts, hugging_face_embeddings, index_name="gen-ai"
        )

        # Delete file after processing
        if os.path.exists(file_path):
            os.remove(file_path)

        return JSONResponse(
            content={"message": "Data ingested into vector database successfully."}
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# POST endpoint to query Pinecone (form-data version)
@app.post("/chatbot")
# async def query_vectorstore(query: str = Form(...)):
#     try:
#         if not query:
#             raise HTTPException(
#                 status_code=400, detail="Missing 'query' in request body"
#             )

#         # Set up QA chain
#         qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

#         result = qa.invoke({"query": query})

#         return JSONResponse(content={"results": result["result"]})

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
async def query_vectorstore(request: QueryRequest):
    try:
        query = request.query
        if not query:
            raise HTTPException(
                status_code=400, detail="Missing 'query' in request body"
            )

        # Set up QA chain
        qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

        result = qa.invoke({"query": query})

        return JSONResponse(content={"results": result["result"]})

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


