from typing import Dict
from sqlalchemy import create_engine, text
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# -----------------------------
# Database setup
# -----------------------------
DATABASE_PATH = "sqlite:///./customer_complaints.db"
engine = create_engine(DATABASE_PATH)

# -----------------------------
# Groq LLM setup
# -----------------------------
groq_llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.0)

# -----------------------------
# Structured SQL output
# -----------------------------
class ConvertToSQL(BaseModel):
    sql_query: str = Field(description="SQL query generated from the user's natural language question.")

# -----------------------------
# Hardcoded table/column info
# -----------------------------
description = {
    "Gender": "The gender of the customer, typically Male or Female.",
    "Age": "The age of the customer in completed years.",
    "first_name": "First of the customer.",
    "last_name": "First of the customer.",
    "Address": "Residential address including city and postal code.",
    "Email": "Customer email for communication.",
    "Complaint": "Detailed description of the reported issue.",
    "Security Question": "Pre-selected security question for identity verification.",
    "Security Answer": "Answer to the security question.",
    "Complaint Resolved": "Indicates if the complaint was resolved (Yes/No)."
}

# -----------------------------
# DB Agent
# -----------------------------
def run_db_agent(question: str) -> Dict:
    state: Dict = {"question": question, "sql_error": False, "query_rows": [], "query_result": ""}

    # 1️⃣ Convert NL question to SQL
    try:
        cols_block = "\n".join([f'- "{col}" {desc}' for col, desc in description.items()])
        system_prompt = f"""
You are an assistant that converts natural language questions into SQL queries.
Database: "customer_complaints"
Table: "customer_complaints"
Columns:
{cols_block}

Rules:
- Provide ONLY the SQL query, no explanations.
- Do not modify column names.
"""
        convert_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Question: {question}")
        ])
        structured_llm = groq_llm.with_structured_output(ConvertToSQL)
        sql_generator = convert_prompt | structured_llm
        result = sql_generator.invoke({"question": question})
        sql_query = result.sql_query
        state["sql_query"] = sql_query
        print(f"[DB Agent] Generated SQL: {sql_query}")
    except Exception as e:
        return {"route": "db", "ok": False, "answer": f"Failed to generate SQL: {e}"}

    # 2️⃣ Execute SQL
    try:
        with engine.connect() as conn:
            res = conn.execute(text(sql_query))
            if sql_query.strip().lower().startswith("select"):
                rows = res.fetchall()
                cols = res.keys()
                state["query_rows"] = [dict(zip(cols, row)) for row in rows]
                if rows:
                    header = ", ".join(cols)
                    formatted = "; ".join([", ".join([f"{k}: {v}" for k, v in row.items()]) for row in state["query_rows"]])
                    state["query_result"] = f"{header}\n{formatted}"
                else:
                    state["query_result"] = "No results found."
            else:
                conn.commit()
                state["query_result"] = "Action completed successfully."
        state["sql_error"] = False
    except Exception as e:
        state["query_result"] = f"Error executing SQL: {e}"
        state["sql_error"] = True

    # 3️⃣ Human-readable summary (optional)
    if not state["sql_error"] and sql_query.strip().lower().startswith("select"):
        system_summary = """
You are a professional analyst. Convert SQL results into a concise, executive summary.
Focus on trends, metrics, and actionable insights.
"""
        human_msg = f"SQL Query:\n{sql_query}\nResult:\n{state['query_result']}"
        summary_prompt = ChatPromptTemplate.from_messages([
            ("system", system_summary),
            ("human", human_msg)
        ])
        try:
            from langchain_core.schema import StrOutputParser
            summary_llm = summary_prompt | groq_llm | StrOutputParser()
            state["answer"] = summary_llm.invoke({})
        except Exception:
            state["answer"] = state["query_result"]
    else:
        state["answer"] = state["query_result"]

    return {"route": "db", "ok": True, **state}
