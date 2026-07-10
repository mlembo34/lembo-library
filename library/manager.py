import sqlite3
import pandas as pd

from datetime import datetime
from library.database import DB_PATH


class LibraryManager:

    def __init__(self):
        self.books = self.load_books()

    def get_connection(self):
        return sqlite3.connect(DB_PATH)

    def load_books(self):
        conn = self.get_connection()

        df = pd.read_sql_query(
            """
            SELECT
                isbn AS ISBN,
                title AS Title,
                author AS Author,
                genre AS Genre,
                publisher AS Publisher,
                published_date AS "Published Date",
                summary AS Summary,
                cover_url AS "Cover URL",
                source AS Source,
                rating AS Rating,
                shelf AS Shelf,
                reading_status AS "Reading Status",
                date_added AS "Date Added"
            FROM books
            ORDER BY id DESC
            """,
            conn
        )

        conn.close()

        return df.astype(str)

    def refresh(self):
        self.books = self.load_books()

    def total_books(self):
        return len(self.books)

    def total_authors(self):
        if self.books.empty:
            return 0

        return self.books["Author"].replace("", pd.NA).dropna().nunique()

    def total_genres(self):
        if self.books.empty:
            return 0

        return self.books["Genre"].replace("", pd.NA).dropna().nunique()

    def latest_book(self):
        if self.books.empty:
            return None

        return self.books.iloc[0]

    def isbn_exists(self, isbn):
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT 1 FROM books WHERE isbn = ?",
            (isbn,)
        )

        result = cursor.fetchone()

        conn.close()

        return result is not None

    def add(self, book):
      if self.isbn_exists(book.isbn):
          return False

      conn = self.get_connection()
      cursor = conn.cursor()

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
              rating,
              shelf,
              reading_status,
              date_added
          )
          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
          """,
          (
              book.isbn,
              book.title,
              book.author,
              book.genre,
              book.publisher,
              book.published_date,
              book.summary,
              book.cover_url,
              book.source,
              book.rating,
              book.shelf,
              book.reading_status,
              datetime.now().strftime("%Y-%m-%d")
          )
      )

      conn.commit()
      conn.close()

      self.refresh()

      return True

    def search(self, search_text):
        if self.books.empty:
            return self.books

        search_text = search_text.lower()

        searchable_columns = [
            "ISBN",
            "Title",
            "Author",
            "Genre",
            "Publisher",
            "Published Date",
            "Summary"
        ]

        mask = self.books[searchable_columns].astype(str).apply(
            lambda row: row.str.lower().str.contains(search_text).any(),
            axis=1
        )

        return self.books[mask]
    

    def update_book(self, original_isbn, updated_book):
      conn = self.get_connection()
      cursor = conn.cursor()

      cursor.execute(
          """
          UPDATE books
          SET
              isbn = ?,
              title = ?,
              author = ?,
              genre = ?,
              publisher = ?,
              published_date = ?,
              summary = ?,
              cover_url = ?,
              source = ?,
              rating = ?,
              shelf = ?,
              reading_status = ?
          WHERE isbn = ?
          """,
          (
              updated_book.isbn,
              updated_book.title,
              updated_book.author,
              updated_book.genre,
              updated_book.publisher,
              updated_book.published_date,
              updated_book.summary,
              updated_book.cover_url,
              updated_book.source,
              updated_book.rating,
              updated_book.shelf,
              updated_book.reading_status,
              original_isbn
          )
      )

      conn.commit()
      conn.close()

      self.refresh()

    def delete_book(self, isbn):
      conn = self.get_connection()
      cursor = conn.cursor()

      cursor.execute(
          "DELETE FROM books WHERE isbn = ?",
          (isbn,)
      )

      deleted = cursor.rowcount > 0

      conn.commit()
      conn.close()

      self.refresh()

      return deleted