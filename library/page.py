import streamlit as st

from library.database import initialize_database
from library.session import get_library

def setup_page(title, icon="📚", layout="wide"):
  """
  Common setup for every Streamlit page.
  Initializes the database, sets the page config,
  and returns the shared LibraryManager.
  """

  st.set_page_config(
    page_title=title,
    page_icon=icon,
    layout=layout
  )

  initialize_database()

  return get_library()