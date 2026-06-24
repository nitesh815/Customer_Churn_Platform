"""
Phase 14: Batch Churn Scorer
Customer Churn Prediction & Analytics Platform

Loads the CLV-enriched dataset, retrains Logistic Regression on the full
dataset (same spec as Phase 9), then scores every customer and exports a
CSV with churn probability, binary prediction, and segment label.
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CLV_CSV = os.path.join(ROOT, "data", "processed", "telco_customer_churn_clv.csv")
OUTPUT_CSV = os.path.join(ROOT, "data", "processed", "customer_churn_scores.csv")

# Features used in Phase 9 training (subset that avoids data leakage)
FEATURE_COLS = [
    "tenure_normalized",
    "MonthlyCharges_normalized",
    "TotalCharges_normalized",
    "Contract_encoded",
    "SeniorCitizen",
    "is_new_customer_0_6m",
    "is_long_tenure_48m",
    "is_month_to_month",
    "is_auto_pay",
    "is_electronic_check",
    "addon_count",
    "security_bundle",
    "charges_per_tenure_month",
    "tenure_x_monthlycharges",
    "new_x_fiber",
    "internet_addon_adoption_rate",
]

TARGET_COL = "Churn_encoded"
CHURN_THRESHOLD = 0.40   # probability cutoff for binary prediction


def load_data(clv_csv: str) -> pd.DataFrame:
    df = pd.read_csv(clv_csv)
    missing = [c for c in FEATURE_COLS + [TARGET_COL] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in input: {missing}")
    return df


def train_scorer(df: pd.DataFrame):
    """Train Logistic Regression on the full dataset for scoring."""
    X = df[FEATURE_COLS].fillna(0)
    y = df[TARGET_COL]

    model = Pipeline([
        ("scaler", StandardScaler()),
        ("lr", LogisticRegression(max_iter=1000, random_state=42, C=1.0)),
    ])
    model.fit(X, y)
    return model


def score_customers(df: pd.DataFrame, model) -> pd.DataFrame:
    """Return scored DataFrame with churn probability and prediction."""
    X = df[FEATURE_COLS].fillna(0)
    proba = model.predict_proba(X)[:, 1]
    pred = (proba >= CHURN_THRESHOLD).astype(int)

    # Risk tier
    def tier(p):
        if p >= 0.60:
            return "Critical"
        elif p >= 0.40:
            return "High"
        elif p >= 0.20:
            return "Medium"
        else:
            return "Low"

    scored = pd.DataFrame({
        "customerID": df["customerID"] if "customerID" in df.columns else df.index.astype(str),
        "churn_probability": np.round(proba, 4),
        "churn_predicted": pred,
        "risk_tier": [tier(p) for p in proba],
        "segment_label": df["segment_label"] if "segment_label" in df.columns else "Unknown",
        "discounted_lifetime_value": df["discounted_lifetime_value"].round(2) if "discounted_lifetime_value" in df.columns else np.nan,
        "actual_churn": df[TARGET_COL],
    })

    return scored.sort_values("churn_probability", ascending=False).reset_index(drop=True)


def print_summary(scored: pd.DataFrame):
    n = len(scored)
    pred_churners = scored["churn_predicted"].sum()
    print(f"  Total customers scored : {n:,}")
    print(f"  Predicted churners     : {pred_churners:,} ({pred_churners/n*100:.1f}%)")
    for tier in ["Critical", "High", "Medium", "Low"]:
        ct = (scored["risk_tier"] == tier).sum()
        print(f"  {tier:<10} risk tier : {ct:,}")


def run_scoring(clv_csv: str = CLV_CSV, output_csv: str = OUTPUT_CSV):
    print("Loading CLV dataset...")
    df = load_data(clv_csv)
    print(f"  Records loaded: {len(df):,}")

    print("Training scorer (Logistic Regression, full dataset)...")
    model = train_scorer(df)

    print("Scoring all customers...")
    scored = score_customers(df, model)

    print_summary(scored)

    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    scored.to_csv(output_csv, index=False)
    print(f"✓ Scored customer file written to: {output_csv}")
    return scored


if __name__ == "__main__":
    run_scoring()
