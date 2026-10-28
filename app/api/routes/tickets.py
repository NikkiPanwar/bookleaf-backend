from typing import Optional
from fastapi import APIRouter, Depends, Form, UploadFile, File, status
from app.db.database import get_db
from app.schemas.ticket import TicketReplyCreate
from app.services.ticket_service import TicketService
from app.core.dependencies import get_current_user
from app.core.response import success_response

router = APIRouter(prefix="/tickets", tags=["Author Tickets"])


def _get_author_id(current_user) -> str:
    return (
        current_user.author_id
        if hasattr(current_user, "author_id")
        else current_user.get("author_id", "AUTH001")
    )


def _get_user_id(current_user) -> int:
    return current_user.id if hasattr(current_user, "id") else current_user.get("id", 1)


def _get_full_name(current_user) -> str:
    return (
        current_user.full_name
        if hasattr(current_user, "full_name")
        else current_user.get("full_name", "Author")
    )


@router.get("", status_code=status.HTTP_200_OK)
async def get_my_tickets(
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    """List the author's support tickets and their statuses."""
    service = TicketService(db)
    tickets = await service.get_author_tickets(_get_author_id(current_user))
    return success_response(data=tickets, message="Tickets fetched successfully")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_support_query(
    subject: str = Form(...),
    description: str = Form(...),
    category: str = Form("General Inquiry"),
    book_id: Optional[str] = Form(None),
    attachment: Optional[UploadFile] = File(None),
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Submit a support query with optional attachment.
    Automatically classifies category, assigns priority, and drafts an AI reply.
    """
    attachment_url = f"/uploads/{attachment.filename}" if attachment else None
    service = TicketService(db)
    ticket = await service.create_ticket(
        author_id=_get_author_id(current_user),
        subject=subject,
        description=description,
        category=category,
        book_id=book_id if book_id != "general" else None,
        attachment_url=attachment_url,
    )
    return success_response(data=ticket, message="Support ticket created successfully")


@router.get("/{ticket_id}", status_code=status.HTTP_200_OK)
async def get_ticket_detail(
    ticket_id: int,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    """View original query and conversation thread with admin responses."""
    service = TicketService(db)
    ticket = await service.get_ticket_detail(ticket_id)
    await service.assert_ticket_owner(ticket, _get_author_id(current_user))
    return success_response(data=ticket, message="Ticket fetched successfully")


@router.post("/{ticket_id}/reply", status_code=status.HTTP_201_CREATED)
async def add_reply(
    ticket_id: int,
    payload: TicketReplyCreate,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    """Author adds a follow-up message to the query thread."""
    service = TicketService(db)
    # Ensure ticket exists and belongs to this author
    ticket = await service.get_ticket_detail(ticket_id)
    await service.assert_ticket_owner(ticket, _get_author_id(current_user))

    reply = await service.add_reply(
        ticket_id=ticket_id,
        sender_id=_get_user_id(current_user),
        sender_role="author",
        message=payload.message,
    )
    return success_response(
        data={
            "id": reply.id,
            "ticket_id": reply.ticket_id,
            "sender_id": reply.sender_id,
            "sender_name": _get_full_name(current_user),
            "sender_role": reply.sender_role,
            "message": reply.message,
            "attachment_url": reply.attachment_url,
            "created_at": reply.created_at.isoformat() if reply.created_at else None,
        },
        message="Reply sent successfully",
    )
