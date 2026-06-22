"""
User History Module
---------------------
Analyzes a user's previous claim behavior using historical claim records.

Checks performed:
    - Past claim count
    - Rejected claims
    - Manual review frequency
    - Acceptance ratio

Output:
    Historical Risk Score (0-100, higher = riskier)
"""

import os
from typing import Dict

import pandas as pd


REQUIRED_COLUMNS = {"user_id", "status"}  # status: approved | rejected | manual_review


def _load_history(history_csv_path: str) -> pd.DataFrame:
    if not history_csv_path or not os.path.exists(history_csv_path):
        return pd.DataFrame(columns=list(REQUIRED_COLUMNS))

    df = pd.read_csv(history_csv_path)
    missing_cols = REQUIRED_COLUMNS - set(df.columns)
    if missing_cols:
        raise ValueError(f"History file is missing required columns: {missing_cols}")
    return df


def analyze_user_history(user_id: str, history_csv_path: str) -> Dict:
    """
    Analyze a user's claim history and return a historical risk report.

    Returns:
        dict with keys: risk_score, total_claims, rejected_claims,
        manual_review_claims, acceptance_ratio
    """
    df = _load_history(history_csv_path)
    user_claims = df[df["user_id"] == user_id]

    total_claims = len(user_claims)

    if total_claims == 0:
        # New users default to a moderate-neutral risk score
        return {
            "risk_score": 40,
            "total_claims": 0,
            "rejected_claims": 0,
            "manual_review_claims": 0,
            "acceptance_ratio": None,
        }

    rejected = len(user_claims[user_claims["status"] == "rejected"])
    manual_review = len(user_claims[user_claims["status"] == "manual_review"])
    approved = len(user_claims[user_claims["status"] == "approved"])

    acceptance_ratio = approved / total_claims

    # Risk increases with rejection rate, manual-review frequency, and claim volume
    rejection_rate = rejected / total_claims
    review_rate = manual_review / total_claims
    volume_penalty = min(total_claims, 10) * 1.5  # frequent filers carry slightly more risk

    risk_score = (rejection_rate * 60) + (review_rate * 25) + volume_penalty
    risk_score = max(0, min(100, round(risk_score)))

    return {
        "risk_score": risk_score,
        "total_claims": total_claims,
        "rejected_claims": rejected,
        "manual_review_claims": manual_review,
        "acceptance_ratio": round(acceptance_ratio, 2),
    }
