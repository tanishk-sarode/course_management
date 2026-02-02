from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.progress import ProgressResponse, ProgressUpdate
from app.models.progress import Progress
from app.models.enrollment import Enrollment
from app.models.user import User
from app.core.dependencies import get_current_user, require_student
from app.common.enums import RoleEnum, EnrollmentStatus

router = APIRouter(prefix="/progress", tags=["Progress"])


@router.get("/my-progress", response_model=List[ProgressResponse])
async def get_my_progress(
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Get progress for all of current student's enrollments.
    """
    # Get all active enrollments for the student
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.status == EnrollmentStatus.active
    ).all()
    
    enrollment_ids = [e.id for e in enrollments]
    
    # Get progress records for these enrollments
    progress_records = db.query(Progress).filter(
        Progress.enrollment_id.in_(enrollment_ids)
    ).all()
    
    return progress_records


@router.get("/enrollment/{enrollment_id}", response_model=ProgressResponse)
async def get_enrollment_progress(
    enrollment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get progress for a specific enrollment.
    Students can only see their own progress, instructors can see any student's progress.
    """
    # Get enrollment
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    # Check authorization
    if current_user.role == RoleEnum.student and enrollment.student_id != current_user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own progress"
        )
    
    # Get progress
    progress = db.query(Progress).filter(Progress.enrollment_id == enrollment_id).first()
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress record not found"
        )
    
    return progress


@router.put("/enrollment/{enrollment_id}", response_model=ProgressResponse)
async def update_progress(
    enrollment_id: int,
    progress_update: ProgressUpdate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Update progress for a specific enrollment.
    Only the enrolled student can update their progress.
    """
    # Get enrollment
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    # Check if enrollment belongs to current user
    if enrollment.student_id != current_user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own progress"
        )
    
    # Check if enrollment is active
    if enrollment.status != EnrollmentStatus.active:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update progress for inactive enrollment"
        )
    
    # Get or create progress record
    progress = db.query(Progress).filter(Progress.enrollment_id == enrollment_id).first()
    if not progress:
        # Create new progress record if it doesn't exist
        progress = Progress(
            enrollment_id=enrollment_id,
            completion_percentage=progress_update.completion_percentage
        )
        db.add(progress)
    else:
        # Update existing progress
        progress.completion_percentage = progress_update.completion_percentage  # type: ignore
    
    # Mark enrollment as completed if progress reaches 100%
    if progress_update.completion_percentage >= 100.0:
        enrollment.status = EnrollmentStatus.completed  # type: ignore
    
    db.commit()
    db.refresh(progress)
    
    return progress


@router.get("/course/{course_id}", response_model=List[ProgressResponse])
async def get_course_progress(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get progress for all enrollments in a specific course.
    Only the course instructor can access this.
    """
    # Get all enrollments for the course
    enrollments = db.query(Enrollment).filter(Enrollment.course_id == course_id).all()
    
    if not enrollments:
        return []
    
    # Verify instructor authorization
    if current_user.role == RoleEnum.instructor:  # type: ignore
        # Check if current user is the course instructor
        course_instructor_id = enrollments[0].course.instructor_id
        if course_instructor_id != current_user.id:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view progress for your own courses"
            )
    elif current_user.role == RoleEnum.student:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Students cannot view course-wide progress"
        )
    
    enrollment_ids = [e.id for e in enrollments]
    
    # Get progress records
    progress_records = db.query(Progress).filter(
        Progress.enrollment_id.in_(enrollment_ids)
    ).all()
    
    return progress_records
