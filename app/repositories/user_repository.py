from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User


class UserRepository:
    """
    Data access layer for the User model.
    All raw DB queries involving User go here — no business logic.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by email address."""
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Fetch a user by primary key."""
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        full_name: str,
        email: str,
        hashed_password: str,
        role: str = "author",
    ) -> User:
        """Insert a new user row and return the persisted instance."""
        user = User(
            full_name=full_name,
            email=email,
            hashed_password=hashed_password,
            role=role,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_role(self, user: User, role: str) -> User:
        """Persist a role change on an existing user."""
        user.role = role
        await self.db.commit()
        await self.db.refresh(user)
        return user

