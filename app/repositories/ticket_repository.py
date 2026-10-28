import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from app.models.ticket import Ticket, TicketReply, InternalNote


class TicketRepository:
    """
    Data access layer for Ticket, TicketReply, and InternalNote models.
    All raw DB queries involving tickets go here — no business logic.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------
    # Tickets
    # ------------------------------------------------------------------

    async def create_ticket(
        self,
        *,
        author_id: str,
        subject: str,
        description: str,
        ticket_number: str,
        category: str,
        priority: str,
        status: str = "Open",
        book_id: Optional[str] = None,
        attachment_url: Optional[str] = None,
        ai_classification: Optional[str] = None,
        ai_priority: Optional[str] = None,
        ai_reply_draft: Optional[str] = None,
    ) -> Ticket:
        """Insert a new ticket row and return the persisted instance."""
        ticket = Ticket(
            ticket_number=ticket_number,
            author_id=author_id,
            book_id=book_id,
            subject=subject,
            description=description,
            attachment_url=attachment_url,
            category=category,
            priority=priority,
            status=status,
            ai_classification=ai_classification,
            ai_priority=ai_priority,
            ai_reply_draft=ai_reply_draft,
        )
        self.db.add(ticket)
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def get_by_id(self, ticket_id: int) -> Optional[Ticket]:
        """Fetch a ticket with all eagerly loaded relationships."""
        stmt = (
            select(Ticket)
            .where(Ticket.id == ticket_id)
            .options(
                selectinload(Ticket.author),
                selectinload(Ticket.book),
                selectinload(Ticket.assigned_admin),
                selectinload(Ticket.replies),
                selectinload(Ticket.internal_notes),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_author(self, author_id: str) -> List[Ticket]:
        """Return all tickets for a given author, newest first."""
        stmt = (
            select(Ticket)
            .where(Ticket.author_id == author_id)
            .options(selectinload(Ticket.book), selectinload(Ticket.replies))
            .order_by(Ticket.created_at.desc())
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_admin_queue(
        self,
        *,
        status: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        search: Optional[str] = None,
    ) -> List[Ticket]:
        """
        Return all tickets for admin queue with optional filters.
        Ordered: Urgent first, then oldest unresolved first.
        """
        stmt = select(Ticket).options(
            selectinload(Ticket.author),
            selectinload(Ticket.book),
            selectinload(Ticket.assigned_admin),
        )

        conditions = []
        if status:
            conditions.append(Ticket.status == status)
        if category:
            conditions.append(Ticket.category == category)
        if priority:
            conditions.append(Ticket.priority == priority)
        if search:
            pattern = f"%{search}%"
            conditions.append(
                or_(
                    Ticket.subject.ilike(pattern),
                    Ticket.description.ilike(pattern),
                    Ticket.author_id.ilike(pattern),
                )
            )

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.order_by(
            Ticket.priority == "Urgent",
            Ticket.created_at.asc(),
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def count_active_by_author(self, author_id: str) -> int:
        """Count Open/In Progress tickets for a given author."""
        stmt = select(func.count(Ticket.id)).where(
            Ticket.author_id == author_id,
            Ticket.status.in_(["Open", "In Progress"]),
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() or 0

    async def assign_admin(self, ticket: Ticket, admin_id: int) -> Ticket:
        """Assign a ticket to an admin."""
        ticket.assigned_admin_id = admin_id
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def update_classification(
        self, ticket: Ticket, category: str, priority: str
    ) -> Ticket:
        """Update category and priority on a ticket."""
        ticket.category = category
        ticket.priority = priority
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def update_status(self, ticket: Ticket, status: str) -> Ticket:
        """Update the status on a ticket."""
        ticket.status = status
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    async def update_ai_fields(
        self,
        ticket: Ticket,
        ai_classification: str,
        ai_priority: str,
        ai_reply_draft: str,
    ) -> Ticket:
        """Persist AI-generated classification, priority, and reply draft."""
        ticket.ai_classification = ai_classification
        ticket.ai_priority = ai_priority
        ticket.ai_reply_draft = ai_reply_draft
        await self.db.commit()
        await self.db.refresh(ticket)
        return ticket

    # ------------------------------------------------------------------
    # Ticket Replies
    # ------------------------------------------------------------------

    async def add_reply(
        self,
        *,
        ticket_id: int,
        sender_id: int,
        sender_role: str,
        message: str,
        attachment_url: Optional[str] = None,
    ) -> TicketReply:
        """Insert a new reply and auto-advance ticket status if needed."""
        ticket = await self.get_by_id(ticket_id)
        reply = TicketReply(
            ticket_id=ticket_id,
            sender_id=sender_id,
            sender_role=sender_role,
            message=message,
            attachment_url=attachment_url,
        )
        self.db.add(reply)

        # Side-effect: first admin reply moves ticket from Open → In Progress
        if sender_role == "admin" and ticket and ticket.status == "Open":
            ticket.status = "In Progress"

        await self.db.commit()
        await self.db.refresh(reply)
        return reply

    # ------------------------------------------------------------------
    # Internal Notes
    # ------------------------------------------------------------------

    async def add_internal_note(
        self,
        *,
        ticket_id: int,
        admin_id: int,
        note_text: str,
    ) -> InternalNote:
        """Insert a new internal note (staff-only)."""
        note = InternalNote(
            ticket_id=ticket_id,
            admin_id=admin_id,
            note_text=note_text,
        )
        self.db.add(note)
        await self.db.commit()
        await self.db.refresh(note)
        return note

