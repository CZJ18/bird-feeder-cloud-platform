from __future__ import annotations

from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: T


class OkResponse(BaseModel, Generic[T]):
    ok: bool = True
    message: str = "success"
    data: T


def api_success(data: T, message: str = "success") -> dict[str, object]:
    return {"code": 200, "message": message, "data": data}


def ok_success(data: T, message: str = "success") -> dict[str, object]:
    return {"ok": True, "message": message, "data": data}
