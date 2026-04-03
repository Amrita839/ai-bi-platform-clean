import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def run_auto_eda(df: pd.DataFrame) -> dict:
    """
    Automatic EDA — CSV upload hone ke baad ye sab automatically hoga
    """
    print("🔄 Auto EDA shuru...")

    results = {}

    # Basic info
    results["shape"]        = df.shape
    results["columns"]      = list(df.columns)
    results["dtypes"]       = df.dtypes.astype(str).to_dict()
    results["missing"]      = df.isnull().sum().to_dict()
    results["missing_pct"]  = (df.isnull().sum() / len(df) * 100).round(2).to_dict()
    results["duplicates"]   = int(df.duplicated().sum())

    # Numeric columns stats
    numeric_df = df.select_dtypes(include=[np.number])
    if not numeric_df.empty:
        results["describe"] = numeric_df.describe().round(2).to_dict()

    # Categorical columns
    cat_df = df.select_dtypes(include=["object"])
    results["categorical"] = {}
    for col in cat_df.columns:
        results["categorical"][col] = df[col].value_counts().head(5).to_dict()

    print("✅ Auto EDA complete!")
    return results


def get_correlation_fig(df: pd.DataFrame):
    """Correlation heatmap banao"""
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.shape[1] < 2:
        return None
    corr = numeric_df.corr().round(2)
    fig  = px.imshow(
        corr,
        title="Correlation Heatmap",
        color_continuous_scale="RdBu",
        aspect="auto"
    )
    return fig


def get_distribution_fig(df: pd.DataFrame, column: str):
    """Column ka distribution plot"""
    if df[column].dtype in [np.float64, np.int64]:
        fig = px.histogram(df, x=column, title=f"{column} Distribution")
    else:
        counts = df[column].value_counts().reset_index()
        counts.columns = [column, "count"]
        fig = px.bar(counts, x=column, y="count", title=f"{column} Distribution")
    return fig


def get_missing_fig(df: pd.DataFrame):
    """Missing values chart"""
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if missing.empty:
        return None
    fig = px.bar(
        x=missing.index,
        y=missing.values,
        title="Missing Values per Column",
        labels={"x": "Column", "y": "Missing Count"}
    )
    return fig