import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import plotly.graph_objects as go


def run_forecasting(df: pd.DataFrame, target_col: str) -> dict:
    """
    Auto forecasting — target column select karo, model khud train hoga
    """
    print(f"🔄 Forecasting shuru for: {target_col}")

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    numeric_cols = [c for c in numeric_cols if c != target_col]

    if not numeric_cols:
        return {"success": False, "error": "Koi numeric features nahi hain!"}

    X = df[numeric_cols].fillna(0)
    y = df[target_col].fillna(0)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = XGBRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mae    = mean_absolute_error(y_test, y_pred)
    r2     = r2_score(y_test, y_pred)

    # Feature importance
    importance = dict(zip(numeric_cols, model.feature_importances_))
    importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))

    # Future forecast (next 5 periods)
    last_row    = X.iloc[-1:].copy()
    future_preds = []
    for i in range(5):
        pred = model.predict(last_row)[0]
        future_preds.append(round(float(pred), 2))

    print(f"✅ Forecasting done! R2: {r2:.4f}")

    return {
        "success":       True,
        "target":        target_col,
        "mae":           round(mae, 2),
        "r2_score":      round(r2, 4),
        "feature_importance": importance,
        "future_forecast":    future_preds,
        "actual":        y_test.tolist(),
        "predicted":     y_pred.tolist(),
    }


def get_forecast_fig(result: dict) -> go.Figure:
    """Forecast chart banao"""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        y=result["actual"],
        name="Actual",
        line=dict(color="#1D9E75")
    ))
    fig.add_trace(go.Scatter(
        y=result["predicted"],
        name="Predicted",
        line=dict(color="#E24B4A", dash="dash")
    ))
    fig.update_layout(title=f"Actual vs Predicted — {result['target']}")
    return fig