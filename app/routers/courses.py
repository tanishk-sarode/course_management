from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database.session import get_db
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse
from app.models.course import Course
from app.models.user import User
from app.core.dependencies import get_current_user, require_instructor
from app.common.enums import CourseCategory, RoleEnum

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(require_instructor),
    db: Session = Depends(get_db)
):
    """
    Create a new course. Only instructors can create courses.
    """
    new_course = Course(
        title=course_data.title,
        description=course_data.description,
        category=course_data.category,
        level=course_data.level,
        instructor_id=current_user.id,
        is_published=False
    )
    
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    
    return new_course


@router.get("/", response_model=List[CourseResponse])
async def list_courses(
    skip: int = 0,
    limit: int = 100,
    category: Optional[CourseCategory] = None,
    instructor_id: Optional[int] = None,
    is_published: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    List all courses with optional filters.
    - Filter by category
    - Filter by instructor_id
    - Filter by published status
    """
    query = db.query(Course)
    
    # Apply filters
    if category:
        query = query.filter(Course.category == category)
    
    if instructor_id:
        query = query.filter(Course.instructor_id == instructor_id)
    
    if is_published is not None:
        query = query.filter(Course.is_published == is_published)
    
    courses = query.offset(skip).limit(limit).all()
    return courses


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: int, db: Session = Depends(get_db)):
    """
    Get a specific course by ID.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    return course


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_update: CourseUpdate,
    current_user: User = Depends(require_instructor),
    db: Session = Depends(get_db)
):
    """
    Update a course. Only the course instructor can update it.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if current user is the course instructor
    if course.instructor_id != current_user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own courses"
        )
    
    # Update fields
    if course_update.title is not None:
        course.title = course_update.title  # type: ignore
    if course_update.description is not None:
        course.description = course_update.description  # type: ignore
    if course_update.category is not None:
        course.category = course_update.category  # type: ignore
    if course_update.level is not None:
        course.level = course_update.level  # type: ignore
    if course_update.is_published is not None:
        course.is_published = course_update.is_published  # type: ignore
    
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    current_user: User = Depends(require_instructor),
    db: Session = Depends(get_db)
):
    """
    Delete a course. Only the course instructor can delete it.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if current user is the course instructor
    if course.instructor_id != current_user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own courses"
        )
    
    db.delete(course)
    db.commit()
    return None


@router.get("/instructor/{instructor_id}", response_model=List[CourseResponse])
async def get_courses_by_instructor(
    instructor_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all courses by a specific instructor.
    """
    # Verify instructor exists
    instructor = db.query(User).filter(
        User.id == instructor_id,
        User.role == RoleEnum.instructor
    ).first()
    
    if not instructor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instructor not found"
        )
    
    courses = db.query(Course).filter(
        Course.instructor_id == instructor_id
    ).offset(skip).limit(limit).all()
    
    return courses


@router.get("/category/{category}", response_model=List[CourseResponse])
async def get_courses_by_category(
    category: CourseCategory,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all courses in a specific category.
    """
    courses = db.query(Course).filter(
        Course.category == category
    ).offset(skip).limit(limit).all()
    
    return courses
