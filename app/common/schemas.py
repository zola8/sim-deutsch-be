from typing import List

from pydantic import BaseModel


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str


class CustomErrorResponse(BaseModel):
    success: bool = False
    error_code: str
    message: str
    details: List[ErrorDetail] = []
