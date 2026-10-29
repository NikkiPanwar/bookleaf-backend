
import logging

from app.core.config import settings
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)

logger = logging.getLogger(__name__)

# Database initialization
engine = None
AsyncSessionLocal = None
HAS_ASYNC = False

try:
    db_url = make_url(settings.DATABASE_URL)

    # Support PostgreSQL URLs from Neon
    if db_url.drivername == "postgresql":
        db_url = db_url.set(drivername="postgresql+asyncpg")
    elif db_url.drivername != "postgresql+asyncpg":
        raise ValueError(
            f"Unsupported database driver: {db_url.drivername}"
        )

    # Remove query parameters not directly supported by asyncpg
    query = dict(db_url.query)
    sslmode = query.pop("sslmode", None)
    query.pop("channel_binding", None)

    db_url = db_url.set(query=query)

    # Configure SSL for Neon PostgreSQL
    connect_args = {}
    if sslmode in ("require", "verify-ca", "verify-full"):
        connect_args["ssl"] = "require"

    engine = create_async_engine(
        db_url,
        echo=False,
        pool_pre_ping=True,
        connect_args=connect_args,
    )

    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )

    HAS_ASYNC = True
    logger.info("Async PostgreSQL engine initialized.")

except Exception:
    logger.exception("Failed to initialize database engine")
    raise


async def get_db():
    """Provide an async database session to FastAPI routes."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
