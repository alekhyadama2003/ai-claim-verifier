"""
AI Claim Verifier - Entry Point
----------------------------------
Runs a single insurance claim through the full verification pipeline:

    Image Analysis + Conversation Analysis + User History
        --> Risk Scoring Engine
        --> Recommendation Engine

Usage:
    python main.py --claim_id C1024 --user_id U501 --amount 50000 \
        --description "Front bumper damage from a parking lot collision" \
        --image data/sample_claim.jpg \
        --conversation data/sample_conversation.txt \
        --history data/user_claim_history.csv
"""

import argparse
import json

from modules.claim_input import build_claim
from modules.image_analysis import analyze_image
from modules.conversation_analysis import analyze_conversation
from modules.user_history import analyze_user_history
from modules.risk_engine import calculate_risk_score
from modules.recommendation import get_recommendation


def run_pipeline(args: argparse.Namespace) -> dict:
    # Step 1: Build the structured claim object
    claim = build_claim(
        claim_id=args.claim_id,
        user_id=args.user_id,
        claim_amount=args.amount,
        claim_description=args.description,
        image_path=args.image,
        conversation_path=args.conversation,
    )

    # Step 2: Analyze image
    image_result = analyze_image(claim.image_path)

    # Step 3: Analyze conversation
    conversation_result = analyze_conversation(claim.claim_description, claim.conversation_path)

    # Step 4: Analyze user history
    user_history_result = analyze_user_history(claim.user_id, args.history)

    # Step 5 & 6: Calculate risk score + confidence
    risk_result = calculate_risk_score(user_history_result, conversation_result, image_result)

    # Step 7: Generate recommendation
    recommendation = get_recommendation(risk_result["fraud_risk_score"])

    return {
        "claim": claim.to_dict(),
        "image_analysis": image_result,
        "conversation_analysis": conversation_result,
        "user_history": user_history_result,
        "risk_assessment": risk_result,
        "recommendation": recommendation,
    }


def print_summary(result: dict) -> None:
    risk = result["risk_assessment"]
    rec = result["recommendation"]

    print("\n" + "=" * 50)
    print(" AI CLAIM VERIFIER - ASSESSMENT SUMMARY")
    print("=" * 50)
    print(f" Claim ID            : {result['claim']['claim_id']}")
    print(f" Fraud Risk Score    : {risk['fraud_risk_score']}%")
    print(f" Confidence Score    : {risk['confidence_score']}%")
    print(f" Recommendation      : {rec['label_emoji']} {rec['recommendation']}")
    print(f" Reason              : {rec['reason']}")
    print("=" * 50 + "\n")


def main():
    parser = argparse.ArgumentParser(description="AI Claim Verifier - Fraud Risk Assessment Pipeline")
    parser.add_argument("--claim_id", required=True, help="Unique claim identifier")
    parser.add_argument("--user_id", required=True, help="Unique user identifier")
    parser.add_argument("--amount", required=True, type=float, help="Claim amount")
    parser.add_argument("--description", required=True, help="Claim description text")
    parser.add_argument("--image", default=None, help="Path to the uploaded claim image")
    parser.add_argument("--conversation", default=None, help="Path to the conversation transcript (.txt)")
    parser.add_argument("--history", default="data/user_claim_history.csv", help="Path to user claim history CSV")
    parser.add_argument("--output", default=None, help="Optional path to save the full JSON report")

    args = parser.parse_args()
    result = run_pipeline(args)
    print_summary(result)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        print(f"Full report saved to: {args.output}")


if __name__ == "__main__":
    main()
