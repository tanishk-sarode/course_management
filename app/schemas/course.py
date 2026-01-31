from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.common.enums import CourseCategory, CourseLevel


# ---------- Base ----------
class CourseBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: str = Field(..., min_length=10)
    category: CourseCategory
    level: CourseLevel


# ---------- Create ----------
class CourseCreate(CourseBase):
    """
    Instructor identity is derived from the JWT, not the payload.
    """
    pass



# ---------- Update ----------
class CourseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[CourseCategory] = None
    level: Optional[CourseLevel] = None
    is_published: Optional[bool] = None


# ---------- Response ----------
class CourseResponse(CourseBase):
    id: int
    instructor_id: int
    is_published: bool
    created_at: datetime

    class Config:
        orm_mode = True
# ---------- List ----------
class CourseListResponse(BaseModel):
    courses: list[CourseResponse]
    total: int

    class Config:
        orm_mode = True