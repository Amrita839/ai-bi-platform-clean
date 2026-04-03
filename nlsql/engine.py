import pandas as pd
import google.generativeai as genai
import os
import re
from dotenv import load_dotenv

load_dotenv()

_key = os.getenv("GEMINI_API_KEY", "")
if _key:
    genai.configure(api_key=_key)


def nl_to_sql(question: str, df: pd.DataFrame) -> dict:
    """
    Natural Language ko SQL mein convert karo using Gemini
    """
    # Table schema banao
    schema = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        schema.append(f"{col} ({dtype})")
    schema_str = ", ".join(schema)

    prompt = f"""
You are an expert SQL generator. Convert the natural language question to SQL.

Table name: uploaded_data
Columns: {schema_str}

Sample data (first 3 rows):
{df.head(3).to_string()}

Question: {question}

Rules:
1. Return ONLY the SQL query — no explanation
2. Use standard SQLite syntax
3. Table name is always: uploaded_data
4. Keep it simple and accurate

SQL:
"""
    try:
        model    = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        sql      = response.text.strip()
        sql      = re.sub(r"```sql|```", "", sql).strip()
        return {"success": True, "sql": sql, "error": None}
    except Exception as e:
        return {"success": False, "sql": None, "error": str(e)}


def execute_nl_query(question: str, df: pd.DataFrame) -> dict:
    """
    NL question → SQL → Execute → Result return karo
    """
    # SQL generate karo
    result = nl_to_sql(question, df)

    if not result["success"]:
        return {
            "success":  False,
            "question": question,
            "sql":      None,
            "data":     None,
            "error":    result["error"]
        }

    sql = result["sql"]

    # Execute karo using pandas
    try:
        import sqlite3
        conn = sqlite3.connect(":memory:")
        df.to_sql("uploaded_data", conn, if_exists="replace", index=False)
        result_df = pd.read_sql_query(sql, conn)
        conn.close()

        return {
            "success":  True,
            "question": question,
            "sql":      sql,
            "data":     result_df,
            "error":    None
        }
    except Exception as e:
        return {
            "success":  False,
            "question": question,
            "sql":      sql,
            "data":     None,
            "error":    str(e)
        }