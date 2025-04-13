# 📦 Inventory Tracking System

## 🛠️ Overview

This is a backend service for tracking inventory and stock movements, evolving from a single kiryana store to a scalable, multi-store, distributed system. Designed for high performance, data integrity, and observability.

---

## ✅ 1. Code (Partial Implementation)

Provided in `main.py` (Stage 1 - Single Store)
```python
from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
from datetime import datetime

app = FastAPI()
conn = sqlite3.connect("inventory.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product TEXT,
    type TEXT,
    quantity INTEGER,
    timestamp TEXT
)
''')
conn.commit()

class Movement(BaseModel):
    product: str
    type: str  # IN, SALE, REMOVAL
    quantity: int

@app.post("/stock/move")
def move_stock(movement: Movement):
    cursor.execute("INSERT INTO stock_movements (product, type, quantity, timestamp) VALUES (?, ?, ?, ?)",
                   (movement.product, movement.type, movement.quantity, datetime.utcnow().isoformat()))
    conn.commit()
    return {"status": "recorded"}

@app.get("/stock/{product}")
def get_stock(product: str):
    cursor.execute("SELECT type, quantity FROM stock_movements WHERE product=?", (product,))
    rows = cursor.fetchall()
    stock = 0
    for row in rows:
        if row[0] == "IN":
            stock += row[1]
        else:
            stock -= row[1]
    return {"product": product, "stock": stock}
```

---

## 📘 README

### 🔧 Design Decisions

- Used FastAPI for speed and ease of testing.
- SQLite for Stage 1 MVP; scalable to PostgreSQL in Stage 2.
- Event-driven updates introduced at Stage 3 for async processing.
- Redis used for caching stock reads (Stage 3).
- Audit logs introduced using a dedicated `audit_logs` table.

### 🧠 Assumptions

- Product units are consistent across stores.
- Inventory updated only through APIs (no direct DB manipulation).
- UTC is the standard for timestamps.
- No fractional quantities.
- Security is introduced progressively: Basic Auth → JWT/API Keys.

### 🌐 API Design

**Stage 1**
- `POST /stock/move`: Create stock movement (IN, SALE, REMOVAL)
- `GET /stock/{product}`: Get stock for a product

**Stage 2+**
- `POST /api/v1/stock-movement/`
- `GET /api/v1/inventory/{store_id}`
- `GET /api/v1/report?store_id=&from=&to=`

All APIs use JSON payloads, secured with Basic Auth (Stage 2), JWT/API key (Stage 3).

### 🧱 Evolution Rationale (v1 → v3)

| Version | Key Features |
|---------|--------------|
| **v1**  | CLI/REST with SQLite, track stock-ins/sales/removals |
| **v2**  | PostgreSQL, Multi-store, Auth, filtering, REST APIs |
| **v3**  | Scalable arch, async updates, Redis cache, audit logging, DB read/write separation |

---

## 📂 Project Structure

```
.
├── main.py            # FastAPI app (Stage 1)
├── README.md
└── inventory.db       # SQLite DB (generated on first run)
```