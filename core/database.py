import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join("data", "marketsignal.db")

def init_db():
    os.makedirs("data", exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                signal_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                justification TEXT NOT NULL,
                reviewer TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)
        conn.commit()

def guardar_revision(signal_id, status, justification, reviewer="Analista de Turno"):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO reviews (signal_id, status, justification, reviewer, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (signal_id, status, justification, reviewer, datetime.now().isoformat()))
        conn.commit()

def obtener_revisiones():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT signal_id, status, justification, reviewer, created_at FROM reviews")
        rows = cursor.fetchall()
        return {row[0]: {"status": row[1], "justification": row[2], "reviewer": row[3], "date": row[4]} for row in rows}