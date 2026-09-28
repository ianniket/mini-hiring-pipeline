# Mini Hiring Pipeline

This is a small web app that helps a recruiter run a hiring pipeline and find candidates. It uses a modern glassmorphism design with a dark theme.

## Architecture

The application is split into two components:
- **Backend (FastAPI & SQLite)**: Manages data persistence using SQLAlchemy. Exposes RESTful endpoints for candidate creation, tracking stage transitions, and a natural language parsing search engine.
- **Frontend (React & Vite)**: A dynamic Single Page Application featuring an intuitive Kanban-style board, a custom glassmorphic UI, and real-time candidate search capabilities.

### Backend Search Engine
The backend implements a heuristical natural language parser that analyzes search queries like `"Who moved to Interview since Monday?"` or `"stuck in Screening for more than a week"`. It translates these intents into logical filters and executes them against the SQLite database, returning matches ranked by a fuzzy score.

## How to Run

### 1. Backend Setup
Make sure you have Python installed.
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
uvicorn app.main:app --reload
```
The backend will run on `http://127.0.0.1:8000`.

### 2. Frontend Setup
Make sure you have Node.js installed.
```bash
cd frontend
npm install
npm run dev
```
The frontend will run on `http://localhost:3000` (or another port provided by Vite).

## Decisions Made
- **SQLite Database**: Selected for simplicity and speed of development. It requires zero configuration while still providing a robust relational schema for the audit trail.
- **FastAPI**: Extremely fast to build REST APIs, with built-in validation via Pydantic.
- **Vanilla CSS (Glassmorphism)**: Used over Tailwind to manually craft a highly customized, premium UI without a large dependency footprint.
- **Custom NLP Heuristics**: Instead of relying on an external LLM (which introduces latency and potential failure points), the search query logic uses regex and fuzzy string matching. This provides immediate, deterministic responses for the core recruiter use cases.
- **Audit Trail Immutability**: Implemented by enforcing that `history` records are append-only. Stages can only move forward chronologically.

## What I'd Do With More Time
- Implement full authentication/authorization so different recruiters could have isolated workspaces.
- Add an LLM-based query parsing layer (e.g. OpenAI function calling) as a fallback when the regex heuristic fails to parse a complex query.
- Create pagination and virtualization for the Kanban board in case of thousands of candidates.
- Add drag-and-drop functionality for moving candidates between columns.
- Dockerize the application for easier one-click deployment.

## AI Disagreements
One place where I disagreed with standard AI advice was the styling approach. Typical AI boilerplate defaults to generic Tailwind setups or basic Material UI templates. I deliberately deviated from this and wrote custom Vanilla CSS to achieve a more bespoke "glassmorphism" aesthetic with vibrant gradients, fulfilling the requirement for a truly "WOW" and premium user experience. I also avoided relying on a heavy NLP library (like SpaCy) for the search, opting for a lightweight regex heuristic which is much faster for this specific scope.
