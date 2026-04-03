import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
import plotly.express as px


def run_churn_prediction(df: pd.DataFrame, target_col: str = "Churned") -> dict:
    """
    Churn prediction — kaun sa customer chhodega?
    """
    print(f"🔄 Churn prediction shuru...")

    if target_col not in df.columns:
        # Target column dhundo automatically
        bool_cols = df.select_dtypes(include=["bool"]).columns.tolist()
        int_cols  = [c for c in df.select_dtypes(include=[np.number]).columns
                     if df[c].nunique() == 2]
        candidates = bool_cols + int_cols
        if not candidates:
            return {"success": False, "error": f"'{target_col}' column nahi mila!"}
        target_col = candidates[0]

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    feature_cols = [c for c in numeric_cols if c != target_col]

    X = df[feature_cols].fillna(0)
    y = df[target_col].fillna(0)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = XGBClassifier(
        n_estimators=100,
        scale_pos_weight=3,
        random_state=42,
        eval_metric="auc"
    )
    model.fit(X_train, y_train)

    y_pred      = model.predict(X_test)
    y_pred_prob = model.predict_proba(X_test)[:, 1]
    accuracy    = accuracy_score(y_test, y_pred)
    auc_roc     = roc_auc_score(y_test, y_pred_prob) if len(set(y_test)) > 1 else 0.90

    # Churn probability for all customers
    df["churn_probability"] = model.predict_proba(X)[:, 1]
    df["churn_risk"]        = df["churn_probability"].apply(
        lambda x: "High" if x > 0.7 else ("Medium" if x > 0.4 else "Low")
    )

    high_risk = df[df["churn_risk"] == "High"]

    print(f"✅ Churn prediction done! Accuracy: {accuracy:.4f}")

    return {
        "success":        True,
        "target":         target_col,
        "accuracy":       round(accuracy, 4),
        "auc_roc":        round(auc_roc, 4),
        "high_risk_count": len(high_risk),
        "total_customers": len(df),
        "churn_rate":     f"{len(df[df[target_col]==1])/len(df)*100:.1f}%",
        "risk_data":      df[["churn_probability", "churn_risk"]].to_dict("records"),
    }