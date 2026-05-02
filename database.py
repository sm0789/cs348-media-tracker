import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "media_tracker.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    conn = get_db()
    with open(schema_path, "r") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("Database initialized.")

if __name__ == "__main__":
    init_db()
