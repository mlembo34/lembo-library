import requests

def lookup_book(isbn):
  isbn = isbn.strip()

  url = f"https://openlibrary.org/isbn/{isbn}.json"

  response = requests.get(url, timeout=10)

  if response.status_code != 200:
    return None
  
  data = response.json()

  title = data.get("title", "")

  authors = []
  for author in data.get("authors", []):
    key = author.get("key")
    if not key:
      continue
    author_url = f"https://openlibrary.org{key}.json"

    author_response = requests.get(author_url)
    if author_response.status_code == 200:
      author_data = author_response.json()
      authors.append(
        author_data.get("name", "")
      )

  return {
    "isbn": isbn,
    "title": title,
    "author": ", ".join(authors),
    "genre": "",
    "publisher": ", ".join(data.get("publishers", {})),
    "published_date": data.get("publish_date", ""),
    "summary": ""  
  }