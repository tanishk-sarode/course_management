from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials
from app.core.security import decode_token
from app.common.enums import RoleEnum
from app.database.session import get_db
from app.models.user import User
from sqlalchemy.orm import Session

# Security scheme for extracting JWT from Authorization header
security = HTTPBearer()


# ---------- CURRENT USER DEPENDENCY ----------

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to extract and validate the current user from JWT token.
    
    Args:
        credentials: HTTP Bearer token from request header
        db: Database session
        
    Returns:
        User object if token is valid
        
    Raises:
        HTTPException: If token is invalid, expired, or user not found
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Decode the token
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract user_id from token (comes as string from JWT, convert to int)
    user_id_str = payload.get("sub")
    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        user_id = int(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


# ---------- ROLE-BASED ACCESS CONTROL ----------

async def require_student(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require student role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User if they have student role
        
    Raises:
        HTTPException: If user does not have student role
    """
    if current_user.role != RoleEnum.student.value:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires student role",
        )
    return current_user


async def require_instructor(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require instructor role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User if they have instructor role
        
    Raises:
        HTTPException: If user does not have instructor role
    """
    if current_user.role != RoleEnum.instructor.value:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires instructor role",
        )
    return current_user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require admin role.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User if they have admin role
        
    Raises:
        HTTPException: If user does not have admin role
    """
    # Admin role is reserved for future use
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin role is not yet enabled",
    )


async def require_instructor_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to require instructor role (admin role is reserved for future use).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User if they have instructor role
        
    Raises:
        HTTPException: If user doesn't have instructor role
    """
    if current_user.role != RoleEnum.instructor.value:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This endpoint requires instructor role",
        )
    return current_user


