import streamlit as st

from library.book import Book


def book_editor(book=None, form_key="book_editor"):
    """
    Reusable form for editing or creating a Book.
    Returns a Book object if the form is submitted.
    """

    if book is None:
        book = Book(isbn="")

    with st.form(form_key):

        st.subheader("Book Details")

        col1, col2 = st.columns(2)

        with col1:
            isbn = st.text_input("ISBN", value=book.isbn)
            title = st.text_input("Title", value=book.title)
            author = st.text_input("Author", value=book.author)
            genre = st.text_input("Genre", value=book.genre)

        with col2:
            publisher = st.text_input("Publisher", value=book.publisher)
            published_date = st.text_input("Published Date", value=book.published_date)
            room_options = [
                "Office",
                "Bedroom",
                "Classroom",
                "Unknown"
            ]

            current_room = book.room or "Unknown"

            if current_room not in room_options:
                room_options.append(current_room)

            room = st.selectbox(
                "Room",
                room_options,
                index=room_options.index(current_room)
            )

            rating_options = [None, 1, 2, 3, 4, 5]

            current_rating = book.rating

            if (
                current_rating is None
                or current_rating == ""
                or current_rating == "None"
                or str(current_rating).lower() == "nan"
                ):
                current_rating = None
            else:
                current_rating = int(float(current_rating))

            rating = st.selectbox(
                "Rating",
                rating_options,
                index=rating_options.index(current_rating)
            )

        status_options = [
            "",
            "Want to Read",
            "Reading",
            "Finished",
            "Paused",
            "Did Not Finish"
        ]

        current_status = book.reading_status

        if current_status not in status_options:
            current_status = ""

        reading_status = st.selectbox(
            "Reading Status",
            status_options,
            index=status_options.index(current_status)
        )

        cover_url = st.text_input("Cover URL", value=book.cover_url)
        source = st.text_input("Source", value=book.source)

        summary = st.text_area(
            "Summary",
            value=book.summary,
            height=200
        )

        submitted = st.form_submit_button("Save Book")

    if submitted:
        return Book(
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
            room=room,
            reading_status=reading_status
        )

    return None