"""
Neighbor Lost & Found — Demo Seed Script
==========================================
Creates realistic demo data by hitting the live API endpoints in order.

Usage:
    python seed.py
    BASE_URL=http://localhost:8080 python seed.py
    PHOTOS_DIR=./my_photos python seed.py

Folder structure for photos (place in ./seed_photos/ by default):
    seed_photos/
    ├── wallet.jpg
    ├── phone.jpg
    ├── dog.jpg
    ├── keys.jpg
    ├── school_bag.jpg
    ├── nid_card.jpg
    ├── airpods.jpg
    ├── bracelet.jpg
    ├── glasses.jpg
    ├── jacket.jpg
    ├── passport.jpg
    └── helmet.jpg

Supported formats: .jpg, .jpeg, .png, .webp
If a photo file is missing, a warning is printed and the item is created without a photo.
"""

import asyncio
import httpx
import os
from pathlib import Path
from datetime import date, timedelta

BASE_URL = os.environ.get("BASE_URL", "http://localhost:8080/api/v1")
PHOTOS_DIR = Path(os.environ.get("PHOTOS_DIR", "./seed_photos"))

MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}

# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

USERS = [
    {"name": "Rahim Chowdhury", "email": "rahim@demo.com",  "password": "password123"},
    {"name": "Nadia Islam",     "email": "nadia@demo.com",   "password": "password123"},
    {"name": "Karim Hossain",   "email": "karim@demo.com",   "password": "password123"},
    {"name": "Suma Begum",      "email": "suma@demo.com",    "password": "password123"},
]

# ---------------------------------------------------------------------------
# Items  (photo_file → filename stem inside PHOTOS_DIR, no extension needed)
# ---------------------------------------------------------------------------

ITEMS = [
    # --- Rahim's items ---
    {
        "owner": "rahim@demo.com",
        "photo_file": "wallet",
        "payload": {
            "type": "lost",
            "title": "Black Leather Wallet",
            "description": "Lost my black leather wallet near Shahbagh intersection. Contains NID card, some cash, and two debit cards. Please contact if found.",
            "category": "wallet",
            "date_occurred": str(date.today() - timedelta(days=2)),
            "lat": 23.7386, "lng": 90.3961,
            "location_name": "Shahbagh, Dhaka",
        },
    },
    {
        "owner": "rahim@demo.com",
        "photo_file": "phone",
        "payload": {
            "type": "lost",
            "title": "Samsung Galaxy S23 — Black",
            "description": "Lost my Samsung Galaxy S23 in black colour somewhere around Dhanmondi Lake area. Has a cracked screen protector on the bottom-left corner.",
            "category": "electronics",
            "date_occurred": str(date.today() - timedelta(days=1)),
            "lat": 23.7461, "lng": 90.3742,
            "location_name": "Dhanmondi Lake, Dhaka",
        },
    },
    {
        "owner": "rahim@demo.com",
        "photo_file": "dog",
        "payload": {
            "type": "lost",
            "title": "Golden Retriever — Buddy",
            "description": "Our golden retriever Buddy went missing near Gulshan 2 circle. He is 3 years old, friendly, and wearing a red collar with a tag.",
            "category": "pets",
            "date_occurred": str(date.today() - timedelta(days=3)),
            "lat": 23.7925, "lng": 90.4078,
            "location_name": "Gulshan 2, Dhaka",
        },
    },
    # --- Nadia's items ---
    {
        "owner": "nadia@demo.com",
        "photo_file": "keys",
        "payload": {
            "type": "found",
            "title": "Set of House Keys",
            "description": "Found a set of 4 keys on a blue keychain near Uttara Sector 7 mosque. Handing over to police if not claimed within 3 days.",
            "category": "keys",
            "date_occurred": str(date.today() - timedelta(days=1)),
            "lat": 23.8759, "lng": 90.3795,
            "location_name": "Uttara Sector 7, Dhaka",
        },
    },
    {
        "owner": "nadia@demo.com",
        "photo_file": "school_bag",
        "payload": {
            "type": "found",
            "title": "Child's School Bag — Blue Spiderman",
            "description": "Found a small blue Spiderman school bag near Mirpur 10 roundabout. Contains notebooks and a pencil case. Please describe contents to claim.",
            "category": "bag",
            "date_occurred": str(date.today() - timedelta(days=2)),
            "lat": 23.8060, "lng": 90.3666,
            "location_name": "Mirpur 10, Dhaka",
        },
    },
    {
        "owner": "nadia@demo.com",
        "photo_file": "nid_card",
        "payload": {
            "type": "found",
            "title": "National ID Card",
            "description": "Found an NID card near Farmgate bus stop. Not publishing the name here for privacy — please message with your details to verify.",
            "category": "documents",
            "date_occurred": str(date.today()),
            "lat": 23.7584, "lng": 90.3892,
            "location_name": "Farmgate, Dhaka",
        },
    },
    # --- Karim's items ---
    {
        "owner": "karim@demo.com",
        "photo_file": "airpods",
        "payload": {
            "type": "lost",
            "title": "AirPods Pro — White Case",
            "description": "Lost my AirPods Pro in a white case near Bashundhara City Mall. Last seen in the food court area on the 4th floor.",
            "category": "electronics",
            "date_occurred": str(date.today() - timedelta(days=4)),
            "lat": 23.7509, "lng": 90.3930,
            "location_name": "Bashundhara City, Panthapath",
        },
    },
    {
        "owner": "karim@demo.com",
        "photo_file": "bracelet",
        "payload": {
            "type": "found",
            "title": "Women's Silver Bracelet",
            "description": "Found a delicate silver bracelet with a heart charm near the Hatirjheel walking path. Kept safely. Please describe it to confirm ownership.",
            "category": "jewelry",
            "date_occurred": str(date.today() - timedelta(days=1)),
            "lat": 23.7614, "lng": 90.4134,
            "location_name": "Hatirjheel, Dhaka",
        },
    },
    # --- Suma's items ---
    {
        "owner": "suma@demo.com",
        "photo_file": "glasses",
        "payload": {
            "type": "lost",
            "title": "Prescription Glasses — Brown Frame",
            "description": "Lost my reading glasses with brown rectangular frames near Banani 11 road. Power is -2.5 on both eyes. Very important to me.",
            "category": "other",
            "date_occurred": str(date.today() - timedelta(days=2)),
            "lat": 23.7938, "lng": 90.4031,
            "location_name": "Banani, Dhaka",
        },
    },
    {
        "owner": "suma@demo.com",
        "photo_file": "jacket",
        "payload": {
            "type": "lost",
            "title": "Blue Denim Jacket",
            "description": "Left my blue denim jacket at a cafe in Mohammadpur. Has a small patch on the left sleeve. Name tag inside reads 'Suma'.",
            "category": "clothing",
            "date_occurred": str(date.today() - timedelta(days=5)),
            "lat": 23.7614, "lng": 90.3574,
            "location_name": "Mohammadpur, Dhaka",
        },
    },
    {
        "owner": "suma@demo.com",
        "photo_file": "passport",
        "payload": {
            "type": "found",
            "title": "Passport — Found Near Airport",
            "description": "Found a Bangladeshi passport near Hazrat Shahjalal Airport departure gate. Urgent — please contact immediately if it belongs to you.",
            "category": "documents",
            "date_occurred": str(date.today()),
            "lat": 23.8480, "lng": 90.4066,
            "location_name": "Hazrat Shahjalal Airport, Dhaka",
        },
    },
    {
        "owner": "suma@demo.com",
        "photo_file": "helmet",
        "payload": {
            "type": "found",
            "title": "Black Motorcycle Helmet",
            "description": "Found a black full-face motorcycle helmet near Tejgaon industrial area. Brand is Steelbird. No visible damage.",
            "category": "other",
            "date_occurred": str(date.today() - timedelta(days=3)),
            "lat": 23.7706, "lng": 90.3961,
            "location_name": "Tejgaon, Dhaka",
        },
    },
]

# ---------------------------------------------------------------------------
# Claims
# ---------------------------------------------------------------------------

CLAIMS = [
    {
        "claimant": "karim@demo.com",
        "item_title": "Black Leather Wallet",
        "opening_message": "Hi! I think I found your wallet near Shahbagh. I handed it to the tea stall owner at the corner. It had an NID card and some cash inside. Please message me to arrange pickup.",
        "replies": [
            ("rahim@demo.com", "Thank you so much! Can you describe the wallet in more detail? What colour was the inside lining?"),
            ("karim@demo.com", "The inside lining is dark red/maroon. There are two debit cards — one from Dutch Bangla, one from BRAC Bank. And a photo ID."),
            ("rahim@demo.com", "That's definitely mine! The BRAC Bank card ends in 4821. When can we meet?"),
            ("karim@demo.com", "I'm free tomorrow afternoon near Shahbagh metro station exit. Around 4pm works?"),
            ("rahim@demo.com", "Perfect, see you then. I'll approve the claim now. Thank you so much!"),
        ],
        "resolve": "approved",
    },
    {
        "claimant": "suma@demo.com",
        "item_title": "Samsung Galaxy S23 — Black",
        "opening_message": "Hello, I believe I saw this phone at Dhanmondi Lake yesterday. Someone else picked it up though — I saw them hand it in at a nearby shop. You might want to check the shops along road 27.",
        "replies": [
            ("rahim@demo.com", "Thank you for the tip. Can you describe the person or which shop specifically?"),
            ("suma@demo.com", "It was a small stationary shop near the lake entrance gate. The person who picked it up was wearing a green shirt."),
            ("rahim@demo.com", "I checked — they don't have it. I think this might not be the right lead, sorry."),
        ],
        "resolve": "rejected",
    },
    {
        "claimant": "rahim@demo.com",
        "item_title": "Set of House Keys",
        "opening_message": "Hi Nadia, I lost my house keys near Uttara Sector 7 two days ago. My keychain is blue with 4 keys — one larger Yale key and three smaller ones. One key has a small scratch on it. Is this a match?",
        "replies": [],
        "resolve": None,
    },
    {
        "claimant": "karim@demo.com",
        "item_title": "Child's School Bag — Blue Spiderman",
        "opening_message": "Hi! My son lost his school bag near Mirpur 10 last Tuesday. It's a blue Spiderman bag with his name 'Rafin' written inside the front pocket. Does that match?",
        "replies": [
            ("nadia@demo.com", "Yes! There is a name written inside. I can see 'Rafin' on a sticker. This is definitely your son's bag. When can you collect it?"),
            ("karim@demo.com", "That's great news! I can come to Mirpur 10 tomorrow morning around 10am. Where exactly are you located?"),
            ("nadia@demo.com", "I'm near the Agora supermarket on Mirpur 10. I'll be there by 10am. See you then!"),
        ],
        "resolve": None,
    },
]


# ---------------------------------------------------------------------------
# Photo helpers
# ---------------------------------------------------------------------------

def find_photo(stem: str) -> tuple[Path, str] | None:
    """
    Search PHOTOS_DIR for a file matching the stem in any supported format.
    Returns (path, mime_type) or None if not found.
    """
    for ext, mime in MIME_TYPES.items():
        path = PHOTOS_DIR / f"{stem}{ext}"
        if path.exists():
            return path, mime
    return None


async def upload_photo(
    client: httpx.AsyncClient, token: str, item_id: int, photo_stem: str
) -> None:
    result = find_photo(photo_stem)
    if result is None:
        print(f"    ⚠ Photo not found for '{photo_stem}' in {PHOTOS_DIR} — skipping")
        return

    photo_path, mime_type = result
    with open(photo_path, "rb") as f:
        photo_bytes = f.read()

    r = await client.put(
        f"/items/{item_id}/photo",
        files={"file": (photo_path.name, photo_bytes, mime_type)},
        cookies={"session_token": token},
    )
    if r.status_code == 200:
        print(f"    📷 Photo uploaded: {photo_path.name}")
    else:
        print(f"    ⚠ Photo upload failed for item {item_id} — {r.status_code}: {r.text[:100]}")


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def make_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)


async def register(client: httpx.AsyncClient, user: dict) -> None:
    r = await client.post("/auth/register", json=user)
    if r.status_code not in (201, 400):
        r.raise_for_status()
    label = "registered" if r.status_code == 201 else "already exists"
    print(f"  ✓ {user['email']} — {label}")


async def login(client: httpx.AsyncClient, email: str, password: str) -> str:
    r = await client.post("/auth/login", json={"email": email, "password": password})
    r.raise_for_status()
    token = r.cookies.get("session_token")
    if not token:
        raise ValueError(f"No session_token cookie returned for {email}")
    return token


async def create_item(client: httpx.AsyncClient, token: str, payload: dict) -> dict:
    r = await client.post("/items/", json=payload, cookies={"session_token": token})
    r.raise_for_status()
    return r.json()["data"]


async def create_claim(
    client: httpx.AsyncClient, token: str, item_id: int, opening_message: str
) -> dict:
    r = await client.post(
        f"/items/{item_id}/claim",
        json={"opening_message": opening_message},
        cookies={"session_token": token},
    )
    r.raise_for_status()
    return r.json()["data"]


async def send_message(
    client: httpx.AsyncClient, token: str, claim_id: int, body: str
) -> None:
    r = await client.post(
        f"/items/claims/{claim_id}/messages",
        json={"body": body},
        cookies={"session_token": token},
    )
    r.raise_for_status()


async def resolve_claim(
    client: httpx.AsyncClient, token: str, claim_id: int, status: str
) -> None:
    r = await client.patch(
        f"/items/claims/{claim_id}/resolve",
        json={"status": status},
        cookies={"session_token": token},
    )
    r.raise_for_status()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def seed():
    print("\n🌱 Neighbor Lost & Found — Seeding demo data\n")

    if not PHOTOS_DIR.exists():
        print(f"⚠  Photos directory '{PHOTOS_DIR}' not found — items will be created without photos.\n"
              f"   Create the folder and add images to include them.\n")
    else:
        print(f"📁 Photos directory: {PHOTOS_DIR.resolve()}\n")

    async with make_client() as client:

        # 1. Register
        print("👤 Registering users...")
        for user in USERS:
            await register(client, user)

        # 2. Login
        print("\n🔑 Logging in...")
        tokens: dict[str, str] = {}
        for user in USERS:
            tokens[user["email"]] = await login(client, user["email"], user["password"])
            print(f"  ✓ {user['email']}")

        # 3. Create items + upload photos
        print("\n📦 Creating items...")
        item_map: dict[str, dict] = {}

        for item_def in ITEMS:
            token = tokens[item_def["owner"]]
            item = await create_item(client, token, item_def["payload"])
            item_map[item_def["payload"]["title"]] = item
            title = item_def["payload"]["title"]
            location = item_def["payload"]["location_name"]
            itype = item_def["payload"]["type"].upper()
            print(f"  ✓ [{itype}] {title} — {location}")

            await upload_photo(client, token, item["id"], item_def["photo_file"])

        # 4. Claims + messages
        print("\n💬 Creating claims and message threads...")
        for claim_def in CLAIMS:
            item = item_map.get(claim_def["item_title"])
            if not item:
                print(f"  ✗ Item not found: {claim_def['item_title']}")
                continue

            claimant_token = tokens[claim_def["claimant"]]
            claim = await create_claim(
                client, claimant_token, item["id"], claim_def["opening_message"]
            )
            claim_id = claim["id"]
            print(f"  ✓ Claim on '{claim_def['item_title']}' by {claim_def['claimant']}")

            for sender_email, body in claim_def["replies"]:
                await send_message(client, tokens[sender_email], claim_id, body)
                print(f"    💬 {sender_email}: {body[:65]}...")

            if claim_def["resolve"]:
                owner_email = next(
                    i["owner"] for i in ITEMS
                    if i["payload"]["title"] == claim_def["item_title"]
                )
                await resolve_claim(client, tokens[owner_email], claim_id, claim_def["resolve"])
                emoji = "✅" if claim_def["resolve"] == "approved" else "❌"
                print(f"    {emoji} Claim {claim_def['resolve'].upper()} by {owner_email}")

        # 5. Summary
        print("\n" + "─" * 45)
        print("✅ Seed complete!")
        print("─" * 45)
        print(f"  Users    : {len(USERS)}")
        print(f"  Items    : {len(ITEMS)}")
        print(f"  Claims   : {len(CLAIMS)}")
        print(f"  Approved : {sum(1 for c in CLAIMS if c['resolve'] == 'approved')}")
        print(f"  Rejected : {sum(1 for c in CLAIMS if c['resolve'] == 'rejected')}")
        print(f"  Pending  : {sum(1 for c in CLAIMS if c['resolve'] is None)}")
        print("─" * 45)
        print("  All passwords : password123")
        print("  Demo login    : rahim@demo.com / password123")
        print("─" * 45 + "\n")


if __name__ == "__main__":
    asyncio.run(seed())