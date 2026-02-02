from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from app.common.enums import EnrollmentStatus


# ---------- REQUEST SCHEMAS ----------

class EnrollmentCreate(BaseModel):
    """
    Payload used when a student enrolls in a course.
    """
    course_id: int


class EnrollmentUpdate(BaseModel):
    """
    Used for unenrollment or status change if required later.
    """
    status: EnrollmentStatus


# ---------- RESPONSE SCHEMAS ----------

class EnrollmentResponse(BaseModel):
    """
    Returned after enrollment or when querying enrollment history.
    """
    id: int
    student_id: int
    course_id: int
    status: EnrollmentStatus
    enrolled_at: datetime
    unenrolled_at: Optional[datetime] = None

    class Config:
        from_attributes = True
