# Bus Ticketing (Assignment-AI Intern)

This repository implements a simple bus ticket booking system with a FastAPI backend, a Streamlit frontend demo, and a Retrieval-Augmented-Generation (RAG) helper for bus provider & policy lookup. It is intended for an assignment demo — you can run the backend locally (or in Docker), load the example routes dataset, and try bookings from the Streamlit UI.

Key components
- Backend: FastAPI + SQLAlchemy (app code in `app/`).
- Database: Postgres.
- Frontend: Streamlit (files under `Frontend/` — `streamlit_page.py`).
- RAG: retrieval pipeline / notebook under `retrieval/rag_engine` that uses embeddings + a vector store.

Prerequisites
- Python 3.10+ (3.11 recommended)
- Git
- A virtualenv tool (venv/virtualenv) for isolating Python dependencies

Quick start (recommended — Docker for DB, venv for Python)

1. Clone the repository

```cmd
git clone https://github.com/sajid73/bus-ticket-booking-rag.git
cd bus-ticket-booking-rag
```

2. Create and activate a virtual environment (Windows cmd.exe)

```cmd
python -m venv .venv
.\.venv\Scripts\activate
```

3. Install Python dependencies

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

4. Start the backend (development mode)

```cmd
# activate your venv if not already active
.\.venv\Scripts\activate
uvicorn app.main:app --reload
```

The backend will create tables (SQLAlchemy `create_all` is used in startup) and ingest example route data on first run.

5. Open the Streamlit frontend (Another terminal, as it depends on backend)

```cmd
streamlit run Frontend/streamlit_app.py
```

The Streamlit UI runs in your browser (default `http://localhost:8501`). Use the search form to find routes and try booking a seat. The Streamlit demo calls the backend API at `http://127.0.0.1:8000/api/` by default.

API endpoints (examples)
- GET /api/routes?origin=Dhaka&destination=Sylhet — search routes
- POST /api/book_ticket — create a booking; JSON body: `{ "route_id": 1, "user_name": "Sajid", "user_phone": "0123456789", "seat_number": "D3" }`
- GET /api/bookings/{phone} — list bookings for a phone number
- DELETE /api/cancel_booking/{booking_id} — cancel a booking

Development notes
- The backend code is in `app/` (models, CRUD, rag_engine, main.py).
- The Streamlit demo is in `Frontend/`.
- The `retrieval/` folder contains a Jupyter notebook for experimenting with ingestion, RAG and stores vector database.