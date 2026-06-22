from __future__ import annotations

import secrets

from fastapi import Header, HTTPException, status

from app.config import settings


async def require_api_token(x_api_token: str | None = Header(default=None)) -> None:
    """Validate the static dashboard API token for /api/* routes."""
    expected = settings.dashboard_api_token
    if not x_api_token or not secrets.compare_digest(x_api_token, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid api token",
        )
