from pydantic import BaseModel, EmailStr, Field

# ---------- REQUEST SCHEMA ----------

class LoginRequest(BaseModel):
    """
    Payload for user login.
    """
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


# ---------- RESPONSE SCHEMAS ----------

class TokenResponse(BaseModel):
    """
    JWT token returned after successful authentication.
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Token expiration time in seconds")


class TokenPayload(BaseModel):
    """
    Internal schema used when decoding JWT tokens.
    """
    sub: int        # user_id
    role: str       # student | instructor | admin


class RefreshTokenRequest(BaseModel):
    """
    Payload for token refresh request.
    """
    refresh_token: str
