import streamlit as st

from library.page import setup_page
from library.preferences import load_preferences

library = setup_page(
  title = "The Lembo Library",
  icon = "📚"
)

preferences = load_preferences()

st.title(f"📚 {preferences['library_name']}")

col1, col2, col3 = st.columns(3)

with col1:
  st.metric("Total Books", library.total_books())
with col2:
  st.metric("Unique Authors", library.total_authors())  
with col3:
  st.metric("Genres", library.total_genres())

st.divider()

latest = library.latest_book()

if latest is not None:
  st.subheader("Most Recently Added")
  st.write(f"**Title:** {latest.get('Title', '')}")
  st.write(f"**Author:** {latest.get('Author', '')}")
  st.write(f"**ISBN:** {latest.get('ISBN', '')}")

else:
  st.info("Your library is empty. Add your first book from the Scan Book page.")

st.divider()

st.markdown("""
Use the sidebar to:

- 📷 Scan or enter new book
- 📖 Browse your collection
- 🔍 Search your library
- 📊 View statistics
- ⚙️ Change settings
""")
