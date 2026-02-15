# 📊 Diagrams — Neighborhood Lost-and-Found

---

## 1. User Flow Diagram

This diagram traces every journey a user can take through the system — from registration through posting, searching, claiming, and resolution.

```mermaid
flowchart TD

    A[Visitor Lands on Platform] --> B{Has Account?}

    B -->|No| C[Register]
    C --> D[Login]

    B -->|Yes| D[Login]

    D --> E[User Dashboard]

    %% Posting Flow
    E --> F[Create Item Post]
    F --> G[Upload Photos]
    G --> H[Set Location & Category]
    H --> I[Submit Item]
    I --> J[Item Status = Open]

    %% Search Flow
    E --> K[Search Items]
    K --> L[Filter by Category / Radius]
    L --> M[View Item Details]

    %% Claim Flow
    M --> N{Is This Mine?}
    N -->|Yes| O[Submit Claim with Proof]
    O --> P[Claim Status = Pending]

    %% Owner Actions
    J --> Q[Owner Receives Notification]
    P --> Q

    Q --> R[Review Claim]
    R --> S{Approve?}

    S -->|Yes| T[Claim Approved]
    T --> U[Item Status = Claimed]
    U --> V[Mark as Resolved]

    S -->|No| W[Claim Rejected]

    %% Messaging
    P --> X[Start Messaging]
    X --> Y[Conversation Between Users]

    %% Moderation
    M --> Z[Report Item]
    Z --> AA[Admin Review]
    AA --> AB{Valid Report?}
    AB -->|Yes| AC[Archive Item / Ban User]
    AB -->|No| AD[Dismiss Report]
```

---

## 2. Data Flow Diagram (DFD) — Level 0 (Context Diagram)

High-level view of who interacts with the system and what data flows in and out.

```mermaid
flowchart LR
    USER(["👤 Registered User"])
    ADMIN(["🛡️ Admin"])
    SYSTEM[["🏠 Lost & Found\nPlatform"]]
    DB[("🗄️ PostgreSQL")]
    STORE[("📦 File Storage\nLocal / S3")]
    SMTP[["📧 Email / Webhook\nNotifications"]]

    USER -- "Register / Login credentials" --> SYSTEM
    SYSTEM -- "Session Cookie Access Token" --> USER

    USER -- "Item post data + photos" --> SYSTEM
    SYSTEM -- "Stored item + photo URLs" --> USER

    USER -- "Search query + location" --> SYSTEM
    SYSTEM -- "Matching items list" --> USER

    USER -- "Claim message" --> SYSTEM
    SYSTEM -- "Claim status updates" --> USER

    USER -- "Messages to other party" --> SYSTEM
    SYSTEM -- "Message thread" --> USER

    USER -- "Report reason" --> SYSTEM

    ADMIN -- "Report action (dismiss/remove)" --> SYSTEM
    SYSTEM -- "Reports list + item data" --> ADMIN

    SYSTEM -- "Read / Write queries" --> DB
    DB -- "Records" --> SYSTEM

    SYSTEM -- "Upload file" --> STORE
    STORE -- "File URL" --> SYSTEM

    SYSTEM -- "Match alert / notification" --> SMTP
```

---

## 3. Item Status State Machine

Tracks all valid transitions for an item through its lifecycle.

```mermaid
stateDiagram-v2
    [*] --> open : Item posted

    open --> claimed : Claim approved by poster
    open --> archived : 30 days with no activity (auto)
    open --> removed : Admin removes post

    claimed --> resolved : Poster marks as resolved
    claimed --> open : Poster reopens (claimant no-show)
    claimed --> removed : Admin removes post

    resolved --> [*]
    archived --> open : Poster re-activates
    removed --> [*]
```

---

## 4. Claim Status State Machine

```mermaid
stateDiagram-v2
    [*] --> pending : Claim submitted

    pending --> approved : Poster approves
    pending --> rejected : Poster rejects

    approved --> [*]
    rejected --> [*]

    note right of approved
        All other pending claims
        on the same item are
        auto-rejected
    end note
```
