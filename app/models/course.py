from sqlalchemy import Column, Enum, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.common.enums import CourseCategory, CourseLevel
from app.database.base import Base



class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String, nullable=False, index=True)  # Ensure description is indexed for search efficiency


    category = Column(Enum(CourseCategory), nullable=False)
    level = Column(Enum(CourseLevel), nullable=False)

    is_published = Column(Boolean, default=False)

    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    instructor = relationship("User", back_populates="courses")
    enrollments = relationship("Enrollment", back_populates="course")
    reviews = relationship("Review", back_populates="course")
