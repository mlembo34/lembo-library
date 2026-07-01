import requests
import streamlit as st

from library.book import Book

class BookLookupService:

  def __init__(self):
    self.timeout = 8

  @st.cache_data(show_spinner=False)
  def lookup_open_library(_self, isbn):
    isbn = isbn.strip()

    url = f"https://openlibrary.org/isbn/{isbn}.json"

    try:
      response = requests.get(url, timeout=_self.timeout)

    except requests.exceptions.ConnectTimeout:
      return None
    
    except requests.exceptions.ReadTimeout:
      return None
    
    except requests.exceptions.RequestException:
      return None
    
    if response.status_code != 200:
      return None
    
    data = response.json()

    authors = _self.get_open_library_authors(data)

    cover_url = ""

    if "covers" in data and len(data["covers"]) > 0:
      cover_id = data["covers"][0]
      cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"

    return Book(
      isbn=isbn,
      title=data.get("title", ""),
      author=", ".join(authors),
      genre="",
      publisher=", ".join(data.get("publishers", [])),
      published_date=data.get("publish_date", ""),
      summary="",
      cover_url=cover_url,
      source="Open Library"
    )
  

  def get_open_library_authors(self, data):
    authors = []

    for author in data.get("authors", []):
      key = author.get("key")

      if not key:
        continue

      author_url = f"https://openlibrary.org{key}.json"

      try:
        response = requests.get(author_url, timeout=self.timeout)

      except requests.exceptions.RequestException:
        continue

      if response.status_code == 200:
        author_data = response.json()
        name = author_data.get("name", "")

        if name:
          authors.append(name)

    return authors
  

  def lookup(self, isbn):
    book = self.lookup_open_library(isbn)

    if book:
      return book
    
    return None