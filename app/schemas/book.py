from typing import Optional, List
from pydantic import BaseModel

class BookOut(BaseModel):
    id: int
    book_id: str
    author_id: str
    title: str
    isbn: str
    genre: str
    publication_date: Optional[str] = None
    status: str
    mrp: float
    author_royalty_per_copy: float
    total_copies_sold: int
    total_royalty_earned: float
    royalty_paid: float
    royalty_pending: float
    last_royalty_payout_date: Optional[str] = None
    print_partner: Optional[str] = "In-House"
    available_on: Optional[List[str]] = []

    class Config:
        from_attributes = True
