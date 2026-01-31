from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from typing import List, Optional
from pathlib import Path
import math
import time

DB_PATH = Path("/app/backend/db.sqlite3")

app = FastAPI(title="Home Cost-Benefit Tracker")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = get_conn()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            cost REAL NOT NULL,
            severity INTEGER NOT NULL,
            frequency INTEGER NOT NULL,
            benefit_score INTEGER NOT NULL,
            cost_score INTEGER NOT NULL,
            net_score INTEGER NOT NULL,
            created_at INTEGER NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()

init_db()

class ItemIn(BaseModel):
    description: str
    cost: float
    severity: int
    frequency: int

class ItemOut(ItemIn):
    id: int
    benefit_score: int
    cost_score: int
    net_score: int
    created_at: int

def compute_scores(cost: float, severity: int, frequency: int) -> tuple[int, int, int]:
    benefit = severity + frequency
    if cost <= 0:
        cost_score = 1
    else:
        cost_score = max(1, int(round(math.log10(cost))) + 1)
    net = benefit - cost_score
    return benefit, cost_score, net

@app.get("/api/items", response_model=List[ItemOut])
def list_items():
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM items ORDER BY net_score DESC, created_at ASC"
    ).fetchall()
    conn.close()
    return [ItemOut(**dict(r)) for r in rows]

@app.post("/api/items", response_model=ItemOut)
def create_item(item: ItemIn):
    benefit, cost_score, net = compute_scores(item.cost, item.severity, item.frequency)
    ts = int(time.time())
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO items (description, cost, severity, frequency,
                           benefit_score, cost_score, net_score, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            item.description,
            item.cost,
            item.severity,
            item.frequency,
            benefit,
            cost_score,
            net,
            ts,
        ),
    )
    conn.commit()
    item_id = cur.lastrowid
    conn.close()
    return ItemOut(
        id=item_id,
        description=item.description,
        cost=item.cost,
        severity=item.severity,
        frequency=item.frequency,
        benefit_score=benefit,
        cost_score=cost_score,
        net_score=net,
        created_at=ts,
    )

@app.delete("/api/items/{item_id}")
def delete_item(item_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id = ?", (item_id,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"status": "ok", "deleted": item_id}
