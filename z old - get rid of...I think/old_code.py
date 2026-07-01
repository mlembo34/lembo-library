### This is the code that looked at Google Books API...which is what I eventually want. ###
import requests

def lookup_book(isbn):
  url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"

  response = requests.get(url)

  if response.status_code != 200:
    print("Google API Error:")
    print(response.text)
    return {
      "error": f"API returned status {response.status_code}"
    }
  
  data = response.json()

  if data.get("totalItems", 0) == 0:
    return None
  
  info = data["items"][0]["volumeInfo"]

  return {
    "isbn": isbn,
    "title": info.get("title", ""),
    "author": ", ".join(info.get("authors", [])),
    "genre": ", ".join(info.get("categories", [])),
    "publisher": info.get("publisher", ""),
    "published_date": info.get("publishedDate", ""),
    "summary": info.get("description", "")
  }

### This is from the og manager.py file. Since changed to SQLite, don't think this is needed. ###
import pandas as pd

from library.sheets import connect, add_book, isbn_exists


class LibraryManager:

    def __init__(self):
        self.sheet = connect()
        self.books = self.load_books()

    def load_books(self):
        records = self.sheet.get_all_records()

        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records)

        text_columns = [
            "ISBN",
            "Title",
            "Author",
            "Genre",
            "Publisher",
            "Published Date",
            "Summary",
            "Date Added"
        ]

        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)

        return df

    def refresh(self):
        self.books = self.load_books()

    def total_books(self):
        return len(self.books)

    def total_authors(self):
        if self.books.empty or "Author" not in self.books.columns:
            return 0

        return self.books["Author"].replace("", pd.NA).dropna().nunique()

    def total_genres(self):
        if self.books.empty or "Genre" not in self.books.columns:
            return 0

        return self.books["Genre"].replace("", pd.NA).dropna().nunique()

    def latest_book(self):
        if self.books.empty:
            return None

        return self.books.iloc[-1]

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

        existing_columns = [
            col for col in searchable_columns
            if col in self.books.columns
        ]

        mask = self.books[existing_columns].astype(str).apply(
            lambda row: row.str.lower().str.contains(search_text).any(),
            axis=1
        )

        return self.books[mask]

    def add(self, book):
        if isbn_exists(self.sheet, book.isbn):
            return False

        add_book(self.sheet, book)
        self.refresh()

        return True


### This is the old Edit_Books.py code ###
import streamlit as st

from library.book import Book
from library.page import setup_page


library = setup_page(
    title="Edit Books",
    icon="✏️"
)

st.title("✏️ Edit Books")

books = library.books

if books.empty:
    st.info("Your library is empty.")
else:
    book_options = {
        f"{row['Title']} — {row['Author']} ({row['ISBN']})": row
        for _, row in books.iterrows()
    }

    selected_label = st.selectbox(
        "Choose a book to edit",
        list(book_options.keys())
    )

    selected = book_options[selected_label]

    original_isbn = selected["ISBN"]

    with st.form("edit_book_form"):
        isbn = st.text_input("ISBN", value=selected.get("ISBN", ""))
        title = st.text_input("Title", value=selected.get("Title", ""))
        author = st.text_input("Author", value=selected.get("Author", ""))
        genre = st.text_input("Genre", value=selected.get("Genre", ""))
        publisher = st.text_input("Publisher", value=selected.get("Publisher", ""))
        # -------- Rating ----------
        rating_options = [None, 1, 2, 3, 4, 5]
        current_rating = selected.get("Rating")
        if current_rating == "" or current_rating is None:
            current_rating = None
        else:
            current_rating = int(current_rating)
        rating = st.selectbox(
            "Rating", 
            rating_options,
            index=rating_options.index(current_rating)
            )
        # --------------------------
        shelf = st.text_input("Shelf")
        reading_status = st.selectbox(
            "Reading Status",
            ["", "Want to Read", "Reading", "Finished", "Paused", "Did Not Finish"]
        )
        published_date = st.text_input(
            "Published Date",
            value=selected.get("Published Date", "")
        )
        summary = st.text_area("Summary", value=selected.get("Summary", ""))
        cover_url = st.text_input("Cover URL", value=selected.get("Cover URL", ""))
        source = st.text_input("Source", value=selected.get("Source", ""))
        submitted = st.form_submit_button("Save Changes")

    if submitted:
        if not isbn.strip():
            st.warning("ISBN cannot be blank.")
        elif not title.strip():
            st.warning("Title cannot be blank.")
        else:
            updated_book = Book(
                isbn=isbn.strip(),
                title=title.strip(),
                author=author.strip(),
                genre=genre.strip(),
                publisher=publisher.strip(),
                published_date=published_date.strip(),
                summary=summary.strip(),
                cover_url=cover_url.strip(),
                source=source.strip(),
                rating=rating,
                shelf=shelf.strip(),
                reading_status=reading_status
            )

            library.update_book(original_isbn, updated_book)

            st.success("Book updated!")
            

### NEXT RETIRED CODE GOES BELOW ###