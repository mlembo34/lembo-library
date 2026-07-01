import streamlit as st

from library.page import setup_page

library = setup_page(
    title="Settings",
    icon="⚙️"
)

st.title("⚙️ Settings")

st.subheader("About The Lembo Library")

st.write("""
The Lembo Library is a personal book catalog app.

Current features:
- Add books by ISBN
- Save books to Google Sheets
- Browse your library
- Search your collection
- View statistics
""")

st.divider()

st.subheader("Coming Soon")

st.write("""
Planned features:
- Built-in iPhone barcode scanning
- Manual book entry
- Edit existing books
- Delete books
- Export to CSV
- Better genre dropdowns
""")