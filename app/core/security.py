from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt 
from passlib.context import CryptContext
from app.core.config import Settings
from app.schemas.auth import TokenPayload

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

settings = Settings()


# ---------- PASSWORD HASHING ----------

def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    
    Args:
        password: Plaintext password to hash
        
    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against its hash.
    
    Args:
        plain_password: Plaintext password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


# ---------- JWT TOKEN MANAGEMENT ----------

def create_access_token(user_id: int, role: str, expires_delta: Optional[timedelta] = None) -> tuple[str, int]:
    """
    Create a JWT access token.
    
    Args:
        user_id: User ID to encode in token
        role: User role (student, instructor, admin)
        expires_delta: Optional custom expiration time
        
    Returns:
        Tuple of (token_string, expires_in_seconds)
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "sub": user_id,
        "role": role,
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    expires_in = int(expires_delta.total_seconds())
    
    return encoded_jwt, expires_in


def create_refresh_token(user_id: int) -> str:
    """
    Create a JWT refresh token with longer expiration.
    
    Args:
        user_id: User ID to encode in token
        
    Returns:
        Refresh token string
    """
    expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "sub": user_id,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc)
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[TokenPayload]:
    """
    Decode and validate a JWT token.
    
    Args:
        token: JWT token string to decode
        
    Returns:
        Token payload if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        return TokenPayload(**payload)
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None


def create_tokens(user_id: int, role: str) -> dict:
    """
    Create both access and refresh tokens for a user.
    
    Args:
        user_id: User ID
        role: User role
        
    Returns:
        Dictionary with access_token, refresh_token, token_type, and expires_in
    """
    access_token, expires_in = create_access_token(user_id, role)
    refresh_token = create_refresh_token(user_id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": expires_in
    }
