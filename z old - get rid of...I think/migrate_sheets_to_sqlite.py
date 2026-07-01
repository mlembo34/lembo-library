import sqlite3
from datetime import datetime

from library.database import DB_PATH, initialize_database
from library.sheets import connect


initialize_database()

sheet = connect()
records = sheet.get_all_records()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

count_added = 0
count_skipped = 0

for record in records:
    isbn = str(record.get("ISBN", "")).strip()

    if not isbn or isbn.upper() == "TEST":
        count_skipped += 1
        continue

    cursor.execute(
        "SELECT 1 FROM books WHERE isbn = ?",
        (isbn,)
    )

    if cursor.fetchone():
        count_skipped += 1
        continue

    cursor.execute(
        """
        INSERT INTO books (
            isbn,
            title,
            author,
            genre,
            publisher,
            published_date,
            summary,
            cover_url,
            source,
            date_added
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            isbn,
            str(record.get("Title", "")),
            str(record.get("Author", "")),
            str(record.get("Genre", "")),
            str(record.get("Publisher", "")),
            str(record.get("Published Date", "")),
            str(record.get("Summary", "")),
            "",
            "Google Sheets Import",
            str(record.get("Date Added", "")) or datetime.now().strftime("%Y-%m-%d")
        )
    )

    count_added += 1

conn.commit()
conn.close()

print(f"Migration complete.")
print(f"Books added: {count_added}")
print(f"Rows skipped: {count_skipped}")