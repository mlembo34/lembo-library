import streamlit as st

from library.page import setup_page

library = setup_page(
    title="Search Library",
    icon="🔍"
)

st.title("🔍 Search The Lembo Library")

search_text = st.text_input(
    "Search by title, author, genre, publisher, ISBN, or summary",
    placeholder="Example: Tolkien, Fantasy, Hobbit, 978..."
)

if not search_text.strip():
    st.info("Enter a search term above.")
else:
    results = library.search(search_text)

    if results.empty:
        st.warning("No matching books found.")
    else:
        st.success(f"Found {len(results)} matching book(s).")

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
            if col in results.columns
        ]

        st.dataframe(
            results[existing_columns],
            use_container_width=True,
            hide_index=True
        )