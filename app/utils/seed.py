import os
import json
import asyncio
from datetime import datetime
from sqlalchemy import select
from app.db.database import AsyncSessionLocal, engine
from app.db.base import Base
from app.models.user import User
from app.models.book import Book
from app.core.security import get_password_hash

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
SAMPLE_DATA_PATH = BASE_DIR / "data" / "bookleaf_sample_data.json"

async def seed_data():
    """
    Imports the provided bookleaf_sample_data.json into PostgreSQL
    while preserving original author_id, book_id, and relationships.
    Also creates a default support desk Admin account.
    """
    if not os.path.exists(SAMPLE_DATA_PATH):
        print(f"Error: Sample data file not found at: {SAMPLE_DATA_PATH}")
        print("Please place 'bookleaf_sample_data.json' inside the 'backend/data/' directory.")
        return

    print(f"Loading sample data from: {SAMPLE_DATA_PATH}")
    with open(SAMPLE_DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    authors_data = data.get("authors", [])
    print(f"Found {len(authors_data)} authors in sample data.")

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # 1. Create or ensure Admin account
        admin_stmt = select(User).where(User.email == "admin@bookleaf.com")
        admin_res = await session.execute(admin_stmt)
        admin_user = admin_res.scalar_one_or_none()

        if not admin_user:
            admin_user = User(
                email="admin@bookleaf.com",
                full_name="BookLeaf Support Admin",
                hashed_password=get_password_hash("Admin@123"),
                role="admin"
            )
            session.add(admin_user)
            print("✓ Created default Admin account: admin@bookleaf.com (Pass: Admin@123)")

        # 2. Import Authors and Books preserving original IDs
        for author_dict in authors_data:
            author_id = author_dict["author_id"]
            email = author_dict["email"]

            stmt = select(User).where(User.author_id == author_id)
            res = await session.execute(stmt)
            existing_author = res.scalar_one_or_none()

            joined_dt = datetime.utcnow()
            if author_dict.get("joined_date"):
                try:
                    joined_dt = datetime.strptime(author_dict["joined_date"], "%Y-%m-%d")
                except ValueError:
                    pass

            if not existing_author:
                author_user = User(
                    author_id=author_id,
                    email=email,
                    full_name=author_dict.get("name", ""),
                    phone=author_dict.get("phone"),
                    city=author_dict.get("city"),
                    joined_date=joined_dt,
                    hashed_password=get_password_hash("Author@123"),
                    role="author"
                )
                session.add(author_user)
                await session.flush()
                print(f"✓ Imported Author: {author_dict.get('name')} ({author_id})")
            else:
                author_user = existing_author

            # Books
            for b_dict in author_dict.get("books", []):
                book_id = b_dict["book_id"]
                b_stmt = select(Book).where(Book.book_id == book_id)
                b_res = await session.execute(b_stmt)
                existing_book = b_res.scalar_one_or_none()

                if not existing_book:
                    new_book = Book(
                        book_id=book_id,
                        author_id=author_id,
                        title=b_dict.get("title", ""),
                        isbn=b_dict.get("isbn", ""),
                        genre=b_dict.get("genre", ""),
                        publication_date=b_dict.get("publication_date"),
                        status=b_dict.get("status", "Published & Live"),
                       mrp=(float(b_dict["mrp"])
                       if b_dict.get("mrp") is not None
                       else None
                       ),
                       author_royalty_per_copy=(float(b_dict["author_royalty_per_copy"])if b_dict.get("author_royalty_per_copy") is not None
                        else None
                        ),
                        print_partner=b_dict.get("print_partner"),
                        total_copies_sold=int(b_dict.get("total_copies_sold", 0)),
                        total_royalty_earned=float(b_dict.get("total_royalty_earned", 0)),
                        royalty_paid=float(b_dict.get("royalty_paid", 0)),
                        royalty_pending=float(b_dict.get("royalty_pending", 0)),
                        last_royalty_payout_date=b_dict.get("last_royalty_payout_date"),
                        available_on=b_dict.get("available_on", [])
                    )
                    session.add(new_book)
                    print(f"   ↳ Added Book: {new_book.title} ({book_id})")

        await session.commit()
        print("\n🎉 Sample data seed successfully completed!")

if __name__ == "__main__":
    asyncio.run(seed_data())
