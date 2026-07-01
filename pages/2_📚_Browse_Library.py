import streamlit as st

from library.page import setup_page

library = setup_page(
    title="Browse Library",
    icon="📚"
)

st.title("📚 Browse The Lembo Library")

books = library.books

if books.empty:
    st.info("Your library is empty.")
else:
    st.write(f"Showing **{len(books)}** books.")

    display_columns = [
        "Title",
        "Author",
        "Genre",
        "Publisher",
        "Published Date",
        "ISBN",
        "Date Added"
    ]

    existing_columns = [
        col for col in display_columns
        if col in books.columns
    ]

    st.dataframe(
        books[existing_columns],
        width='stretch',
        hide_index=True
    )