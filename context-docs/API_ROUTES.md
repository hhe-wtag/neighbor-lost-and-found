# API Routes Reference

Base URL: `http://localhost:8000` (dev)

Auth: routes marked 🔒 require `Authorization: Bearer <token>` header.
Routes marked 🛡️ additionally require `role = admin`.

---

## Auth

### POST /auth/register

Register a new user account.

**Body**

```json
{ "name": "string", "email": "string", "password": "string" }
```

**Response 201**

```json
{
  "id": 1,
  "name": "string",
  "email": "string",
  "role": "user",
  "created_at": "..."
}
```

---

### POST /auth/login

Authenticate and receive a Session Cookie set.

**Body**

```json
{ "email": "string", "password": "string" }
```

**Response 200**

```json
{ "access_token": "string", "token_type": "bearer" }
```

---

### GET /auth/me 🔒

Return the currently authenticated user's profile.

**Response 200**

```json
{
  "id": 1,
  "name": "string",
  "email": "string",
  "role": "user",
  "contact_pref": "message",
  "created_at": "..."
}
```

---

## Items

### POST /items 🔒

Create a new lost or found post.

**Body**

```json
{
  "type": "lost",
  "title": "string",
  "description": "string",
  "category": "electronics",
  "date_occurred": "2024-01-15",
  "lat": 40.7128,
  "lng": -74.006,
  "location_name": "string"
}
```

**Response 201** — full `ItemOut` with empty `photos: []`

---

### GET /items

List recent open items, paginated.

**Query params:** `skip=0` · `limit=20`

**Response 200** — array of `ItemOut`

---

### GET /items/search

Search items by keyword, category, and/or location radius.

**Query params**

| Param      | Type   | Description                             |
| ---------- | ------ | --------------------------------------- |
| `query`    | string | Full-text search on title + description |
| `category` | string | Filter by category slug                 |
| `type`     | string | `lost` or `found`                       |
| `lat`      | float  | Centre latitude for geo filter          |
| `lng`      | float  | Centre longitude for geo filter         |
| `radius`   | float  | Radius in kilometres (default 10)       |
| `skip`     | int    | Pagination offset                       |
| `limit`    | int    | Page size (max 50)                      |

**Response 200** — array of `ItemOut`

---

### GET /items/{id}

Get full item detail including photos.

**Response 200**

```json
{
  "id": 1,
  "type": "lost",
  "title": "string",
  "description": "string",
  "category": "string",
  "date_occurred": "string",
  "lat": 0.0,
  "lng": 0.0,
  "location_name": "string",
  "status": "open",
  "photos": [{ "id": 1, "url": "string", "created_at": "..." }],
  "user": { "id": 1, "name": "string" },
  "created_at": "..."
}
```

---

### PATCH /items/{id} 🔒

Update an item. Owner only.

**Body** — any subset of create fields plus `"status": "resolved"`

**Response 200** — updated `ItemOut`

---

### DELETE /items/{id} 🔒

Delete an item. Owner or admin only.

**Response 204** No content

---

## Photos

### POST /items/{id}/photos 🔒

Upload one or more photos for an item. Owner only.

**Body** — `multipart/form-data`, field name `files`, accepts `image/jpeg`, `image/png`, `image/webp`. Max 5 MB per file, max 5 files per item.

**Response 201**

```json
[
  {
    "id": 1,
    "url": "/uploads/abc.jpg",
    "mime_type": "image/jpeg",
    "created_at": "..."
  }
]
```

---

## Claims

### POST /items/{id}/claims 🔒

Submit a claim on an item. Cannot claim own item.

**Body**

```json
{ "message": "string" }
```

**Response 201**

```json
{
  "id": 1,
  "item_id": 1,
  "user_id": 2,
  "message": "string",
  "status": "pending",
  "created_at": "..."
}
```

---

### GET /items/{id}/claims 🔒

List all claims on an item. Item owner only.

**Response 200** — array of `ClaimOut` with claimant user info

---

### PATCH /claims/{id} 🔒

Approve or reject a claim. Item owner only.

**Body**

```json
{ "status": "approved" }
```

Approving auto-rejects all other pending claims and sets `item.status = "claimed"`.

**Response 200** — updated `ClaimOut`

---

## Messages

### POST /items/{id}/messages 🔒

Send a message related to an item. Sender must be the poster or approved claimant.

**Body**

```json
{ "to_user_id": 2, "body": "string" }
```

**Response 201** — `MessageOut`

---

### GET /items/{id}/messages 🔒

Retrieve the message thread for an item. Participants only.

**Response 200** — array of `MessageOut` ordered by `created_at` ascending

---

## Reports

### POST /items/{id}/reports 🔒

Report a suspicious or inappropriate post.

**Body**

```json
{ "reason": "spam", "details": "string" }
```

**Response 201** — `ReportOut`

---

### GET /admin/reports 🔒🛡️

List all reports, filterable by status.

**Query params:** `status=pending` (optional)

**Response 200** — array of `ReportOut` with item and reporter info

---

### PATCH /admin/reports/{id} 🔒🛡️

Action a report.

**Body**

```json
{ "status": "actioned" }
```

Setting `status = "actioned"` also sets `item.status = "removed"`.

**Response 200** — updated `ReportOut`

---

## Common Response Shapes

### ItemOut

```json
{
  "id": 0,
  "type": "lost|found",
  "title": "",
  "description": "",
  "category": "",
  "date_occurred": "",
  "lat": 0.0,
  "lng": 0.0,
  "location_name": "",
  "status": "open|claimed|resolved|archived|removed",
  "is_archived": false,
  "expires_at": null,
  "photos": [],
  "user": { "id": 0, "name": "" },
  "created_at": "",
  "updated_at": ""
}
```

### Error shape (4xx / 5xx)

```json
{ "detail": "string" }
```
