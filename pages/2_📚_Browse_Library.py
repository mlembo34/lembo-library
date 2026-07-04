import streamlit as st

from library.page import setup_page
from library.utils import author_sort_key


library = setup_page(
    title="Browse Library",
    icon="📚"
)

st.title("📚 Browse The Lembo Library")

books = library.books


def stars(rating):
    if rating in ["", "None", "nan"] or rating is None:
        return "No rating"

    try:
        rating = int(float(rating))
        return "★" * rating + "☆" * (5 - rating)
    except ValueError:
        return "No rating"


if books.empty:
    st.info("Your library is empty.")

else:
    st.write(f"Showing **{len(books)}** books.")

    search = st.text_input(
        "Filter books",
        placeholder="Search title, author, genre, shelf..."
    )

    if search.strip():
        books = library.search(search)

    if books.empty:
        st.warning("No matching books found.")

    else:
        books = books.copy()
        books["Author Sort"] = books["Author"].apply(author_sort_key)

        books = books.sort_values(
            by=["Room", "Genre", "Author Sort", "Title"],
            na_position="last" 
        )
            
        

        for _, book in books.iterrows():

            with st.container():
                col1, col2 = st.columns([1, 3])

                with col1:
                    cover_url = str(book.get("Cover URL", ""))

                    if cover_url and cover_url.lower() != "nan":
                        st.image(cover_url, width=120)
                    else:
                        st.markdown("📕")

                with col2:
                    st.subheader(book.get("Title", "Untitled"))

                    st.write(f"**Author:** {book.get('Author', '')}")

                    genre = book.get("Genre", "")
                    room = book.get("Room", "")
                    status = book.get("Reading Status", "")
                    rating = book.get("Rating", "")

                    st.write(f"**Rating:** {stars(rating)}")

                    if genre and str(genre).lower() != "nan":
                        st.write(f"**Genre:** {genre}")

                    if room and str(room).lower() != "nan":
                        st.write(f"**Room:** {room}")

                    if status and str(status).lower() != "nan":
                        st.write(f"**Status:** {status}")

                    st.caption(f"ISBN: {book.get('ISBN', '')}")

                st.divider()