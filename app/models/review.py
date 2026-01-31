from sqlalchemy import CheckConstraint, Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.base import Base



class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)
    __table_args__ = (CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),)  # Ensure rating is between 1 and 5

    comment = Column(String, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("User", back_populates="reviews")
    course = relationship("Course", back_populates="reviews")
