# 🗺️ Milestones & Task Breakdown

## Milestone 1 — Auth + CRUD Items

**Goal:** A registered user can log in and manage lost/found posts.

### Tasks

- [ ] **Project scaffolding**
  - Initialize FastAPI app with `app/main.py`
  - Set up `pyproject.toml`, `requirements.txt`, `.env.example`
  - Configure `pydantic-settings` for config management
  - Docker Compose for Postgres + Redis

- [ ] **Database setup**
  - SQLAlchemy async engine + session factory (`database.py`)
  - Alembic init + first migration for `users` and `items` tables

- [ ] **User model & auth**
  - `User` ORM model
  - `POST /auth/register` — hash password with bcrypt, store user
  - `POST /auth/login` — verify password, return signed JWT
  - `GET /auth/me` — protected route returning current user
  - `get_current_user` dependency using JWT Bearer

- [ ] **Item CRUD**
  - `Item` ORM model
  - `POST /items` — create item (authenticated)
  - `GET /items` — paginated list of recent open items
  - `GET /items/{id}` — single item detail with photos
  - `PATCH /items/{id}` — update item (owner only)
  - `DELETE /items/{id}` — soft-delete or hard-delete (owner or admin)

- [ ] **Tests**
  - Auth registration, login, token validation
  - Item create / read / update / delete (owner checks)

---

## Milestone 2 — Search (Keyword + Geo)

**Goal:** Users can find relevant items by keyword, category, and proximity.

### Tasks

- [ ] **Full-text search**
  - Add `tsvector` column or use `to_tsvector` in query
  - `GET /items/search?query=wallet` — searches title + description

- [ ] **Category filter**
  - `GET /items/search?category=pets`

- [ ] **Geospatial filter**
  - Accept `lat`, `lng`, `radius` (km) query params
  - Implement Haversine distance filter in SQL or PostGIS
  - `GET /items/search?lat=40.7&lng=-74.0&radius=5`

- [ ] **Combined filters**
  - Allow chaining query + category + geo in a single request
  - Add pagination (`skip`, `limit`)

- [ ] **Tests**
  - Keyword match / no match
  - Category filter
  - Geo radius (items inside vs outside radius)

---

## Milestone 3 — Photo Uploads

**Goal:** Posters can attach photos to their items.

### Tasks

- [ ] **Storage abstraction**
  - `utils/storage.py` with `save_file()` and `get_url()` interface
  - Local filesystem implementation (save to `./uploads/`)
  - S3 implementation using `boto3` (switched via env var)

- [ ] **Photo model & migration**
  - `Photo` ORM model
  - Alembic migration for `photos` table

- [ ] **Upload endpoint**
  - `POST /items/{id}/photos` — accept `multipart/form-data`
  - Validate MIME type (jpg, png, webp only)
  - Limit size (e.g. max 5 MB per file, max 5 files per item)
  - Save file, store record, return photo URLs

- [ ] **Integrate with item responses**
  - Include `photos` array in `GET /items/{id}` response

- [ ] **Tests**
  - Upload valid image
  - Reject invalid MIME type
  - Reject oversized file
  - Photos appear in item detail response

---

## Milestone 4 — Claim Flow + Messaging

**Goal:** A user can claim an item and exchange messages with the poster.

### Tasks

- [ ] **Claim model & migration**
  - `Claim` ORM model
  - Alembic migration for `claims` table

- [ ] **Claim endpoints**
  - `POST /items/{id}/claims` — submit claim with proof message (authenticated, not own item)
  - `GET /items/{id}/claims` — list claims (item owner only)
  - `PATCH /claims/{id}` — approve or reject (item owner only)
  - On approval: set item status → `claimed`, reject all other claims

- [ ] **Message model & migration**
  - `Message` ORM model
  - Alembic migration for `messages` table

- [ ] **Messaging endpoints**
  - `POST /items/{id}/messages` — send message to the other party
  - `GET /items/{id}/messages` — fetch thread (participants only)
  - Enforce only poster ↔ claimant can message per item

- [ ] **Tests**
  - Claim submission (valid, duplicate, own item guard)
  - Claim approval / rejection
  - Status transition on approval
  - Message send and receive
  - Unauthorised access guard

---

## Milestone 5 — Status Changes + Auto-Archive

**Goal:** Items move through their lifecycle correctly and expire automatically.

### Tasks

- [ ] **Status transition logic**
  - Service method `transition_item_status(item, new_status)` with allowed transitions:
    - `open → claimed` (on claim approval)
    - `claimed → resolved` (owner marks resolved)
    - `open/claimed → archived` (expiry or manual)
    - `any → removed` (admin only)
  - Guard against invalid transitions

- [ ] **Poster resolves item**
  - `PATCH /items/{id}` with `{"status": "resolved"}` — owner only after claim approved

- [ ] **Auto-archive job**
  - Background task (APScheduler or FastAPI lifespan) runs daily
  - Finds items with `status = 'open'` and `created_at < now() - 30 days`
  - Sets `status = 'archived'`, `is_archived = true`

- [ ] **Report & moderation endpoints**
  - `POST /items/{id}/reports` — any user can report
  - `GET /admin/reports` — admin lists all pending reports
  - `PATCH /admin/reports/{id}` — admin actions report (dismiss / remove item)

- [ ] **Tests**
  - Valid and invalid status transitions
  - Auto-archive job (mock `now()` to simulate 31-day-old item)
  - Report submission
  - Admin report action (with and without admin role)

---

## Post-MVP Backlog

- [ ] Map view — return GeoJSON-compatible item list
- [ ] Anonymous relay email
- [ ] Duplicate detection — cosine similarity on title embeddings
- [ ] Email/webhook notification on nearby match
- [ ] Verified organisation accounts
- [ ] Rate limiting with Redis
- [ ] WebSocket real-time messaging
