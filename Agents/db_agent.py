from typing import Dict, List
from sqlalchemy import create_engine, inspect, text
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser

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
# Schema tools
# -----------------------------
def get_table_names() -> List[str]:
    inspector = inspect(engine)
    return inspector.get_table_names()

def get_columns(table_name: str) -> Dict[str, str]:
    inspector = inspect(engine)
    return {col["name"]: str(col["type"]) for col in inspector.get_columns(table_name)}

def get_schema_text(table_name: str) -> str:
    cols = get_columns(table_name)
    return "\n".join([f'- "{col}" {ctype}' for col, ctype in cols.items()])

# -----------------------------
# Question Regeneration / Enrichment
# -----------------------------
SYNONYMS = {
    "Pakistan": ["Pakistan", "PK", "PAK"],
    "United Kingdom": ["United Kingdom", "UK", "GB"]
}

def regenerate_question(question: str) -> str:
    """Expand question with known synonyms and abbreviations."""
    for key, variants in SYNONYMS.items():
        if key.lower() in question.lower():
            variants_str = " or ".join(variants)
            question = question.replace(key, variants_str)
    return question

# -----------------------------
# DB Agent
# -----------------------------
def run_db_agent(question: str) -> Dict:
    state: Dict = {
        "question": question,
        "sql_query": "",
        "sql_error": False,
        "query_rows": [],
        "query_result": "",
        "answer": "",
    }

    # 1️⃣ Regenerate question
    enriched_question = regenerate_question(question)
    state["question"] = enriched_question
    print(f"[DB Agent] Enriched question: {enriched_question}")

    # 2️⃣ Generate SQL
    try:
        table_name = "customer_complaints"
        cols_block = get_schema_text(table_name)
        system_prompt = f"""
You are an assistant that converts natural language questions into SQL queries.
Database: "{table_name}"
Columns:
{cols_block}

Rules:
- Provide ONLY the SQL query, no explanations.
- Use LIKE statements for partial matches if needed.
"""
        convert_prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "Question: {question}")
        ])
        structured_llm = groq_llm.with_structured_output(ConvertToSQL)
        sql_generator = convert_prompt | structured_llm
        result = sql_generator.invoke({"question": enriched_question})
        sql_query = result.sql_query
        state["sql_query"] = sql_query
        print(f"[DB Agent] Generated SQL: {sql_query}")
    except Exception as e:
        state["sql_error"] = True
        state["query_result"] = f"Failed to generate SQL: {e}"
        state["answer"] = state["query_result"]
        return {"route": "db", "ok": False, **state}

    # 3️⃣ Execute SQL
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
        state["answer"] = state["query_result"]
        return {"route": "db", "ok": False, **state}

    # 4️⃣ Human-readable summary
    try:
        if state["query_rows"]:
            system_summary = """
You are a professional analyst. Convert SQL results into a narrative, story-like, executive summary.
Highlight key patterns, trends, duplicates, and actionable insights.
"""
            human_msg = f"SQL Query:\n{sql_query}\nResult:\n{state['query_result']}"
            summary_prompt = ChatPromptTemplate.from_messages([
                ("system", system_summary),
                ("human", human_msg)
            ])
            summary_llm = summary_prompt | groq_llm | StrOutputParser()
            state["answer"] = summary_llm.invoke({})
        else:
            state["answer"] = state["query_result"]
    except Exception as e:
        state["answer"] = state["query_result"]

    return {"route": "db", "ok": True, **state}
