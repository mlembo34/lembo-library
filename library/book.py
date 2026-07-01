from dataclasses import dataclass


@dataclass
class Book:
  isbn: str
  title: str = ""
  author: str = ""
  genre: str = ""
  publisher: str = ""
  published_date: str = ""
  summary: str = ""
  cover_url: str = ""
  source: str = ""
  rating: int | None = None
  shelf: str = ""
  reading_status: str = ""