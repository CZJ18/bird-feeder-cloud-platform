from __future__ import annotations

from pydantic import BaseModel, Field


class LowConfidenceReviewIn(BaseModel):
    review_status: str = Field(pattern="^(approved|rejected)$")
    review_comment: str | None = None
