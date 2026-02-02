from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.schemas.user import UserRead, UserUpdate
from app.models.user import User
from app.core.dependencies import get_current_user, require_instructor
from app.common.enums import RoleEnum

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserRead)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get current user's profile.
    """
    return current_user


@router.put("/me", response_model=UserRead)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile.
    """
    if user_update.first_name is not None:
        current_user.first_name = user_update.first_name  # type: ignore
    if user_update.last_name is not None:
        current_user.last_name = user_update.last_name  # type: ignore
    if user_update.is_active is not None:
        current_user.is_active = user_update.is_active  # type: ignore
    
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/", response_model=List[UserRead])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    role: RoleEnum | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all users (accessible to authenticated users).
    Can filter by role.
    """
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    users = query.offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserRead)
async def get_user_by_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific user by ID.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.get("/instructors/", response_model=List[UserRead])
async def list_instructors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all instructors.
    """
    instructors = db.query(User).filter(User.role == RoleEnum.instructor).offset(skip).limit(limit).all()
    return instructors


@router.get("/students/", response_model=List[UserRead])
async def list_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all students.
    """
    students = db.query(User).filter(User.role == RoleEnum.student).offset(skip).limit(limit).all()
    return students
