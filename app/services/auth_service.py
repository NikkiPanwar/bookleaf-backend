from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_password, get_password_hash
from app.core.exceptions import UnauthorizedException, ConflictException, NotFoundException, BadRequestException
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    """
    Business logic for authentication and user registration.
    Raises custom AppException subclasses — never raw HTTPException.
    Delegates all DB access to UserRepository.
    """

    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    async def authenticate_user(self, email: str, password: str) -> User:
        """
        Validate credentials.
        Raises UnauthorizedException if email not found or password wrong.
        """
        try:
            user = await self.repo.get_by_email(email)
        except Exception as exc:
            raise UnauthorizedException("Authentication service unavailable") from exc

        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password")
        return user

    async def register_user(
        self,
        full_name: str,
        email: str,
        password: str,
        role: str = "author",
    ) -> User:
        """
        Create a new user account.
        Raises ConflictException if the email is already taken.
        """
        try:
            existing = await self.repo.get_by_email(email)
        except Exception as exc:
            raise ConflictException("Could not verify email uniqueness") from exc

        if existing:
            raise ConflictException("A user with this email address already exists")

        hashed = get_password_hash(password)
        try:
            return await self.repo.create(
                full_name=full_name,
                email=email,
                hashed_password=hashed,
                role=role,
            )
        except Exception as exc:
            raise ConflictException("Could not create user account") from exc

    async def update_role(self, user_id: int, role: str) -> User:
        """
        Change the role of an existing user.
        Raises NotFoundException if no user matches user_id.
        Raises BadRequestException if role value is invalid.
        """
        if role not in ("admin", "author"):
            raise BadRequestException("Role must be either 'admin' or 'author'")

        try:
            user = await self.repo.get_by_id(user_id)
        except Exception as exc:
            raise NotFoundException(f"Could not look up user {user_id}") from exc

        if not user:
            raise NotFoundException(f"User with id {user_id} not found")

        try:
            return await self.repo.update_role(user, role)
        except Exception as exc:
            raise ConflictException("Could not update user role") from exc
