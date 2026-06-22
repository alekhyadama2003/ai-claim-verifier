"""
Risk Scoring Engine
---------------------
Combines the outputs of the Image Analysis, Conversation Analysis, and
User History modules into a single weighted Fraud Risk Score (0-100).

Weighting:
    40% User History
    30% Conversation Analysis
    30% Image Analysis
"""

from typing import Dict

WEIGHT_USER_HISTORY = 0.40
WEIGHT_CONVERSATION = 0.30
WEIGHT_IMAGE = 0.30


def calculate_risk_score(
    user_history_result: Dict,
    conversation_result: Dict,
    image_result: Dict,
) -> Dict:
    """
    Combine module outputs into a final fraud risk score.

    Note:
        - user_history_result["risk_score"] is already a *risk* score (higher = riskier)
        - conversation_result["trust_score"] and image_result["reliability_score"]
          are *trust/reliability* scores (higher = safer), so they are inverted
          to a risk equivalent before weighting.

    Returns:
        dict with keys: fraud_risk_score, confidence_score, breakdown
    """
    user_history_risk = user_history_result.get("risk_score", 50)
    conversation_risk = 100 - conversation_result.get("trust_score", 50)
    image_risk = 100 - image_result.get("reliability_score", 50)

    fraud_risk_score = (
        user_history_risk * WEIGHT_USER_HISTORY
        + conversation_risk * WEIGHT_CONVERSATION
        + image_risk * WEIGHT_IMAGE
    )
    fraud_risk_score = round(max(0, min(100, fraud_risk_score)))

    confidence_score = _calculate_confidence(
        user_history_result, conversation_result, image_result
    )

    return {
        "fraud_risk_score": fraud_risk_score,
        "confidence_score": confidence_score,
        "breakdown": {
            "user_history_risk": round(user_history_risk, 1),
            "conversation_risk": round(conversation_risk, 1),
            "image_risk": round(image_risk, 1),
        },
    }


def _calculate_confidence(
    user_history_result: Dict, conversation_result: Dict, image_result: Dict
) -> int:
    """
    Confidence reflects how much usable data was available for the assessment.
    Missing images, empty transcripts, or brand-new users lower confidence,
    even if the resulting risk score looks clear-cut.
    """
    confidence = 100

    if image_result.get("is_missing"):
        confidence -= 30
    if user_history_result.get("total_claims", 0) == 0:
        confidence -= 20
    if conversation_result.get("consistency_ratio") is None:
        confidence -= 15

    return max(0, min(100, confidence))
