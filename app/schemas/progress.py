from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ---------- Base ----------
class ProgressBase(BaseModel):
    completion_percentage: float = Field(default=0.0, ge=0.0, le=100.0)


# ---------- Update ----------
class ProgressUpdate(BaseModel):
    completion_percentage: float = Field(..., ge=0.0, le=100.0)


# ---------- Response ----------
class ProgressResponse(ProgressBase):
    id: int
    enrollment_id: int
    last_accessed: datetime

    class Config:
        from_attributes = True
