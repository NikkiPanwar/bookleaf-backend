from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.book import Book


class BookRepository:
    """
    Data access layer for the Book model.
    All raw DB queries involving Book go here — no business logic.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_author_id(self, author_id: str) -> List[Book]:
        """Return all books belonging to the given author."""
        stmt = select(Book).where(Book.author_id == author_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_book_id(self, book_id: str) -> Optional[Book]:
        """Return a single book by its domain book_id (e.g. 'BK001')."""
        stmt = select(Book).where(Book.book_id == book_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_author_aggregates(self, author_id: str):
        """
        Return aggregated royalty metrics for all books of an author.
        Returns a tuple: (book_count, total_copies_sold, total_royalty_earned,
                          royalty_paid, royalty_pending)
        """
        stmt = select(
            func.count(Book.id),
            func.sum(Book.total_copies_sold),
            func.sum(Book.total_royalty_earned),
            func.sum(Book.royalty_paid),
            func.sum(Book.royalty_pending),
        ).where(Book.author_id == author_id)
        result = await self.db.execute(stmt)
        return result.first()

