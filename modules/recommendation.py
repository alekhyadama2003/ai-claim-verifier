"""
Recommendation Engine
------------------------
Converts a Fraud Risk Score into a final, actionable recommendation.

Thresholds:
    0-30      Approve
    31-60     Manual Review
    61-100    High Fraud Risk
"""

from typing import Dict

APPROVE_THRESHOLD = 30
MANUAL_REVIEW_THRESHOLD = 60


def get_recommendation(fraud_risk_score: int) -> Dict:
    """
    Map a fraud risk score to a recommendation label and short rationale.

    Returns:
        dict with keys: recommendation, label_emoji, reason
    """
    if fraud_risk_score <= APPROVE_THRESHOLD:
        return {
            "recommendation": "Approve",
            "label_emoji": "✅",
            "reason": "Low fraud indicators across image, conversation, and history checks.",
        }
    elif fraud_risk_score <= MANUAL_REVIEW_THRESHOLD:
        return {
            "recommendation": "Manual Review",
            "label_emoji": "⚠️",
            "reason": "Moderate fraud indicators detected; human review recommended before approval.",
        }
    else:
        return {
            "recommendation": "High Fraud Risk",
            "label_emoji": "🚨",
            "reason": "Strong fraud indicators detected across one or more analysis modules.",
        }
