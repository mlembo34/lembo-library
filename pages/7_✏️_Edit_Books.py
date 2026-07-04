import streamlit as st

from library.book import Book
from library.page import setup_page
from library.components.book_editor import book_editor


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

    st.divider()

    left_col, right_col = st.columns([1, 3])

    with left_col:
        cover_url_current = selected.get("Cover URL", "")

        if cover_url_current and cover_url_current.lower() != "nan":
            st.image(cover_url_current, width=180)
        else:
            st.info("No cover image")

    with right_col:
        st.subheader(selected.get("Title", "Untitled"))
        st.write(f"**Author:** {selected.get('Author', '')}")
        st.write(f"**ISBN:** {selected.get('ISBN', '')}")

    st.divider()

    selected_book = Book(
        isbn=selected.get("ISBN", ""),
        title=selected.get("Title", ""),
        author=selected.get("Author", ""),
        genre=selected.get("Genre", ""),
        publisher=selected.get("Publisher", ""),
        published_date=selected.get("Published Date", ""),
        summary=selected.get("Summary", ""),
        cover_url=selected.get("Cover URL", ""),
        source=selected.get("Source", ""),
        rating=selected.get("Rating", None),
        room=selected.get("Room", ""),
        reading_status=selected.get("Reading Status", "")
    )

    updated_book = book_editor(
        book=selected_book,
        form_key="edit_book_form"
    )

    if updated_book:
        if not updated_book.isbn:
            st.warning("ISBN cannot be blank.")

        elif not updated_book.title:
            st.warning("Title cannot be blank.")

        else:
            library.update_book(original_isbn, updated_book)

            st.success("Book updated!")
            st.rerun()