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
        except requests.exceptions.RequestException:
            return None

        if response.status_code != 200:
            return None

        data = response.json()

        authors = _self.get_open_library_authors(data)
        subjects = _self.get_subjects(data)
        genre = _self.infer_genre(subjects)

        cover_url = ""

        if "covers" in data and len(data["covers"]) > 0:
            cover_id = data["covers"][0]
            cover_url = f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"

        return Book(
            isbn=isbn,
            title=data.get("title", ""),
            author=", ".join(authors),
            genre=genre,
            publisher=", ".join(data.get("publishers", [])),
            published_date=data.get("publish_date", ""),
            summary=_self.get_description(data),
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

    def get_subjects(self, data):
        subjects = []

        subjects.extend(data.get("subjects", []))

        for work in data.get("works", []):
            key = work.get("key")

            if not key:
                continue

            work_url = f"https://openlibrary.org{key}.json"

            try:
                response = requests.get(work_url, timeout=self.timeout)
            except requests.exceptions.RequestException:
                continue

            if response.status_code == 200:
                work_data = response.json()
                subjects.extend(work_data.get("subjects", []))

        return subjects

    def get_description(self, data):
        description = data.get("description", "")

        if isinstance(description, dict):
            return description.get("value", "")

        return description

    def infer_genre(self, subjects):
        subject_text = " ".join(subjects).lower()

        genre_keywords = {
            "Fantasy": ["fantasy", "magic", "wizards", "dragons", "mythical"],
            "Science Fiction": ["science fiction", "sci-fi", "space", "aliens", "future"],
            "Mystery": ["mystery", "detective", "crime", "murder", "suspense"],
            "Thriller": ["thriller", "spy", "espionage", "conspiracy"],
            "Horror": ["horror", "ghost", "supernatural", "vampire", "zombie"],
            "Biography": ["biography", "autobiography", "memoir"],
            "History": ["history", "historical", "war", "civilization"],
            "Mathematics": ["mathematics", "calculus", "algebra", "geometry", "statistics"],
            "Programming": ["programming", "python", "computer science", "software", "coding"],
            "Education": ["education", "teaching", "pedagogy", "schools"],
            "Sports": ["sports", "baseball", "basketball", "football", "soccer", "hockey"],
            "Science": ["science", "physics", "biology", "chemistry", "astronomy"],
            "Religion": ["religion", "christianity", "bible", "theology"],
            "Poetry": ["poetry", "poems"],
            "Drama": ["drama", "plays", "theater"],
            "Romance": ["romance", "love stories"],
            "Young Adult": ["young adult", "juvenile fiction", "teenagers"],
            "Children": ["children", "juvenile literature", "picture books"],
            "Comics": ["comics", "graphic novels", "manga"],
        }

        for genre, keywords in genre_keywords.items():
            for keyword in keywords:
                if keyword in subject_text:
                    return genre

        return ""

    def lookup(self, isbn):
        return self.lookup_open_library(isbn)