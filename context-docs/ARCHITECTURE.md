# Architecture — Neighborhood Lost-and-Found

## System Layers

```
┌─────────────────────────────────────────┐
│        Vue 3 SPA  (frontend/)           │
│  Vue Router · Pinia · Axios             │
└──────────────┬──────────────────────────┘
               │ HTTP/JSON  (JWT Bearer)
┌──────────────▼──────────────────────────┐
│        FastAPI  (backend/)              │
│  Routers → Services → Models            │
│  Pydantic v2 schemas · Dependencies     │
└───────┬──────────────────┬──────────────┘
        │                  │
┌───────▼──────┐   ┌───────▼──────────────┐
│  PostgreSQL  │   │  File Storage        │
│  SQLAlchemy  │   │  Local FS  /  S3     │
│  Alembic     │   └──────────────────────┘
└──────────────┘
        │
┌───────▼──────┐
│  Redis       │  (optional — rate limit, cache)
└──────────────┘
```

---

## Tech Decisions

| Concern            | Choice                       | Rationale                                                  |
| ------------------ | ---------------------------- | ---------------------------------------------------------- |
| Frontend framework | Vue 3 + Vite                 | Composition API, fast HMR, lightweight                     |
| State management   | Pinia                        | Official Vue store, simpler than Vuex                      |
| API client         | Axios                        | Interceptors for JWT injection and 401 handling            |
| Backend framework  | FastAPI                      | Async-native, automatic OpenAPI docs, Pydantic integration |
| ORM                | SQLAlchemy 2 async           | Mature, Alembic support, async sessions                    |
| Database           | PostgreSQL 15+               | Full-text search, geospatial via PostGIS, JSONB            |
| Auth               | Cookie Session Token + JWT   | Stateful, HTTP-Only, secure server-side session token      |
| Password hashing   | passlib + bcrypt             | Industry-standard, future-proof                            |
| Schema validation  | Pydantic v2                  | Strict typing, serialisation, FastAPI native               |
| Migrations         | Alembic                      | Battle-tested for SQLAlchemy projects                      |
| File storage       | Abstracted (local / S3)      | Swap backend via `STORAGE_BACKEND` env var                 |
| Search             | Postgres FTS + Haversine geo | No external service needed for MVP                         |
| Caching            | Redis (optional)             | Rate limiting on auth routes; search result cache          |
| Testing (BE)       | pytest + httpx AsyncClient   | Async-compatible, no test server process needed            |
| Testing (FE)       | Vitest + Vue Test Utils      | Co-located with Vite config, fast                          |
| Containerisation   | Docker + Docker Compose      | Consistent dev environment for Postgres + Redis            |

---

## Backend Folder Structure

```
backend/
├── app/
│   ├── main.py                 # App factory, router registration, lifespan events
│   ├── config.py                # pydantic-settings: reads .env, exposes Settings singleton
│   ├── database.py             # Async engine, SessionLocal, Base declarative
│   ├── dependencies.py         # get_db(), get_user_repo(), get_message_service(), require_admin()
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User ORM model
│   │   ├── item.py             # Item ORM model
│   │   ├── photo.py            # Photo ORM model
│   │   ├── claim.py            # Claim ORM model
│   │   ├── message.py          # Message ORM model
│   │   └── report.py           # Report ORM model
│   │
│   ├── schemas/
│   │   ├── auth.py             # RegisterRequest, LoginRequest, TokenResponse
│   │   ├── user.py             # UserOut, UserUpdate
│   │   ├── item.py             # ItemCreate, ItemUpdate, ItemOut, ItemListOut
│   │   ├── photo.py            # PhotoOut
│   │   ├── claim.py            # ClaimCreate, ClaimUpdate, ClaimOut
│   │   ├── message.py          # MessageCreate, MessageOut
│   │   └── report.py           # ReportCreate, ReportUpdate, ReportOut
│   │
│   ├── routers/
│   │   ├── auth.py             # /auth/*
│   │   ├── items.py            # /items/*
│   │   ├── photos.py           # /items/{id}/photos
│   │   ├── claims.py           # /items/{id}/claims, /claims/{id}
│   │   ├── messages.py         # /items/{id}/messages
│   │   └── reports.py          # /items/{id}/reports, /admin/reports
│   │
│   ├── services/
│   │   ├── auth_service.py     # register, login, token creation
│   │   ├── item_service.py     # CRUD, status transitions, archive job
│   │   ├── photo_service.py    # validate, store, persist record
│   │   ├── claim_service.py    # submit, approve/reject, cascade status
│   │   ├── message_service.py  # send, fetch thread, participant guard
│   │   └── report_service.py   # create report, admin list, action
│   │
│   └── utils/
│       ├── security.py         # hash_password(), verify_password(), create_jwt()
│       ├── storage.py          # StorageBackend ABC → LocalStorage, S3Storage
│       └── geo.py              # haversine(), build_geo_filter()
│
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── tests/
│   ├── conftest.py             # async engine, test DB, fixtures
│   ├── test_auth.py
│   ├── test_items.py
│   ├── test_photos.py
│   ├── test_claims.py
│   ├── test_messages.py
│   └── test_reports.py
│
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── pyproject.toml
```

---

## Frontend Folder Structure

```
frontend/
├── src/
│   ├── main.js                 # App mount, plugin registration
│   ├── App.vue                 # Root component, router-view
│   │
│   ├── router/
│   │   └── index.js            # Route definitions, navigation guards (auth)
│   │
│   ├── stores/
│   │   ├── auth.js             # Pinia: user state, login, logout, token
│   │   ├── items.js            # Pinia: item list, active item, search results
│   │   ├── claims.js           # Pinia: claims for active item
│   │   └── messages.js         # Pinia: message threads
│   │
│   ├── api/
│   │   ├── client.js           # Axios instance, base URL, JWT interceptor
│   │   ├── auth.js             # register(), login(), getMe()
│   │   ├── items.js            # createItem(), listItems(), searchItems(), etc.
│   │   ├── photos.js           # uploadPhotos()
│   │   ├── claims.js           # submitClaim(), listClaims(), actionClaim()
│   │   ├── messages.js         # sendMessage(), getThread()
│   │   └── reports.js          # reportItem(), adminListReports(), actionReport()
│   │
│   ├── views/
│   │   ├── Home.vue            # Feed of recent items + search bar
│   │   ├── ItemDetail.vue      # Full item view: photos, claim button, messages
│   │   ├── PostItem.vue        # Create/edit item form
│   │   ├── Search.vue          # Search results with filters
│   │   ├── Profile.vue         # User profile, their posts, their claims
│   │   ├── Login.vue
│   │   ├── Register.vue
│   │   └── Admin.vue           # Reports queue (admin only)
│   │
│   ├── components/
│   │   ├── ItemCard.vue        # Summary card used in lists and search
│   │   ├── PhotoUpload.vue     # Drag-and-drop photo uploader
│   │   ├── ClaimForm.vue       # Submit claim modal
│   │   ├── ClaimList.vue       # Poster's view of incoming claims
│   │   ├── MessageThread.vue   # Chat-style message list
│   │   ├── LocationPicker.vue  # Map or lat/lng input widget
│   │   ├── StatusBadge.vue     # Colour-coded item status pill
│   │   └── NavBar.vue
│   │
│   └── utils/
│       ├── geo.js              # formatDistance(), coordsFromBrowser()
│       └── format.js           # formatDate(), truncate()
│
├── public/
├── index.html
├── vite.config.js
├── .env.example
└── package.json
```

---

## Environment Variables

### Backend (`backend/.env`)

```env
# ===========================
# APP Config
# ===========================
APP_ENV=development
STORAGE_BACKEND=local
LOCAL_UPLOAD_DIR=./uploads
S3_BUCKET=
REDIS_URL=redis://localhost:6379/0

# ===========================
# PostgreSQL Config
# ===========================
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=lostfound

# ===========================
# Authentication Settings
# ===========================
JWT_SECRET_KEY=
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# ===========================
# Cookies Settings
# ===========================
COOKIE_SECURE=True
COOKIE_HTTPONLY=True
COOKIE_SAMESITE="strict"
```

### Frontend (`frontend/.env`)

```env
VITE_APP_ENV=development
VITE_API_BASE_URL=http://localhost:8000
```

---

## Cross-Cutting Concerns

**Auth flow:** Vue login → `POST /auth/login` → Cookies Saved in Session by Backend → Axios interceptor attaches `Authorization: Bearer <token>` to every request → FastAPI `get_current_user` dependency decodes token and injects user.

**File upload flow:** Vue `PhotoUpload.vue` → `multipart/form-data POST /items/{id}/photos` → FastAPI validates MIME + size → `storage.py` saves file → DB record created → URL returned and stored in Pinia item state.

**Geo search flow:** Vue `LocationPicker.vue` captures lat/lng (browser geolocation or manual input) → passes `lat`, `lng`, `radius` as query params → FastAPI `geo.py` builds Haversine SQL filter → results returned ordered by distance.
