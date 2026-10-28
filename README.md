# BookLeaf Backend

FastAPI & SQLAlchemy backend service for the **BookLeaf Author Support & Communication Portal**.

## Overview

- **FastAPI**: Asynchronous REST API framework
- **SQLAlchemy 2.0 & asyncpg**: Database ORM and PostgreSQL driver
- **Pydantic v2**: Request validation and response schemas
- **Role-based Authentication**: JWT authentication supporting Author and Admin roles
- **AI Support Assistant**: Intelligent category classification, priority assignment, and reply drafting

## Folder Structure

```text
backend/
├── app/
│   ├── main.py              # FastAPI application entrypoint and middleware
│   ├── core/
│   │   ├── config.py        # Environment settings (DB, JWT, AI keys)
│   │   ├── security.py      # Password hashing and JWT generation
│   │   └── dependencies.py  # DB session and role-based auth dependencies
│   ├── db/
│   │   ├── database.py      # Async database connection and sessionmaker
│   │   └── base.py          # SQLAlchemy DeclarativeBase
│   ├── models/              # Database models (User, Book, Ticket, Reply, Note)
│   ├── schemas/             # Pydantic validation schemas
│   ├── api/
│   │   └── routes/          # REST API route controllers
│   ├── services/            # Business logic (auth, ticket workflows, AI assistant)
│   └── utils/
│       └── seed.py          # Imports bookleaf_sample_data.json into DB
├── data/
│   └── bookleaf_sample_data.json  # Author & book records
├── tests/                   # Automated API tests
├── .env.example             # Template for environment variables
├── requirements.txt         # Python dependencies
└── README.md
```

## Setup & Running

### 1. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Ensure your PostgreSQL `DATABASE_URL` and `AI_API_KEY` are configured.

### 4. Seed Sample Data

Import author and book records preserving IDs and relationships:
```powershell
python -m app.utils.seed
```

### 5. Run the Server

```powershell
uvicorn app.main:app --reload --port 8000
```
Interactive API documentation: `http://localhost:8000/docs`
