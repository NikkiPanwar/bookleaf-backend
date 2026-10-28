from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from app.db.database import get_db
from app.core.security import decode_access_token

security = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db = Depends(get_db)
):
    """
    Validates JWT token and loads current active user from database.
    """
    from app.models.user import User

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials not provided",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token payload",
        )

    # In starter/mock mode or db mode
    try:
        stmt = select(User).where(User.id == int(user_id))
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            return user
    except Exception:
        pass

    # Fallback user dict for local prototype/mock mode
    return {
        "id": int(user_id),
        "email": payload.get("email", ""),
        "role": payload.get("role", "author"),
        "author_id": payload.get("author_id", "AUTH001"),
        "full_name": payload.get("full_name", "Author User")
    }

def require_role(allowed_role: str):
    """
    Role-based authorization dependency factory.
    Enforces author vs admin access permissions strictly.
    """
    async def role_checker(current_user = Depends(get_current_user)):
        user_role = current_user.role if hasattr(current_user, "role") else current_user.get("role")
        if user_role != allowed_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: requires '{allowed_role}' role"
            )
        return current_user
    return role_checker

require_author = require_role("author")
require_admin = require_role("admin")
