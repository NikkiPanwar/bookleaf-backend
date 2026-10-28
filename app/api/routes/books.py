from typing import List
from fastapi import APIRouter, Depends, status
from app.db.database import get_db
from app.services.book_service import BookService
from app.core.dependencies import get_current_user
from app.core.response import success_response
from fastapi import HTTPException

router = APIRouter(prefix="/books", tags=["Books & Royalties"])


def _get_author_id(current_user) -> str:
    return (
        current_user.author_id
        if hasattr(current_user, "author_id")
        else current_user.get("author_id", "AUTH001")
    )


@router.get("")
async def get_my_books(
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    if current_user.role != "author" or not current_user.author_id:
        raise HTTPException(
            status_code=403,
            detail="Author account or author ID required",
        )

    service = BookService(db)
    books = await service.get_books_for_author(
        current_user.author_id
    )

    return success_response(
        data=books,
        message="Books fetched successfully",
    )

@router.get("/{book_id}", status_code=status.HTTP_200_OK)
async def get_book_by_id(
    book_id: str,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    """Get detailed metrics for a specific book."""
    service = BookService(db)
    book = await service.get_book_by_id(book_id)
    return success_response(data=book, message="Book fetched successfully")
