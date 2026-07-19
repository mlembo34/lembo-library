import pandas as pd
import streamlit as st

from datetime import datetime
from supabase import create_client


class SupabaseLibraryManager:

    def __init__(self):
        self.client = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )

        self.books = self.load_books()

    def load_books(self):
        response = (
            self.client
            .table("books")
            .select("*")
            .order("id", desc=True)
            .execute()
        )

        records = response.data

        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)

        df = df.rename(columns={
            "isbn": "ISBN",
            "title": "Title",
            "author": "Author",
            "genre": "Genre",
            "publisher": "Publisher",
            "published_date": "Published Date",
            "summary": "Summary",
            "cover_url": "Cover URL",
            "source": "Source",
            "rating": "Rating",
            "shelf": "Shelf",
            "room": "Room",
            "reading_status": "Reading Status",
            "date_added": "Date Added"
        })

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
        response = (
            self.client
            .table("books")
            .select("isbn")
            .eq("isbn", isbn)
            .execute()
        )

        return len(response.data) > 0

    def add(self, book):
        if self.isbn_exists(book.isbn):
            return False

        self.client.table("books").insert({
            "isbn": book.isbn,
            "title": book.title,
            "author": book.author,
            "genre": book.genre,
            "publisher": book.publisher,
            "published_date": book.published_date,
            "summary": book.summary,
            "cover_url": book.cover_url,
            "source": book.source,
            "rating": book.rating,
            "room": book.room,
            "reading_status": book.reading_status,
            "date_added": datetime.now().strftime("%Y-%m-%d")
        }).execute()

        self.refresh()

        return True

    def update_book(self, original_isbn, updated_book):
        self.client.table("books").update({
            "isbn": updated_book.isbn,
            "title": updated_book.title,
            "author": updated_book.author,
            "genre": updated_book.genre,
            "publisher": updated_book.publisher,
            "published_date": updated_book.published_date,
            "summary": updated_book.summary,
            "cover_url": updated_book.cover_url,
            "source": updated_book.source,
            "rating": updated_book.rating,
            "room": updated_book.room,
            "reading_status": updated_book.reading_status
        }).eq("isbn", original_isbn).execute()

        self.refresh()

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
            "Summary",
            "Room",
            "Reading Status"
        ]

        existing_columns = [
            col for col in searchable_columns
            if col in self.books.columns
        ]

        mask = self.books[existing_columns].astype(str).apply(
            lambda row: row.str.lower().str.contains(search_text).any(),
            axis=1
        )

        return self.books[mask]
    
    def delete_book(self, isbn):
      response = (
          self.client
          .table("books")
          .delete()
          .eq("isbn", isbn)
          .execute()
      )

      self.refresh()

      return bool(response.data)

    def update_reading_status(self, old_status, new_status):
      """Bulk-update a reading status and return the number of changed books."""
      matches = (
          self.client
          .table("books")
          .select("isbn")
          .eq("reading_status", old_status)
          .execute()
      )
      changed = len(matches.data)

      if changed:
          (
              self.client
              .table("books")
              .update({"reading_status": new_status})
              .eq("reading_status", old_status)
              .execute()
          )
          self.refresh()

      return changed

    def bulk_update_field(self, field, old_value, new_value):
      columns = {
          "Genre": "genre",
          "Room": "room",
          "Reading Status": "reading_status"
      }
      if field not in columns:
          raise ValueError("Unsupported bulk-update field")

      matches = (
          self.client.table("books")
          .select("isbn")
          .eq(columns[field], old_value)
          .execute()
      )
      changed = len(matches.data)
      if changed:
          (
              self.client.table("books")
              .update({columns[field]: new_value})
              .eq(columns[field], old_value)
              .execute()
          )
          self.refresh()
      return changed
