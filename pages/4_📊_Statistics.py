import streamlit as st

from library.page import setup_page

library = setup_page(
    title="Library Statistics",
    icon="📊"
)

st.title("📊 The Lembo Library Statistics")

books = library.books

if books.empty:
    st.info("Your library is empty.")
else:
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Books", library.total_books())

    with col2:
        st.metric("Unique Authors", library.total_authors())

    with col3:
        st.metric("Genres", library.total_genres())

    st.divider()

    if "Genre" in books.columns:
        genre_counts = (
            books["Genre"]
            .replace("", "Uncategorized")
            .fillna("Uncategorized")
            .value_counts()
        )

        st.subheader("Books by Genre")
        st.bar_chart(genre_counts)

    if "Author" in books.columns:
        author_counts = (
            books["Author"]
            .replace("", "Unknown")
            .fillna("Unknown")
            .value_counts()
            .head(10)
        )

        st.subheader("Top Authors")
        st.bar_chart(author_counts)

    if "Publisher" in books.columns:
        publisher_counts = (
            books["Publisher"]
            .replace("", "Unknown")
            .fillna("Unknown")
            .value_counts()
            .head(10)
        )

        st.subheader("Top Publishers")
        st.bar_chart(publisher_counts)