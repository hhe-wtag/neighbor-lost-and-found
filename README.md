# 🏘️ Neighborhood Lost-and-Found

A community platform where people post lost or found items with photos and a location. Others can search nearby, message the poster, and submit a claim. Admins moderate reports.

**Stack:** Vue.js (frontend) · FastAPI (backend) · PostgreSQL · Session Cookie Auth · S3-compatible storage

---

## 📁 Repository Structure

```
neighborhood-lost-and-found/
├── frontend/                  # Vue.js SPA
├── backend/                   # FastAPI application
├── context-docs/              # Architecture docs, diagrams, DB design, milestones
│   ├── OVERVIEW.md            # LLM-optimised project summary (start here)
│   ├── ARCHITECTURE.md        # System design, tech decisions, folder structures
│   ├── DB_DESIGN.md           # Full database schema (paste into dbdiagram.io)
│   ├── API_ROUTES.md          # All endpoints with method, path, auth, body, response
│   ├── DIAGRAMS.md            # User flow + DFD (Mermaid, renders in any .md viewer)
│   └── MILESTONES.md          # Feature breakdown into tasks per milestone
└── README.md                  # This file
```

---

## 🚀 Quick Start

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # fill in DB_URL, SECRET_KEY, etc.
docker-compose up -d          # start Postgres (+ optional Redis)
alembic upgrade head
uvicorn app.main:app --reload
# API docs → http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
cp .env.example .env          # set VITE_API_BASE_URL=http://localhost:8000
npm run dev
# App → http://localhost:5173
```

---

## 🧭 Documentation

All design and architecture documents live in [`context-docs/`](./context-docs/).

| Document                                            | What it covers                                                                          |
| --------------------------------------------------- | --------------------------------------------------------------------------------------- |
| [`OVERVIEW.md`](./context-docs/OVERVIEW.md)         | Concise project summary — best starting point for LLMs and new contributors             |
| [`ARCHITECTURE.md`](./context-docs/ARCHITECTURE.md) | System layers, tech stack decisions, backend + frontend folder structure                |
| [`DB_DESIGN.md`](./context-docs/DB_DESIGN.md)       | Database schema in DBML — paste into [dbdiagram.io](https://dbdiagram.io) to render ERD |
| [`API_ROUTES.md`](./context-docs/API_ROUTES.md)     | Every API route with method, auth requirement, request body and response shape          |
| [`DIAGRAMS.md`](./context-docs/DIAGRAMS.md)         | User flow diagram, DFD Level 0 + Level 1, and status state machines (Mermaid)           |
| [`MILESTONES.md`](./context-docs/MILESTONES.md)     | MVP scope divided into 5 milestones with granular checkbox tasks                        |

---

## ⚡ Feature Summary

**MVP**

- User registration, login (Session Cookie), profile with contact preferences
- Post Lost / Found items with title, description, category, date, and location
- Photo uploads (local filesystem in dev, S3-compatible in prod)
- Keyword + category + geospatial search (radius from a lat/lng point)
- Claim flow: submit → approve / reject → resolved
- In-app messaging between poster and claimant
- Report suspicious posts; admin moderation queue

**Post-MVP**

- Map view with clustered pins
- Post auto-expiry (30 days)
- Anonymous relay email
- Duplicate detection
- Email / webhook notifications on nearby matches
- Verified organisation accounts

---

## 🛠️ Tech Stack

|          | Technology                                             |
| -------- | ------------------------------------------------------ |
| Frontend | Vue 3 + Vite + Vue Router + Pinia                      |
| Backend  | FastAPI + SQLAlchemy 2 + Alembic                       |
| Database | PostgreSQL 15+                                         |
| Auth     | Session Cookie with JWT (python-jose + passlib bcrypt) |
| Storage  | Local FS (dev) / S3-compatible (prod)                  |
