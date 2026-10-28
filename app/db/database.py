from app.core.config import settings

engine = None
AsyncSessionLocal = None
HAS_ASYNC = False

try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    # Async PostgreSQL engine with asyncpg
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True
    )
    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )
    HAS_ASYNC = True
except Exception:
    # Graceful fallback for local development before PostgreSQL/greenlet is installed
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    try:
        engine = create_engine("sqlite:///./bookleaf_dev.db", echo=False, future=True)
    except Exception:
        engine = create_engine("sqlite:///:memory:", echo=False, future=True)
    AsyncSessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
    HAS_ASYNC = False

async def get_db():
    """
    Dependency for database session in FastAPI routes.
    Guarantees session cleanup across async or sync sessions.
    """
    if HAS_ASYNC and AsyncSessionLocal:
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
    elif AsyncSessionLocal:
        session = AsyncSessionLocal()
        try:
            yield session
        finally:
            session.close()
    else:
        yield None
