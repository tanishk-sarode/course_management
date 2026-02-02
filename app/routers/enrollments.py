from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.enrollment import EnrollmentCreate, EnrollmentResponse, EnrollmentUpdate
from app.models.enrollment import Enrollment
from app.models.course import Course
from app.models.user import User
from app.models.progress import Progress
from app.core.dependencies import get_current_user, require_student
from app.common.enums import RoleEnum, EnrollmentStatus

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def enroll_in_course(
    enrollment_data: EnrollmentCreate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Enroll current student in a course.
    """
    # Check if course exists and is published
    course = db.query(Course).filter(Course.id == enrollment_data.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    if not course.is_published:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot enroll in unpublished course"
        )
    
    # Check if already enrolled
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id,
        Enrollment.course_id == enrollment_data.course_id
    ).first()
    
    if existing_enrollment:
        if existing_enrollment.status == EnrollmentStatus.active:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already enrolled in this course"
            )
        else:
            # Reactivate enrollment
            existing_enrollment.status = EnrollmentStatus.active  # type: ignore
            db.commit()
            db.refresh(existing_enrollment)
            return existing_enrollment
    
    # Create new enrollment
    new_enrollment = Enrollment(
        student_id=current_user.id,
        course_id=enrollment_data.course_id,
        status=EnrollmentStatus.active
    )
    
    db.add(new_enrollment)
    db.commit()
    db.refresh(new_enrollment)
    
    # Create progress record
    progress = Progress(
        enrollment_id=new_enrollment.id,
        completion_percentage=0.0
    )
    db.add(progress)
    db.commit()
    
    return new_enrollment


@router.get("/my-enrollments", response_model=List[EnrollmentResponse])
async def get_my_enrollments(
    status_filter: EnrollmentStatus | None = None,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Get current student's enrollments.
    """
    query = db.query(Enrollment).filter(Enrollment.student_id == current_user.id)
    
    if status_filter:
        query = query.filter(Enrollment.status == status_filter)
    
    enrollments = query.all()
    return enrollments


@router.get("/course/{course_id}", response_model=List[EnrollmentResponse])
async def get_course_enrollments(
    course_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all enrollments for a specific course.
    Only instructors can see enrollments for their courses.
    """
    # Verify course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if user is the course instructor
    if current_user.role == RoleEnum.instructor and course.instructor_id != current_user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view enrollments for your own courses"
        )
    
    enrollments = db.query(Enrollment).filter(Enrollment.course_id == course_id).all()
    return enrollments


@router.put("/{enrollment_id}", response_model=EnrollmentResponse)
async def update_enrollment(
    enrollment_id: int,
    enrollment_update: EnrollmentUpdate,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Update enrollment status (e.g., unenroll by changing status to 'dropped').
    """
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
            detail="You can only update your own enrollments"
        )
    
    enrollment.status = enrollment_update.status  # type: ignore
    db.commit()
    db.refresh(enrollment)
    
    return enrollment


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unenroll_from_course(
    enrollment_id: int,
    current_user: User = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Unenroll from a course (soft delete by changing status to 'dropped').
    """
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
            detail="You can only unenroll from your own courses"
        )
    
    # Change status to dropped instead of deleting
    enrollment.status = EnrollmentStatus.dropped  # type: ignore
    db.commit()
    
    return None


@router.get("/student/{student_id}", response_model=List[EnrollmentResponse])
async def get_student_enrollments(
    student_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get enrollment history for a specific student.
    Students can only see their own history, instructors can see any student's history.
    """
    # Students can only see their own enrollments
    if current_user.role == RoleEnum.student and current_user.id != student_id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own enrollment history"
        )
    
    # Verify student exists
    student = db.query(User).filter(
        User.id == student_id,
        User.role == RoleEnum.student
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == student_id).all()
    return enrollments
