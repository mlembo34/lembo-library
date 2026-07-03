import streamlit as st

from library.manager import LibraryManager
from library.supabase_manager import SupabaseLibraryManager


def get_library():
    if "library" not in st.session_state:

        use_supabase = st.secrets.get("USE_SUPABASE", False)

        if use_supabase:
            st.session_state.library = SupabaseLibraryManager()
        else:
            st.session_state.library = LibraryManager()

    return st.session_state.library