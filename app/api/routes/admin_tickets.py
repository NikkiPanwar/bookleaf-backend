from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from app.db.database import get_db
from app.schemas.ticket import (
    TicketReplyCreate, InternalNoteCreate, ClassificationUpdate, StatusUpdate,
)
from app.services.ticket_service import TicketService
from app.core.dependencies import require_admin
from app.core.response import success_response

router = APIRouter(prefix="/admin/tickets", tags=["Admin Ticket Resolution Desk"])


def _get_admin_id(current_admin) -> int:
    return current_admin.id if hasattr(current_admin, "id") else current_admin.get("id", 1)


def _get_admin_name(current_admin) -> str:
    return (
        current_admin.full_name
        if hasattr(current_admin, "full_name")
        else current_admin.get("full_name", "Support Staff")
    )


@router.get("", status_code=status.HTTP_200_OK)
async def get_ticket_queue(
    status_filter: Optional[str] = Query(None, alias="status"),
    category: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    date: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    current_admin=Depends(require_admin),
    db=Depends(get_db),
):
    """
    Ticket Queue: All authors' tickets with filters for status, category, priority, and date.
    Urgent and oldest unresolved tickets are sorted to the top.
    """
    service = TicketService(db)
    tickets = await service.get_admin_queue(
        status=status_filter,
        category=category,
        priority=priority,
        date_str=date,
        search=search,
    )
    return success_response(data=tickets, message="Ticket queue fetched successfully")


@router.get("/{ticket_id}", status_code=status.HTTP_200_OK)
async def get_admin_ticket_detail(
    ticket_id: int,
    current_admin=Depends(require_admin),
    db=Depends(get_db),
):
    """Detailed ticket review including original query, AI suggestions, and internal notes."""
    service = TicketService(db)
    ticket = await service.get_ticket_detail(ticket_id)
    return success_response(data=ticket, message="Ticket fetched successfully")


@router.post("/{ticket_id}/assign", status_code=status.HTTP_200_OK)
async def assign_to_self(
    ticket_id: int,
    current_admin=Depends(require_admin),
    db=Depends(get_db),
):
    """Assign ticket to the currently logged-in support desk staff member."""
    service = TicketService(db)
    ticket = await service.assign_to_admin(ticket_id, _get_admin_id(current_admin))
    return success_response(data=ticket, message="Ticket assigned successfully")


@router.patch("/{ticket_id}/classification", status_code=status.HTTP_200_OK)
async def update_classification(
    ticket_id: int,
    payload: ClassificationUpdate,
    current_admin=Depends(require_admin),
    db=Depends(get_db),
):
    """Update category and priority level on the ticket."""
    service = TicketService(db)
    ticket = await service.update_classification(ticket_id, payload.category, payload.priority)
    return success_response(data=ticket, message="Ticket classification updated")


@router.patch("/{ticket_id}/status", status_code=status.HTTP_200_OK)
async def update_status(
    ticket_id: int,
    payload: StatusUpdate,
    current_admin=Depends(require_admin),
    db=Depends(get_db),
):
    """Update ticket status (Open, In Progress, Resolved, Closed)."""
    service = TicketService(db)
    ticket = await service.update_status(ticket_id, payload.status)
    return success_response(data=ticket, message=f"Ticket status updated to '{payload.status}'")


@router.post("/{ticket_id}/reply", status_code=status.HTTP_201_CREATED)
async def send_admin_reply(
    ticket_id: int,
    payload: TicketReplyCreate,
    current_admin=Depends(require_admin),
    db=Depends(get_db),
):
    """Send response to the author and automatically mark ticket as In Progress."""
    service = TicketService(db)
    # Verify ticket exists before replying
    await service.get_ticket_detail(ticket_id)

    reply = await service.add_reply(
        ticket_id=ticket_id,
        sender_id=_get_admin_id(current_admin),
        sender_role="admin",
        message=payload.message,
    )
    return success_response(
        data={
            "id": reply.id,
            "ticket_id": reply.ticket_id,
            "sender_id": reply.sender_id,
            "sender_name": _get_admin_name(current_admin),
            "sender_role": reply.sender_role,
            "message": reply.message,
            "attachment_url": reply.attachment_url,
            "created_at": reply.created_at.isoformat() if reply.created_at else None,
        },
        message="Reply sent successfully",
    )


@router.post("/{ticket_id}/notes", status_code=status.HTTP_201_CREATED)
async def add_internal_note(
    ticket_id: int,
    payload: InternalNoteCreate,
    current_admin=Depends(require_admin),
    db=Depends(get_db),
):
    """Add internal staff note (private from author)."""
    service = TicketService(db)
    await service.get_ticket_detail(ticket_id)  # raises 404 if missing

    note = await service.add_internal_note(
        ticket_id=ticket_id,
        admin_id=_get_admin_id(current_admin),
        note_text=payload.note_text,
    )
    return success_response(
        data={
            "id": note.id,
            "ticket_id": note.ticket_id,
            "admin_id": note.admin_id,
            "admin_name": _get_admin_name(current_admin),
            "note_text": note.note_text,
            "created_at": note.created_at.isoformat() if note.created_at else None,
        },
        message="Internal note added successfully",
    )


@router.post("/{ticket_id}/ai-draft", status_code=status.HTTP_200_OK)
async def regenerate_ai_draft(
    ticket_id: int,
    current_admin=Depends(require_admin),
    db=Depends(get_db),
):
    """Request or regenerate AI reply draft, classification, and priority."""
    service = TicketService(db)
    result = await service.regenerate_ai_draft(ticket_id)
    return success_response(data=result, message="AI draft regenerated successfully")
