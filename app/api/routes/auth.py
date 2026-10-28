from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from app.db.database import get_db
from app.schemas.auth import LoginRequest, SignupRequest, UpdateRoleRequest
from app.services.auth_service import AuthService
from app.core.exceptions import BadRequestException
from app.core.security import create_access_token
from app.core.dependencies import get_current_user, require_admin
from app.core.response import success_response

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _user_info(user) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "author_id": getattr(user, "author_id", None),
        "phone": getattr(user, "phone", None),
        "city": getattr(user, "city", None),
    }


def _build_token(user) -> str:
    return create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "author_id": user.author_id,
        "full_name": user.full_name,
    })


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(credentials: LoginRequest, db=Depends(get_db)):
    """
    Authenticate author or admin user and return JWT bearer token.
    Raises 401 if credentials are invalid.
    """
    service = AuthService(db)
    user = await service.authenticate_user(credentials.email, credentials.password)
    return success_response(
        data={"access_token": _build_token(user), "token_type": "bearer", "user": _user_info(user)},
        message="Login successful",
    )


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user_data: SignupRequest, db=Depends(get_db)):
    """
    Register a new author account.
    Role is always set to 'author' — cannot self-assign admin.
    Returns JWT access token immediately after successful registration.
    """
    service = AuthService(db)
    user = await service.register_user(
        full_name=user_data.full_name,
        email=user_data.email,
        password=user_data.password,
        role="author",
    )
    return success_response(
        data={"access_token": _build_token(user), "token_type": "bearer", "user": _user_info(user)},
        message="Account created successfully",
    )


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_me(current_user=Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    if hasattr(current_user, "id"):
        return success_response(data=_user_info(current_user), message="User profile fetched")
    return success_response(data=current_user, message="User profile fetched")


@router.put("/update-role", status_code=status.HTTP_200_OK)
async def update_user_role(
    payload: UpdateRoleRequest,
    db=Depends(get_db),
    _admin=Depends(require_admin),
):
    """
    Update a user's role (admin only).
    Allows promoting an author to admin or demoting an admin to author.
    """
    service = AuthService(db)
    user = await service.update_role(payload.user_id, payload.role)
    return success_response(data=_user_info(user), message=f"User role updated to '{payload.role}'")
