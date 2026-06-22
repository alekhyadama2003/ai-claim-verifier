"""
Claim Input Module
-------------------
Collects and structures all incoming claim data (claim details, image path,
conversation transcript, and user information) into a single, validated
ClaimRecord object that downstream modules can consume.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class ClaimRecord:
    """Structured representation of a single insurance claim."""

    claim_id: str
    user_id: str
    claim_amount: float
    claim_description: str
    image_path: Optional[str] = None
    conversation_path: Optional[str] = None
    submitted_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def is_valid(self) -> bool:
        """Basic sanity check that the minimum required fields are present."""
        return bool(
            self.claim_id
            and self.user_id
            and self.claim_amount is not None
            and self.claim_amount >= 0
            and self.claim_description
        )

    def to_dict(self) -> dict:
        return {
            "claim_id": self.claim_id,
            "user_id": self.user_id,
            "claim_amount": self.claim_amount,
            "claim_description": self.claim_description,
            "image_path": self.image_path,
            "conversation_path": self.conversation_path,
            "submitted_at": self.submitted_at,
        }


def build_claim(
    claim_id: str,
    user_id: str,
    claim_amount: float,
    claim_description: str,
    image_path: Optional[str] = None,
    conversation_path: Optional[str] = None,
) -> ClaimRecord:
    """Factory function that builds and validates a ClaimRecord."""
    claim = ClaimRecord(
        claim_id=claim_id,
        user_id=user_id,
        claim_amount=claim_amount,
        claim_description=claim_description,
        image_path=image_path,
        conversation_path=conversation_path,
    )

    if not claim.is_valid():
        raise ValueError(f"Claim {claim_id} is missing required fields.")

    return claim
