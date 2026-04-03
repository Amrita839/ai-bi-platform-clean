import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import google.generativeai as genai
import pandas as pd
from fpdf import FPDF
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
_key = os.getenv("GEMINI_API_KEY", "")
if _key:
    genai.configure(api_key=_key)


def generate_bi_report(df: pd.DataFrame, insights: dict) -> str:
    """Gemini se BI report generate karo"""

    prompt = f"""
You are a senior business analyst. Write a professional executive summary report.

Dataset info:
- Total rows: {df.shape[0]}
- Total columns: {df.shape[1]}
- Columns: {list(df.columns)}

Key statistics:
{df.describe().to_string()}

Write 3 paragraphs covering:
1. Data overview and key findings
2. Business insights and patterns
3. Recommendations

Use professional English. Be concise and data-driven.
"""
    try:
        model       = genai.GenerativeModel("gemini-1.5-flash")
        report_text = model.generate_content(prompt).text
    except Exception as e:
        report_text = (
            f"Business Intelligence Report\n\n"
            f"Total Records: {df.shape[0]}\n"
            f"Total Features: {df.shape[1]}\n"
            f"Columns: {', '.join(df.columns)}\n\n"
            f"Note: Gemini API error - {e}"
        )

    os.makedirs("reports", exist_ok=True)
    ts       = datetime.now().strftime("%Y%m%d_%H%M")
    pdf_path = f"reports/bi_report_{ts}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "AI Business Intelligence Report", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
    pdf.ln(4)
    pdf.set_font("Arial", "", 11)
    for line in report_text.split("\n"):
        pdf.multi_cell(0, 7, line.encode("latin-1", "replace").decode("latin-1"))
    pdf.output(pdf_path)

    xlsx_path = pdf_path.replace(".pdf", ".xlsx")
    df.to_excel(xlsx_path, index=False)

    print(f"✅ PDF   -> {pdf_path}")
    print(f"✅ Excel -> {xlsx_path}")
    return pdf_path


if __name__ == "__main__":
    import pandas as pd
    df = pd.read_csv("data/sample_data.csv")
    generate_bi_report(df, {})