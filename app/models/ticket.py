from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base

class Ticket(Base):
    """
    Support Ticket Model
    Captures author queries, AI classification & priority, editable drafts,
    and resolution status.
    """
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String(50), unique=True, index=True, nullable=False)
    author_id = Column(String(50), ForeignKey("users.author_id"), nullable=False, index=True)
    book_id = Column(String(50), ForeignKey("books.book_id"), nullable=True, index=True)
    
    subject = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    attachment_url = Column(String(500), nullable=True)
    
    # Classification & Priority
    category = Column(String(100), default="General Inquiry")
    priority = Column(String(50), default="Medium")  # 'Urgent', 'High', 'Medium', 'Low'
    status = Column(String(50), default="Open")     # 'Open', 'In Progress', 'Resolved', 'Closed'
    
    # AI Assistance Fields
    ai_classification = Column(String(100), nullable=True)
    ai_priority = Column(String(50), nullable=True)
    ai_reply_draft = Column(Text, nullable=True)
    
    # Assignment
    assigned_admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    author = relationship("User", foreign_keys=[author_id], back_populates="tickets")
    assigned_admin = relationship("User", foreign_keys=[assigned_admin_id], back_populates="assigned_tickets")
    book = relationship("Book", back_populates="tickets")
    replies = relationship("TicketReply", back_populates="ticket", cascade="all, delete-orphan", order_by="TicketReply.created_at")
    internal_notes = relationship("InternalNote", back_populates="ticket", cascade="all, delete-orphan", order_by="InternalNote.created_at")


class TicketReply(Base):
    """
    Ticket Reply Model
    Messages communicated between author and support desk admin.
    """
    __tablename__ = "ticket_replies"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    sender_role = Column(String(50), nullable=False)  # 'author' or 'admin'
    message = Column(Text, nullable=False)
    attachment_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="replies")
    sender = relationship("User")


class InternalNote(Base):
    """
    Internal Note Model
    Staff-only notes attached to a ticket. Never visible to authors.
    """
    __tablename__ = "internal_notes"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id"), nullable=False, index=True)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    note_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", back_populates="internal_notes")
    admin = relationship("User")
