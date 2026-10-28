import json
import os
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundException, ServiceException
from app.models.book import Book
from app.repositories.book_repository import BookRepository
from app.schemas.book import BookOut


class BookService:
    """
    Business logic for books and royalty data.
    Raises custom AppException subclasses — never raw HTTPException.
    Delegates all DB access to BookRepository.
    Falls back to JSON sample data when the DB has no rows yet.
    """

    def __init__(self, db: AsyncSession):
        self.repo = BookRepository(db)

    async def get_books_for_author(self, author_id: str) -> List[Book]:
        """
        Return the author's books from DB; fall back to JSON sample data
        if the DB table is empty or unavailable.
        """
        try:
            books = await self.repo.get_by_author_id(author_id)
            if books:
                return books
        except Exception:
            # DB unavailable — try JSON fallback silently
            pass

        return self._load_from_json(author_id)

    async def get_book_by_id(self, book_id: str) -> Book:
        """
        Return a single book by its domain ID.
        Raises NotFoundException if no book matches.
        """
        try:
            book = await self.repo.get_by_book_id(book_id)
        except Exception as exc:
            raise ServiceException("Could not retrieve book details") from exc

        if not book:
            raise NotFoundException(f"Book '{book_id}' not found")
        return book

    async def get_author_aggregates(self, author_id: str):
        """Return aggregated royalty metrics for all of an author's books."""
        try:
            return await self.repo.get_author_aggregates(author_id)
        except Exception as exc:
            raise ServiceException("Could not compute author metrics") from exc

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load_from_json(author_id: str) -> List[BookOut]:
        """Load sample book data from the bundled JSON file."""
        json_path = os.path.join(
            os.path.dirname(__file__), "..", "data", "bookleaf_sample_data.json"
        )
        if not os.path.exists(json_path):
            return []

        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return []

        for author in data.get("authors", []):
            if author.get("author_id") == author_id or author_id is None:
                return [
                    BookOut(
                        id=idx + 1,
                        book_id=b["book_id"],
                        author_id=author["author_id"],
                        title=b["title"],
                        isbn=b["isbn"],
                        genre=b["genre"],
                        publication_date=b.get("publication_date"),
                        status=b.get("status", "Published & Live"),
                        mrp=float(b.get("mrp", 0)),
                        author_royalty_per_copy=float(b.get("author_royalty_per_copy", 0)),
                        total_copies_sold=int(b.get("total_copies_sold", 0)),
                        total_royalty_earned=float(b.get("total_royalty_earned", 0)),
                        royalty_paid=float(b.get("royalty_paid", 0)),
                        royalty_pending=float(b.get("royalty_pending", 0)),
                        last_royalty_payout_date=b.get("last_royalty_payout_date"),
                        print_partner=b.get("print_partner", "In-House"),
                        available_on=b.get("available_on", []),
                    )
                    for idx, b in enumerate(author.get("books", []))
                ]
        return []
