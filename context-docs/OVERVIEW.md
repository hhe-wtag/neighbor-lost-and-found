# Project Overview — Neighborhood Lost-and-Found

## Purpose

A web platform for community lost-and-found management. Users post items they have lost or found, attach photos and a location, and the community helps reunite items with their owners through search, messaging, and a structured claim flow.

## Tech Stack

- **Frontend:** Vue 3 (Vite, Vue Router, Pinia) — lives in `/frontend`
- **Backend:** FastAPI (Python 3.11+) — lives in `/backend`
- **Database:** PostgreSQL 15+, accessed via SQLAlchemy 2 async ORM
- **Auth:** Session Cookie Tokens + JWT (python-jose, passlib/bcrypt)
- **Migrations:** Alembic
- **Storage:** Local filesystem in dev; S3-compatible bucket in prod (abstracted via `utils/storage.py`)
- **Caching / Rate limiting:** Redis (optional)

## Domain Entities

| Entity    | Key Fields                                                                       | Notes                                   |
| --------- | -------------------------------------------------------------------------------- | --------------------------------------- |
| `User`    | id, name, email, hashed_password, role, contact_pref                             | role: `user` or `admin`                 |
| `Item`    | id, user_id, type, title, description, category, date_occurred, lat, lng, status | type: `lost` or `found`                 |
| `Photo`   | id, item_id, url, storage_type                                                   | one item → many photos                  |
| `Claim`   | id, item_id, user_id, message, status                                            | status: `pending → approved / rejected` |
| `Message` | id, item_id, from_user_id, to_user_id, body, is_read                             | scoped to one item thread               |
| `Report`  | id, item_id, reporter_id, reason, status                                         | admin moderation queue                  |

## Item Lifecycle

```
open → claimed → resolved
open → archived   (auto after 30 days)
any  → removed    (admin action)
```

## Core API Surfaces

- `POST /auth/register` · `POST /auth/login` · `GET /auth/me`
- `POST /items` · `GET /items` · `GET /items/{id}` · `PATCH /items/{id}` · `DELETE /items/{id}`
- `GET /items/search?query=&category=&lat=&lng=&radius=`
- `POST /items/{id}/photos`
- `POST /items/{id}/claims` · `GET /items/{id}/claims` · `PATCH /claims/{id}`
- `POST /items/{id}/messages` · `GET /items/{id}/messages`
- `POST /items/{id}/reports` · `GET /admin/reports` · `PATCH /admin/reports/{id}`

## Business Rules

1. A user cannot claim their own item.
2. Only one claim per item can be approved; all others are auto-rejected on approval.
3. Only the item owner can approve or reject claims.
4. Only participants (poster + approved claimant) can exchange messages on an item.
5. Only admins can access `GET /admin/reports` and `PATCH /admin/reports/{id}`.
6. Items with status `open` and no activity for 30 days are auto-archived by a background scheduler.
7. Photos are validated for MIME type (jpg/png/webp) and size (max 5 MB each, max 5 per item).

## Frontend Structure (Vue 3)

```
frontend/src/
├── views/          # Page-level components (Home, ItemDetail, Post, Search, Profile)
├── components/     # Reusable UI components
├── stores/         # Pinia stores (auth, items, claims, messages)
├── router/         # Vue Router config
├── api/            # Axios-based API client modules
└── utils/          # Helpers (geo, formatting)
```

## Backend Structure (FastAPI)

```
backend/app/
├── main.py         # App factory, router registration, lifespan
├── config.py       # pydantic-settings env config
├── database.py     # Async SQLAlchemy engine + session
├── dependencies.py # get_current_user, get_db, require_admin
├── models/         # SQLAlchemy ORM models
├── schemas/        # Pydantic v2 request/response schemas
├── routers/        # FastAPI route handlers (thin layer)
├── services/       # Business logic (called by routers)
└── utils/          # security.py, storage.py, geo.py
```

## Related Documents

- `ARCHITECTURE.md` — detailed tech decisions and rationale
- `DB_DESIGN.dbml` — full schema (paste into https://dbdiagram.io)
- `API_ROUTES.md` — complete endpoint reference
- `DIAGRAMS.md` — user flow and data flow diagrams (Mermaid)
- `MILESTONES.md` — task breakdown per milestone
