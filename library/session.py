import streamlit as st

from library.manager import LibraryManager

def get_library():
  """
  Returns the LibraryManager stored in the current Streamlit session.
  Creates it the first time it is requested.
  """

  if "library" not in st.session_state:
    st.session_state.library = LibraryManager()

  return st.session_state.library