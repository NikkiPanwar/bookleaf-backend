import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import NotFoundException, ForbiddenException, ServiceException
from app.models.ticket import Ticket, TicketReply, InternalNote
from app.repositories.ticket_repository import TicketRepository
from app.repositories.book_repository import BookRepository
from app.services.ai_service import AIService


class TicketService:
    """
    Business logic for support tickets, replies, and internal notes.
    Raises custom AppException subclasses — never raw HTTPException.
    Delegates all DB access to TicketRepository.
    """

    def __init__(self, db: AsyncSession):
        self.repo = TicketRepository(db)
        self.book_repo = BookRepository(db)

    async def create_ticket(
        self,
        *,
        author_id: str,
        subject: str,
        description: str,
        category: str = "General Inquiry",
        book_id: Optional[str] = None,
        attachment_url: Optional[str] = None,
    ) -> Ticket:
        """
        Create a support ticket:
        1. Resolve book title for AI context (if book_id given).
        2. Run AI classification and draft generation.
        3. Persist via repository.
        Raises ServiceException on DB failure.
        """
        # Optional: resolve book title for richer AI context
        book_title: Optional[str] = None
        if book_id:
            try:
                book = await self.book_repo.get_by_book_id(book_id)
                if book:
                    book_title = book.title
            except Exception:
                pass  # non-critical; proceed without title

        # AI analysis (non-blocking on failure)
        try:
            ai_res = await AIService.analyze_and_draft(subject, description, book_title)
        except Exception:
            ai_res = {"classification": category, "priority": "Medium", "reply_draft": None}

        ticket_number = f"BL-{uuid.uuid4().hex[:6].upper()}"

        try:
            return await self.repo.create_ticket(
                author_id=author_id,
                subject=subject,
                description=description,
                ticket_number=ticket_number,
                category=category or ai_res["classification"],
                priority=ai_res["priority"],
                book_id=book_id,
                attachment_url=attachment_url,
                ai_classification=ai_res["classification"],
                ai_priority=ai_res["priority"],
                ai_reply_draft=ai_res["reply_draft"],
            )
        except Exception as exc:
            raise ServiceException("Could not create support ticket") from exc

    async def get_author_tickets(self, author_id: str) -> List[Ticket]:
        """Return all tickets for an author, newest first."""
        try:
            return await self.repo.get_by_author(author_id)
        except Exception as exc:
            raise ServiceException("Could not retrieve tickets") from exc

    async def get_ticket_detail(self, ticket_id: int) -> Ticket:
        """
        Return a single ticket with all relationships loaded.
        Raises NotFoundException if the ticket does not exist.
        """
        try:
            ticket = await self.repo.get_by_id(ticket_id)
        except Exception as exc:
            raise ServiceException("Could not retrieve ticket") from exc

        if not ticket:
            raise NotFoundException(f"Ticket #{ticket_id} not found")
        return ticket

    async def assert_ticket_owner(self, ticket: Ticket, author_id: str) -> None:
        """Raise ForbiddenException if the ticket doesn't belong to author_id."""
        if ticket.author_id != author_id:
            raise ForbiddenException("You can only access your own tickets")

    async def get_admin_queue(
        self,
        *,
        status: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        date_str: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Ticket]:
        """
        Return filtered/sorted ticket queue for admins.
        Date filtering is applied here as business logic.
        """
        try:
            tickets = await self.repo.get_admin_queue(
                status=status,
                category=category,
                priority=priority,
                search=search,
            )
        except Exception as exc:
            raise ServiceException("Could not retrieve ticket queue") from exc

        if date_str:
            tickets = [
                t for t in tickets
                if t.created_at and t.created_at.strftime("%Y-%m-%d") == date_str
            ]
        return tickets

    async def assign_to_admin(self, ticket_id: int, admin_id: int) -> Ticket:
        """Assign ticket to the given admin user."""
        ticket = await self.get_ticket_detail(ticket_id)
        try:
            return await self.repo.assign_admin(ticket, admin_id)
        except Exception as exc:
            raise ServiceException("Could not assign ticket") from exc

    async def update_classification(
        self, ticket_id: int, category: str, priority: str
    ) -> Ticket:
        """Update ticket category and priority."""
        ticket = await self.get_ticket_detail(ticket_id)
        try:
            return await self.repo.update_classification(ticket, category, priority)
        except Exception as exc:
            raise ServiceException("Could not update ticket classification") from exc

    async def update_status(self, ticket_id: int, status: str) -> Ticket:
        """Update ticket status."""
        ticket = await self.get_ticket_detail(ticket_id)
        try:
            return await self.repo.update_status(ticket, status)
        except Exception as exc:
            raise ServiceException("Could not update ticket status") from exc

    async def add_reply(
        self,
        *,
        ticket_id: int,
        sender_id: int,
        sender_role: str,
        message: str,
        attachment_url: Optional[str] = None,
    ) -> TicketReply:
        """Add a reply from either an author or admin."""
        try:
            return await self.repo.add_reply(
                ticket_id=ticket_id,
                sender_id=sender_id,
                sender_role=sender_role,
                message=message,
                attachment_url=attachment_url,
            )
        except Exception as exc:
            raise ServiceException("Could not save reply") from exc

    async def add_internal_note(
        self,
        *,
        ticket_id: int,
        admin_id: int,
        note_text: str,
    ) -> InternalNote:
        """Add a staff-only internal note to a ticket."""
        try:
            return await self.repo.add_internal_note(
                ticket_id=ticket_id,
                admin_id=admin_id,
                note_text=note_text,
            )
        except Exception as exc:
            raise ServiceException("Could not save internal note") from exc

    async def regenerate_ai_draft(self, ticket_id: int) -> dict:
        """Re-run AI analysis and persist updated fields. Returns raw AI result."""
        ticket = await self.get_ticket_detail(ticket_id)
        book_title = ticket.book.title if ticket.book else None

        try:
            ai_res = await AIService.analyze_and_draft(
                ticket.subject, ticket.description, book_title
            )
        except Exception as exc:
            raise ServiceException("AI service unavailable") from exc

        try:
            await self.repo.update_ai_fields(
                ticket,
                ai_classification=ai_res["classification"],
                ai_priority=ai_res["priority"],
                ai_reply_draft=ai_res["reply_draft"],
            )
        except Exception as exc:
            raise ServiceException("Could not persist AI draft") from exc

        return ai_res
