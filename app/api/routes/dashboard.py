from fastapi import APIRouter, Depends, status
from app.db.database import get_db
from app.services.dashboard_service import DashboardService
from app.core.dependencies import get_current_user
from app.core.response import success_response

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _get_author_id(current_user) -> str:
    return (
        current_user.author_id
        if hasattr(current_user, "author_id")
        else current_user.get("author_id", "AUTH001")
    )


def _get_author_name(current_user) -> str:
    return (
        current_user.full_name
        if hasattr(current_user, "full_name")
        else current_user.get("full_name", "Author")
    )


@router.get("/author", status_code=status.HTTP_200_OK)
async def get_author_dashboard(
    current_user=Depends(get_current_user),
    db=Depends(get_db),
):
    """
    Author Dashboard Metrics:
    total_books, total_copies_sold, total_royalty_earned,
    royalty_paid, royalty_pending, active_tickets_count.
    """
    service = DashboardService(db)
    metrics = await service.get_author_metrics(
        author_id=_get_author_id(current_user),
        author_name=_get_author_name(current_user),
    )
    return success_response(data=metrics, message="Dashboard metrics fetched successfully")
