from __future__ import annotations

from pydantic import BaseModel


class MomentOut(BaseModel):
    id: int
    videoUrl: str
    title: str
    coverImage: str | None = None
