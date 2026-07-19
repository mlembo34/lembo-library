import sqlite3
from pathlib import Path


DB_PATH = Path("lembo_library.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            isbn TEXT UNIQUE,
            title TEXT,
            author TEXT,
            genre TEXT,
            publisher TEXT,
            published_date TEXT,
            summary TEXT,
            cover_url TEXT,
            source TEXT,
            rating INTEGER,
            shelf TEXT,
            room TEXT,
            reading_status TEXT,
            date_added TEXT
        )
    """)

    cursor.execute("PRAGMA table_info(books)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    if "room" not in existing_columns:
        cursor.execute("ALTER TABLE books ADD COLUMN room TEXT")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS book_collections (
            book_id INTEGER,
            collection_id INTEGER,
            PRIMARY KEY (book_id, collection_id),
            FOREIGN KEY (book_id) REFERENCES books(id),
            FOREIGN KEY (collection_id) REFERENCES collections(id)
        )
    """)

    conn.commit()
    conn.close()
