from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base

class User(Base):
    """
    User Model
    Supports both 'author' and 'admin' roles.
    Authors are linked to their author_id from the BookLeaf sample data.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(String(50), unique=True, nullable=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="author", nullable=False)  # 'author' or 'admin'
    phone = Column(String(50), nullable=True)
    city = Column(String(100), nullable=True)
    joined_date = Column(DateTime, default=datetime.utcnow)

    # Relationships
    books = relationship("Book", back_populates="author", cascade="all, delete-orphan")
    tickets = relationship("Ticket", foreign_keys="Ticket.author_id", back_populates="author")
    assigned_tickets = relationship("Ticket", foreign_keys="Ticket.assigned_admin_id", back_populates="assigned_admin")
