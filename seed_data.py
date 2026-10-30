
import asyncio
import json
from pathlib import Path
from datetime import datetime

from sqlalchemy import select

from app.db.database import AsyncSessionLocal
from app.models.user import User
from app.models.book import Book
from app.models.ticket import Ticket, TicketReply, InternalNote

from app.core.security import get_password_hash


# Default password assigned to seeded author accounts
DEFAULT_PASSWORD = "Author@123"

# Default admin credentials
ADMIN_EMAIL = "admin@bookleaf.com"
ADMIN_PASSWORD = "Admin@123"

BASE_DIR = Path(__file__).resolve().parent
JSON_FILE = BASE_DIR / "data" / "bookleaf_sample_data.json"


def parse_date(value):
    """Convert a date string into datetime, if possible."""

    if not value:
        return datetime.utcnow()

    if isinstance(value, datetime):
        return value

    try:
        return datetime.fromisoformat(
            str(value).replace("Z", "+00:00")
        )
    except (ValueError, TypeError):
        return datetime.utcnow()


def get_value(data, *keys, default=None):
    """Return the first available key from a dictionary."""

    for key in keys:
        if key in data and data[key] is not None:
            return data[key]

    return default


def load_authors():
    """Load author data from JSON file."""

    if not JSON_FILE.exists():
        raise FileNotFoundError(
            f"JSON file not found: {JSON_FILE}"
        )

    with open(JSON_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if isinstance(data, list):
        authors = data

    elif isinstance(data, dict):
        authors = data.get("authors", [])

    else:
        raise ValueError(
            "Unexpected JSON format. Expected a list or an authors object."
        )

    if not authors:
        raise ValueError(
            "No authors found in the JSON file."
        )

    return authors


async def seed_data():

    if AsyncSessionLocal is None:
        raise RuntimeError(
            "AsyncSessionLocal is None. Check app/db/database.py and DATABASE_URL."
        )

    authors = load_authors()

    inserted_authors = 0
    skipped_authors = 0

    inserted_books = 0
    skipped_books = 0

    admin_created = False

    async with AsyncSessionLocal() as db:

        try:

            # ---------------------------------
            # 1. INSERT AUTHORS AND THEIR BOOKS
            # ---------------------------------

            for author_data in authors:

                author_id = get_value(
                    author_data, "author_id"
                )

                email = get_value(
                    author_data, "email"
                )

                if not author_id or not email:

                    print(
                        f"Skipping author: missing author_id/email: {author_data}"
                    )

                    skipped_authors += 1
                    continue

                # Check existing author by author_id or email
                result = await db.execute(
                    select(User).where(
                        (User.author_id == str(author_id))
                        |
                        (User.email == str(email))
                    )
                )

                author = result.scalar_one_or_none()

                if author is None:

                    author = User(
                        author_id=str(author_id),
                        email=str(email),

                        hashed_password=get_password_hash(
                            DEFAULT_PASSWORD
                        ),

                        full_name=str(
                            get_value(
                                author_data,
                                "name",
                                "full_name",
                                default="Author"
                            )
                        ),

                        role="author",

                        phone=str(
                            get_value(
                                author_data,
                                "phone",
                                default=""
                            ) or ""
                        ),

                        city=str(
                            get_value(
                                author_data,
                                "city",
                                default=""
                            ) or ""
                        ),

                        joined_date=parse_date(
                            get_value(
                                author_data,
                                "joined_date"
                            )
                        ),
                    )

                    db.add(author)

                    await db.flush()

                    inserted_authors += 1

                    print(
                        f"Added author: {author.full_name}"
                    )

                else:

                    skipped_authors += 1

                    print(
                        f"Author already exists: {email}"
                    )

                # ---------------------------------
                # 2. INSERT BOOKS FOR EACH AUTHOR
                # ---------------------------------

                author_books = get_value(
                    author_data,
                    "books",
                    default=[]
                ) or []

                for book_data in author_books:

                    book_id = get_value(
                        book_data,
                        "book_id",
                        "id"
                    )

                    if not book_id:

                        print(
                            f"Skipping book for {email}: missing book_id"
                        )

                        skipped_books += 1
                        continue

                    existing_book = await db.execute(
                        select(Book).where(
                            Book.book_id == str(book_id)
                        )
                    )

                    if existing_book.scalar_one_or_none():

                        skipped_books += 1

                        print(
                            f"Book already exists: {book_id}"
                        )

                        continue

                    book = Book(

                        book_id=str(book_id),

                        author_id=str(author_id),

                        title=str(
                            get_value(
                                book_data,
                                "title",
                                default="Untitled"
                            )
                        ),

                        isbn=str(
                            get_value(
                                book_data,
                                "isbn",
                                default=""
                            )
                        ),

                        genre=str(
                            get_value(
                                book_data,
                                "genre",
                                default="General"
                            )
                        ),

                        publication_date=get_value(
                            book_data,
                            "publication_date"
                        ),

                        status=get_value(
                            book_data,
                            "status",
                            default="Published & Live"
                        ),

                        mrp=float(
                            get_value(
                                book_data,
                                "mrp",
                                default=0
                            ) or 0
                        ),

                        author_royalty_per_copy=float(
                            get_value(
                                book_data,
                                "author_royalty_per_copy",
                                default=0
                            ) or 0
                        ),

                        total_copies_sold=int(
                            get_value(
                                book_data,
                                "total_copies_sold",
                                default=0
                            ) or 0
                        ),

                        total_royalty_earned=float(
                            get_value(
                                book_data,
                                "total_royalty_earned",
                                default=0
                            ) or 0
                        ),

                        royalty_paid=float(
                            get_value(
                                book_data,
                                "royalty_paid",
                                default=0
                            ) or 0
                        ),

                        royalty_pending=float(
                            get_value(
                                book_data,
                                "royalty_pending",
                                default=0
                            ) or 0
                        ),

                        last_royalty_payout_date=get_value(
                            book_data,
                            "last_royalty_payout_date"
                        ),

                        print_partner=get_value(
                            book_data,
                            "print_partner",
                            default="In-House"
                        ),

                        available_on=get_value(
                            book_data,
                            "available_on",
                            default=[]
                        ) or [],
                    )
                    db.add(book)
                    inserted_books += 1
                    print(
                        f"  Added book: {book.title}"
                    )
            # ---------------------------------
            # 3. CREATE DEFAULT ADMIN ACCOUNT
            # ---------------------------------

            result = await db.execute(
                select(User).where(
                    User.email == ADMIN_EMAIL
                )
            )
            admin = result.scalar_one_or_none()
            if admin is None:
                admin = User(
                    author_id=None,
                    email=ADMIN_EMAIL,
                    hashed_password=get_password_hash(
                        ADMIN_PASSWORD
                    ),
                    full_name="BookLeaf Admin",
                    role="admin",
                    phone=None,
                    city=None
                )
                db.add(admin)
                admin_created = True
                print("Admin account created successfully.")

            else:

                print("Admin account already exists.")

            # ---------------------------------
            # 4. COMMIT ALL CHANGES
            # ---------------------------------

            await db.commit()
            print("\n========== SEEDING COMPLETED ==========")
            print(
                f"Authors inserted : {inserted_authors}"
            )
            print(
                f"Authors skipped  : {skipped_authors}"
            )
            print(
                f"Books inserted   : {inserted_books}"
            )
            print(
                f"Books skipped    : {skipped_books}"
            )
            print(
                f"Admin created    : {'Yes' if admin_created else 'Already exists'}"
            )
            print("=======================================")
        except Exception:
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(seed_data())
