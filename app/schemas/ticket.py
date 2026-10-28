from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class TicketCreateRequest(BaseModel):
    subject: str
    description: str
    category: Optional[str] = "General Inquiry"
    book_id: Optional[str] = None
    attachment_url: Optional[str] = None

class TicketReplyCreate(BaseModel):
    message: str

class TicketReplyOut(BaseModel):
    id: int
    ticket_id: int
    sender_id: int
    sender_name: Optional[str] = "Staff"
    sender_role: str
    message: str
    attachment_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class InternalNoteCreate(BaseModel):
    note_text: str

class InternalNoteOut(BaseModel):
    id: int
    ticket_id: int
    admin_id: int
    admin_name: Optional[str] = "Admin"
    note_text: str
    created_at: datetime

    class Config:
        from_attributes = True

class ClassificationUpdate(BaseModel):
    category: str
    priority: str

class StatusUpdate(BaseModel):
    status: str

class TicketOut(BaseModel):
    id: int
    ticket_number: str
    author_id: str
    author_name: Optional[str] = None
    book_id: Optional[str] = None
    book_title: Optional[str] = None
    subject: str
    description: str
    attachment_url: Optional[str] = None
    category: str
    priority: str
    status: str
    ai_classification: Optional[str] = None
    ai_priority: Optional[str] = None
    ai_reply_draft: Optional[str] = None
    assigned_admin_id: Optional[int] = None
    assigned_admin_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    replies: Optional[List[TicketReplyOut]] = []
    internal_notes: Optional[List[InternalNoteOut]] = []

    class Config:
        from_attributes = True
