# BookLeaf Author Support & Communication Portal

A full-stack application designed to help authors manage their books and support tickets while enabling administrators to manage and respond to author queries with AI-assisted support.

## Live Application

- **Frontend:** https://bookleaf-frontend-nine.vercel.app/login
- **Backend:** https://bookleaf-backend-sqs3.onrender.com
- **API Documentation:** https://bookleaf-backend-sqs3.onrender.com/docs

## Technology Stack

### Frontend
- Angular 17
- TypeScript
- HTML
- SCSS

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy 2.0
- Pydantic v2
- asyncpg

### Database
- PostgreSQL

### AI Integration
- Gemini-compatible AI API configuration
- Configurable model (`gemini-1.5-flash`)
- Ticket category classification
- Priority assignment
- AI-assisted reply drafting

## Project Features

### Author Portal
- Author authentication.
- Author dashboard.
- View assigned books and book information.
- Create and manage support tickets.
- View ticket details and replies.

### Admin Portal
- Admin authentication.
- Administrative dashboard.
- View and manage author support tickets.
- Review ticket information and respond to author queries.
- AI-assisted ticket classification, prioritization, and reply drafting.

## Architecture Overview

The application follows a frontend-backend architecture.

- **Angular frontend:** Handles user interfaces, navigation, authentication flows, and API integration.
- **FastAPI backend:** Provides REST APIs and handles application business logic.
- **PostgreSQL:** Stores application data and maintains relationships between users, books, tickets, and replies.
- **SQLAlchemy:** Handles database models and ORM operations.
- **JWT authentication:** Supports authenticated access and Author/Admin role-based authorization.
- **AI support assistant:** Assists with ticket classification, priority assignment, and suggested replies.

The backend separates routes, schemas, models, services, and database operations to keep responsibilities organized and maintainable.

## Repository Structure

```text
BookLeaf/
├── frontend/
│   └── bookleaf-frontend/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── utils/
│   ├── data/
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
└── README.md
```

## Local Setup

### Backend

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Configure the environment variables in `.env` using the backend's `.env.example`.

Seed the provided sample data:

```powershell
python -m app.utils.seed
```

Run the backend:

```powershell
uvicorn app.main:app --reload --port 8000
```

Backend: `http://localhost:8000`

Swagger: `http://localhost:8000/docs`

### Frontend

```powershell
cd frontend/bookleaf-frontend
npm install
npm start
ng serve
```

Frontend: `http://localhost:4200`

Configure the frontend API base URL to point to the backend running locally.

## Demo Credentials

The following credentials are provided for application evaluation.

**Author**
- Email: `diya.chatterjee@email.com`
- Password: `Author@123`

**Admin**
- Email: `admin@bookleaf.com`
- Password: `Admin@123`

## AI Integration

The application includes AI-assisted support capabilities for ticket category classification, priority assignment, and reply drafting.

The backend configuration supports a configurable AI model, with `gemini-1.5-flash` as the configured default. The AI API key is stored on the backend and must never be exposed in the Angular frontend or committed to the repository.

AI prompts are intended to use relevant ticket context and task-specific instructions to generate classifications and suggested replies. AI-generated replies are suggestions for support workflows.

AI usage, provider availability, and request costs depend on the configured provider and model. Production improvements can include request limits, token-usage monitoring, response validation, and a documented fallback workflow.

## Security

- JWT-based authentication.
- Author and Admin role-based access.
- Password hashing in the backend.
- Sensitive configuration stored in environment variables.
- AI API credentials kept on the backend.
- CORS configured for the frontend origin.

Never commit `.env` files, database passwords, JWT secrets, or AI API keys.

## Known Limitations & Future Improvements

Potential improvements for a production environment include:

- More comprehensive automated tests.
- Centralized logging and monitoring.
- AI request rate limiting and token-usage tracking.
- More robust AI error handling and fallback behavior.
- Improved API performance and database query optimization.
- Additional production security and deployment monitoring.

## API Documentation

The deployed API documentation is available at:

https://bookleaf-backend-sqs3.onrender.com/docs

## Project Repositories

- **Frontend:** https://github.com/NikkiPanwar/bookleaf-frontend
- **Backend:** https://github.com/NikkiPanwar/bookleaf-backend

Both repositories are private. Repository access can be provided to the BookLeaf team once their GitHub collaborator email is shared.

---

**Project:** BookLeaf Author Support & Communication Portal  
**Frontend:** Angular  
**Backend:** FastAPI  
**Database:** PostgreSQL