import streamlit as st

from library.page import setup_page
from library.components.book_editor import book_editor


library = setup_page(
    title="Manual Book Entry",
    icon="✍️"
)

st.title("✍️ Manual Book Entry")

new_book = book_editor(
    book=None,
    form_key="manual_entry_form"
)

if new_book:
    if not new_book.isbn:
        st.warning("Please enter an ISBN.")

    elif not new_book.title:
        st.warning("Please enter a title.")

    elif library.isbn_exists(new_book.isbn):
        st.warning("This book is already in The Lembo Library.")

    else:
        added = library.add(new_book)

        if added:
            st.success("Book added to The Lembo Library!")
            st.rerun()

        else:
            st.warning("This book is already in The Lembo Library.")