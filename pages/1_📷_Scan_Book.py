import streamlit as st

from library.lookup import BookLookupService
from library.page import setup_page
from library.components.book_editor import book_editor
from library.components.barcode_scanner import barcode_scanner


library = setup_page(
    title="Scan Book",
    icon="📷"
)

st.title("📷 Scan Book")

lookup_service = BookLookupService()

st.subheader("Scan or Enter ISBN")

scan_mode = st.radio(
    "Choose input method",
    ["Type ISBN", "Scan Barcode"],
    horizontal=True
)

isbn = ""

if scan_mode == "Type ISBN":
    isbn = st.text_input(
        "Enter ISBN",
        placeholder="9780547928227"
    )

else:
    scanned_isbn = barcode_scanner()

    if scanned_isbn:
        st.success(f"Scanned ISBN: {scanned_isbn}")
        isbn = scanned_isbn

if st.button("Lookup Book"):

    if not isinstance(isbn, str) or not isbn.strip():
        st.warning("Please enter or scan an ISBN.")

    else:
        with st.spinner("Looking up book..."):
            book = lookup_service.lookup(isbn)

        if not book:
            st.error("Book not found or lookup service timed out.")
        else:
            st.session_state["scanned_book"] = book

if "scanned_book" in st.session_state:

    book = st.session_state["scanned_book"]

    st.divider()

    st.subheader("Review Book Before Saving")

    if book.cover_url and book.cover_url.lower() != "nan":
        st.image(book.cover_url, width=180)

    edited_book = book_editor(
        book=book,
        form_key="scan_book_form"
    )

    if edited_book:

        if not edited_book.isbn:
            st.warning("ISBN cannot be blank.")

        elif not edited_book.title:
            st.warning("Title cannot be blank.")

        elif library.isbn_exists(edited_book.isbn):
            st.warning("This book is already in The Lembo Library.")

        else:
            added = library.add(edited_book)

            if added:
                st.success("Book added to The Lembo Library!")
                del st.session_state["scanned_book"]
                st.rerun()

            else:
                st.warning("This book is already in The Lembo Library.")