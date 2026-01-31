from sqlalchemy import CheckConstraint, Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), unique=True)
    completion_percentage = Column(Float, default=0.0)
    last_accessed = Column(DateTime(timezone=True), server_default=func.now())

    enrollment = relationship("Enrollment")

    def __repr__(self):
        return f"<Progress(id={self.id}, enrollment_id={self.enrollment_id}, completion_percentage={self.completion_percentage})>"
    
    def __table_args__(self):
        return (
            CheckConstraint('completion_percentage >= 0.0 AND completion_percentage <= 100.0', name='chk_completion_percentage_range'),
        )