import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import plotly.express as px
from eda.auto_eda import run_auto_eda, get_correlation_fig, get_distribution_fig, get_missing_fig
from nlsql.engine import execute_nl_query
from models.forecasting import run_forecasting, get_forecast_fig
from models.churn import run_churn_prediction
from database.db_setup import init_db

init_db()

st.set_page_config(
    page_title="AI BI Platform",
    page_icon="🧠",
    layout="wide"
)

st.title("🧠 AI-Powered Business Intelligence Platform")
st.markdown("**Auto EDA + NL-to-SQL + Forecasting + Churn Prediction** | Powered by Gemini AI")

# ── Session state ──
if "df" not in st.session_state:
    st.session_state.df = None

# ── Sidebar: File Upload ──
st.sidebar.header("📁 Data Upload")
uploaded = st.sidebar.file_uploader("CSV ya Excel upload karo", type=["csv", "xlsx"])

if uploaded:
    if uploaded.name.endswith(".csv"):
        st.session_state.df = pd.read_csv(uploaded)
    else:
        st.session_state.df = pd.read_excel(uploaded)
    st.sidebar.success(f"✅ {uploaded.name} loaded! ({st.session_state.df.shape[0]} rows)")

# Demo data button
if st.sidebar.button("📊 Demo Data Load Karo"):
    st.session_state.df = pd.read_csv("data/sample_data.csv")
    st.sidebar.success("✅ Demo data loaded!")

df = st.session_state.df

# ── TABS ──
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Auto EDA",
    "💬 NL Query",
    "📈 Forecasting",
    "👥 Churn Prediction"
])

# ════════════════════════════════
# TAB 1: AUTO EDA
# ════════════════════════════════
with tab1:
    st.header("📊 Automatic Exploratory Data Analysis")

    if df is None:
        st.info("👈 Pehle sidebar se CSV/Excel upload karo ya Demo Data load karo!")
    else:
        eda = run_auto_eda(df)

        # Metrics
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Rows",    eda["shape"][0])
        c2.metric("Total Columns", eda["shape"][1])
        c3.metric("Missing Values", sum(eda["missing"].values()))
        c4.metric("Duplicates",    eda["duplicates"])

        st.subheader("📋 Data Preview")
        st.dataframe(df.head(10), use_container_width=True)

        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("🔥 Correlation Heatmap")
            fig = get_correlation_fig(df)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Numeric columns kam hain")

        with col_b:
            st.subheader("📉 Missing Values")
            fig2 = get_missing_fig(df)
            if fig2:
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.success("✅ Koi missing values nahi!")

        st.subheader("📊 Column Distribution")
        col = st.selectbox("Column select karo", df.columns.tolist())
        if col:
            st.plotly_chart(get_distribution_fig(df, col), use_container_width=True)

# ════════════════════════════════
# TAB 2: NL QUERY
# ════════════════════════════════
with tab2:
    st.header("💬 Natural Language to SQL Query")

    if df is None:
        st.info("👈 Pehle sidebar se data upload karo!")
    else:
        st.markdown("**Plain English mein poochho — AI SQL generate karega!**")

        examples = [
            "Show me top 5 customers with highest monthly charges",
            "How many customers have churned?",
            "What is the average age of churned customers?",
            "Show customers with tenure less than 3 months",
        ]

        st.markdown("**Example questions:**")
        for ex in examples:
            if st.button(f"💡 {ex}"):
                st.session_state.nl_question = ex

        question = st.text_input(
            "Apna question likho:",
            value=st.session_state.get("nl_question", ""),
            placeholder="e.g. Show me customers who churned last month"
        )

        if st.button("🔍 Query Karo") and question:
            with st.spinner("Gemini SQL generate kar raha hai..."):
                result = execute_nl_query(question, df)

            if result["success"]:
                st.success("✅ Query successful!")
                st.code(result["sql"], language="sql")
                st.dataframe(result["data"], use_container_width=True)
            else:
                st.error(f"❌ Error: {result['error']}")

# ════════════════════════════════
# TAB 3: FORECASTING
# ════════════════════════════════
with tab3:
    st.header("📈 Auto Forecasting")

    if df is None:
        st.info("👈 Pehle sidebar se data upload karo!")
    else:
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        target = st.selectbox("Forecast karna hai kaunsa column?", numeric_cols)

        if st.button("🚀 Forecast Karo"):
            with st.spinner("XGBoost model train ho raha hai..."):
                result = run_forecasting(df, target)

            if result["success"]:
                col1, col2, col3 = st.columns(3)
                col1.metric("R² Score", result["r2_score"])
                col2.metric("MAE",      result["mae"])
                col3.metric("Target",   result["target"])

                st.plotly_chart(get_forecast_fig(result), use_container_width=True)

                st.subheader("🔮 Next 5 Periods Forecast")
                forecast_df = pd.DataFrame({
                    "Period":   [f"Period +{i+1}" for i in range(5)],
                    "Forecast": result["future_forecast"]
                })
                st.dataframe(forecast_df, use_container_width=True)

                st.subheader("🎯 Feature Importance")
                imp_df = pd.DataFrame(
                    list(result["feature_importance"].items()),
                    columns=["Feature", "Importance"]
                )
                st.plotly_chart(
                    px.bar(imp_df, x="Feature", y="Importance", title="Feature Importance"),
                    use_container_width=True
                )
            else:
                st.error(result["error"])

# ════════════════════════════════
# TAB 4: CHURN PREDICTION
# ════════════════════════════════
with tab4:
    st.header("👥 Churn Prediction")

    if df is None:
        st.info("👈 Pehle sidebar se data upload karo!")
    else:
        churn_col = st.text_input("Churn column ka naam:", value="Churned")

        if st.button("🔍 Churn Analysis Karo"):
            with st.spinner("Churn model train ho raha hai..."):
                result = run_churn_prediction(df, churn_col)

            if result["success"]:
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Accuracy",       result["accuracy"])
                c2.metric("AUC-ROC",        result["auc_roc"])
                c3.metric("High Risk",      result["high_risk_count"])
                c4.metric("Churn Rate",     result["churn_rate"])

                risk_df = pd.DataFrame(result["risk_data"])
                counts  = risk_df["churn_risk"].value_counts()
                st.plotly_chart(
                    px.pie(
                        values=counts.values,
                        names=counts.index,
                        title="Customer Risk Distribution",
                        color_discrete_map={
                            "High":   "#E24B4A",
                            "Medium": "#EF9F27",
                            "Low":    "#1D9E75"
                        }
                    ),
                    use_container_width=True
                )
            else:
                st.error(result["error"])