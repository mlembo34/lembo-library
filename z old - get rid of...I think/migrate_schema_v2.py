import sqlite3

from library.database import DB_PATH, initialize_database


initialize_database()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


def add_column_if_missing(table, column, column_type):
    cursor.execute(f"PRAGMA table_info({table})")
    existing_columns = [row[1] for row in cursor.fetchall()]

    if column not in existing_columns:
        cursor.execute(
            f"ALTER TABLE {table} ADD COLUMN {column} {column_type}"
        )
        print(f"Added column: {column}")
    else:
        print(f"Column already exists: {column}")


add_column_if_missing("books", "rating", "INTEGER")
add_column_if_missing("books", "shelf", "TEXT")
add_column_if_missing("books", "reading_status", "TEXT")

conn.commit()
conn.close()

print("Schema migration complete.")