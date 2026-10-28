from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.base import Base

class Book(Base):
    """
    Book Model
    Stores publication information and royalty performance metrics.
    Preserves original IDs and structure from bookleaf_sample_data.json.
    """
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(String(50), unique=True, nullable=False, index=True)
    author_id = Column(String(50), ForeignKey("users.author_id"), nullable=False, index=True)
    
    title = Column(String(255), nullable=False)
    isbn = Column(String(100), nullable=False)
    genre = Column(String(100), nullable=False)
    publication_date = Column(String(50), nullable=True)
    status = Column(String(100), default="Published & Live")
    mrp = Column(Float, default=0.0)
    author_royalty_per_copy = Column(Float, default=0.0)
    total_copies_sold = Column(Integer, default=0)
    total_royalty_earned = Column(Float, default=0.0)
    royalty_paid = Column(Float, default=0.0)
    royalty_pending = Column(Float, default=0.0)
    last_royalty_payout_date = Column(String(50), nullable=True)
    print_partner = Column(String(100), default="In-House")
    available_on = Column(JSON, default=list)

    # Relationships
    author = relationship("User", back_populates="books")
    tickets = relationship("Ticket", back_populates="book")
