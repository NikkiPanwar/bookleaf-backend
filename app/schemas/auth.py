from typing import Optional
from pydantic import BaseModel

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    full_name: str
    email: str
    password: str
    # No role field — signup always creates an "author" account

class UserInfo(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    author_id: Optional[str] = None
    phone: Optional[str] = None
    city: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserInfo

class UpdateRoleRequest(BaseModel):
    user_id: int
    role: str  # "admin" or "author"
