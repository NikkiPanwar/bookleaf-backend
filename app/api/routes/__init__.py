from app.api.routes.auth import router as auth_router
from app.api.routes.books import router as books_router
from app.api.routes.tickets import router as tickets_router
from app.api.routes.admin_tickets import router as admin_tickets_router
from app.api.routes.dashboard import router as dashboard_router

__all__ = [
    "auth_router",
    "books_router",
    "tickets_router",
    "admin_tickets_router",
    "dashboard_router"
]
