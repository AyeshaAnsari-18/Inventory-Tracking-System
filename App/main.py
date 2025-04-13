from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
from datetime import datetime

app = FastAPI()
conn = sqlite3.connect("data/inventory.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product TEXT,
    type TEXT,  -- IN, SALE, REMOVAL
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
