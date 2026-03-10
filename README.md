# Neighbor Lost & Found — User Flow

This document describes the user flow for the **Neighbor Lost & Found** application, a community platform for posting, searching, and resolving lost and found items.

---

## Flow Diagram

```mermaid
flowchart TD
    A([🏠 Landing Page]) --> B{User Authenticated?}
    B -- No --> C[Register / Login]
    C --> C1[Fill Name, Email, Password]
    C1 --> C2{Email Already Exists?}
    C2 -- Yes --> C3[Show Error: Account Exists]
    C3 --> C
    C2 -- No --> C4[Create Account ✓]
    C4 --> D
    B -- Yes --> D([🏘️ Home / Dashboard])

    D --> E[Browse Items Feed]
    D --> F[Post New Item]
    D --> G[Search & Filter Items]
    D --> H[Radius-Based Map Search]
    D --> I[My Posted Items]

    %% POST ITEM FLOW
    F --> F1[Select Type: Lost / Found]
    F1 --> F2[Select Category\nKey / Wallet / Pet / Phone / Other...]
    F2 --> F3[Add Title, Description, Photo]
    F3 --> F4[Set Location / Pin on Map]
    F4 --> F5[Submit Item Post]
    F5 --> F6[Item Published ✓]
    F6 --> I

    %% MY ITEMS FLOW
    I --> I1[View My Item]
    I1 --> I3[Edit Item Details]
    I3 --> I4[Update Title / Desc / Photo / Location]
    I4 --> I5[Save Changes ✓]

    %% SEARCH & FILTER FLOW
    G --> G1[Filter by Type: Lost / Found]
    G1 --> G2[Filter by Category]
    G2 --> G3[Enter Keyword]
    G3 --> G4[View Filtered Results]
    G4 --> K

    %% RADIUS SEARCH FLOW
    H --> H1{Browser Location\nPermission?}
    H1 -- Denied --> H2[Show Permission Error\nEnable Location to Use This Feature]
    H1 -- Granted --> H3[Get Current Coordinates]
    H3 --> H4[Select Search Radius\ne.g. 1km / 5km / 10km]
    H4 --> H5[Fetch Nearby Items]
    H5 --> H6[Display Items on Map View]
    H6 --> K

    %% ITEM DETAIL VIEW
    E --> K
    K([📄 Item Detail Page])
    K --> L{Is Current User\nthe Item Owner?}

    %% OWNER VIEW
    L -- Yes / Owner --> M[View All Claims & Sightings]
    M --> M1[Select a Claim / Sighting]
    M1 --> M2[View Conversation Thread]
    M2 --> M3[Reply to Message]
    M3 --> M4[Message Sent ✓]
    M2 --> M5{Make Decision}
    M5 -- Approve --> M6[Approve Claim / Sighting]
    M6 --> M7[Item Marked as Resolved ✓]
    M7 --> M8[All Other Claims/Sightings\nAuto-Rejected ✗]
    M5 -- Reject --> M10[Reject This Claim / Sighting ✗]
    M10 --> M

    %% NON-OWNER VIEW
    L -- No / Visitor --> N{Item Type?}
    N -- Lost Item --> N1[Submit Sighting\nI think I saw this!]
    N -- Found Item --> N2[Submit Claim\nThis belongs to me!]
    N1 & N2 --> O[Fill in Details + Message]
    O --> P{Already Submitted\na Claim/Sighting?}
    P -- Yes --> Q[View Your Existing\nClaim / Sighting Thread]
    P -- No --> R[Submit Claim / Sighting]
    R --> S[Claim/Sighting Created ✓]
    S --> Q

    %% MESSAGING ON CLAIM
    Q --> T[View Your Conversation\nwith Item Owner]
    T --> U[Send a New Message]
    U --> V[Message Posted ✓]
    V --> T
    T --> W{Claim Status?}
    W -- Pending --> X[⏳ Awaiting Owner Decision]
    W -- Approved --> Y[✅ Claim Approved!\nItem Resolved]
    W -- Rejected --> Z[❌ Claim Rejected]

    %% STYLES
    style A fill:#4f7942,color:#fff,stroke:#2d4f28
    style D fill:#4f7942,color:#fff,stroke:#2d4f28
    style K fill:#5b7fa6,color:#fff,stroke:#3a5f86
    style F6 fill:#2d7a2d,color:#fff,stroke:#1a5c1a
    style I5 fill:#2d7a2d,color:#fff,stroke:#1a5c1a
    style M7 fill:#2d7a2d,color:#fff,stroke:#1a5c1a
    style S fill:#2d7a2d,color:#fff,stroke:#1a5c1a
    style Y fill:#2d7a2d,color:#fff,stroke:#1a5c1a
    style M8 fill:#c0392b,color:#fff,stroke:#922b21
    style Z fill:#c0392b,color:#fff,stroke:#922b21
    style M10 fill:#c0392b,color:#fff,stroke:#922b21
    style H2 fill:#e67e22,color:#fff,stroke:#b35a00
    style C3 fill:#e67e22,color:#fff,stroke:#b35a00
    style X fill:#8e6bbf,color:#fff,stroke:#6a4f9e
```

---

## Flow Summary

### Authentication

- New users register with name, email, and password
- Duplicate email addresses are caught and surfaced as an error
- Authenticated users land on the Home / Dashboard

### Posting an Item

- Users select whether the item is **Lost** or **Found**
- A category is chosen (e.g. Key, Wallet, Pet, Phone)
- Title, description, photo, and a map-pinned location are added
- The published item appears under **My Posted Items**
- Owners can edit item details at any time

### Searching for Items

- **Feed browsing** — scroll all active items
- **Filter search** — filter by type (Lost/Found), category, and keyword
- **Radius search** — uses browser geolocation to surface items within a chosen radius (1km, 5km, 10km, etc.) on a map view; requires location permission

### Item Detail Page

The Item Detail Page behaves differently depending on whether the viewer is the item owner or a visitor.

**Owner view**

- Sees all claims and sightings submitted for the item
- Can open any claim/sighting to read the conversation thread and reply
- Can **Approve** a claim/sighting → item is marked Resolved and all remaining claims/sightings are auto-rejected
- Can **Reject** individual claims/sightings and continue reviewing others

**Visitor view**

- On a _Lost_ item: can submit a **Sighting** ("I think I saw this!")
- On a _Found_ item: can submit a **Claim** ("This belongs to me!")
- Can only see their own claim/sighting thread — other people's submissions are hidden
- Can message the owner within the thread
- Claim status is visible as: ⏳ Pending · ✅ Approved · ❌ Rejected

### Claim & Sighting Resolution

1. A visitor submits a claim or sighting with an initial message
2. The owner reviews it and may exchange messages in the thread
3. The owner approves or rejects:
   - **Approve** → item resolved, all other open claims/sightings auto-rejected
   - **Reject** → that specific claim is closed; the owner continues reviewing others
