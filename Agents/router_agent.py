import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, inspect
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError("GROQ_API_KEY not found in environment variables.")
os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# Database setup
DATABASE_PATH = "sqlite:///./customer_complaints.db"
engine = create_engine(DATABASE_PATH)

# Define structured output model
class RouteDecision(BaseModel):
    route: str = Field(
        description="Indicates whether the question is related to the database schema. 'db' for database else 'kb'."
    )

def get_database_schema() -> str:
    """Retrieve and format the database schema as a string."""
    inspector = inspect(engine)
    schema_lines = []
    
    for table_name in inspector.get_table_names():
        schema_lines.append(f"Table: {table_name}")
        for column in inspector.get_columns(table_name):
            col_type = str(column["type"])
            if column.get("primary_key"):
                col_type += ", Primary Key"
            if column.get("foreign_keys"):
                fk = list(column["foreign_keys"])[0]
                col_type += f", Foreign Key to {fk.column.table.name}.{fk.column.name}"
            schema_lines.append(f"- {column['name']}: {col_type}")
        schema_lines.append("")  # Blank line between tables
    
    schema = "\n".join(schema_lines)
    print("Retrieved database schema.")
    return schema

# Initialize LLM
groq_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)

def route_question(question: str) -> RouteDecision:
    """
    Determine if the question is related to the database ('db') or not ('kb').
    
    Returns:
        RouteDecision: Structured result with route info.
    """
    schema = get_database_schema()
    
    system_prompt = f"""You are an assistant that determines whether a given question is related to the following database schema.

Schema:
{schema}

Respond with only "db" if from database or "kb" if not from database.
"""
    human_prompt = f"Question: {question}"

    check_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", human_prompt),
        ]
    )

    structured_llm = groq_llm.with_structured_output(RouteDecision)
    relevance_checker = check_prompt | structured_llm

    result: RouteDecision = relevance_checker.invoke({})
    print(f"Relevance determined: {result.route}")
    return result
