import pandas as pd
import streamlit as st

from library.page import setup_page
from library.print_export import build_library_pdf
from library.preferences import load_preferences
from library.utils import author_sort_key


READ_NOT_OWNED = "Read - Not Owned"


def shelf_group(book):
  if str(book.get("Reading Status", "")).strip() == READ_NOT_OWNED:
    return READ_NOT_OWNED

  genre = str(book.get("Genre", "")).strip()
  return genre if genre and genre.lower() != "nan" else "Uncategorized"


def suggested_order(room_books, preferences):
  ordered = room_books.copy()
  ordered["Shelf"] = ordered.apply(shelf_group, axis=1)
  ordered["Author Sort"] = ordered["Author"].apply(author_sort_key)
  ordered["Shelf Rank"] = 0
  not_owned = ordered["Shelf"] == READ_NOT_OWNED
  if preferences["read_not_owned_position"] == "First":
    ordered.loc[~not_owned, "Shelf Rank"] = 1
  else:
    ordered.loc[not_owned, "Shelf Rank"] = 1
  book_sort = "Title" if preferences["shelf_sort"] == "Title" else "Author Sort"
  ordered = ordered.sort_values(
    by=["Shelf Rank", "Shelf", book_sort, "Title"],
    na_position="last"
  ).reset_index(drop=True)
  ordered["Position"] = ordered.groupby("Shelf").cumcount() + 1
  return ordered


def normalize_manual_order(edited):
  ordered = edited.copy()
  ordered["Shelf"] = ordered["Shelf"].fillna("").astype(str).str.strip()
  ordered.loc[ordered["Shelf"] == "", "Shelf"] = "Uncategorized"
  ordered.loc[
    ordered["Reading Status"].fillna("") == READ_NOT_OWNED,
    "Shelf"
  ] = READ_NOT_OWNED
  ordered["Position"] = pd.to_numeric(ordered["Position"], errors="coerce").fillna(999999)
  ordered = ordered.sort_values(
    by=["Shelf", "Position", "Author", "Title"],
    na_position="last"
  ).reset_index(drop=True)
  ordered["Position"] = ordered.groupby("Shelf").cumcount() + 1
  return ordered


library = setup_page(title="Organize Library", icon="📚")
preferences = load_preferences()

st.title("📚 Organize Library")

books = library.books

if books.empty:
  st.info("Your library is empty.")
elif "Room" not in books.columns:
  st.warning("Room column not found yet.")
else:
  rooms = sorted(
    books["Room"].replace("", "Unknown").fillna("Unknown").unique()
  )
  selected_room = st.selectbox("Choose a room", rooms)
  room_books = books[
    books["Room"].replace("", "Unknown").fillna("Unknown") == selected_room
  ].copy()

  st.subheader(selected_room)
  st.write(f"**{len(room_books)}** books in this room.")

  order_key = f"shelf_order::{selected_room}"

  if st.button("📖 Generate Shelf Order", type="primary"):
    st.session_state[order_key] = suggested_order(room_books, preferences)

  if order_key in st.session_state:
    st.subheader("📖 Manual Shelf Order")
    st.caption(
      "Edit a shelf name or position, then click Apply Changes. "
      "Books marked Read - Not Owned always stay together."
    )

    current_order = st.session_state[order_key]
    editor_columns = [
      "Position", "Shelf", "Title", "Author", "Genre", "Reading Status", "ISBN"
    ]
    editor_columns = [column for column in editor_columns if column in current_order.columns]

    edited_order = st.data_editor(
      current_order[editor_columns],
      key=f"shelf_editor::{selected_room}",
      hide_index=True,
      use_container_width=True,
      disabled=["Title", "Author", "Genre", "Reading Status", "ISBN"],
      column_config={
        "Position": st.column_config.NumberColumn("Position", min_value=1, step=1),
        "Shelf": st.column_config.TextColumn("Shelf", width="medium"),
        "Title": st.column_config.TextColumn("Title", width="large"),
      }
    )

    apply_col, reset_col = st.columns([1, 1])
    with apply_col:
      if st.button("✅ Apply Changes", use_container_width=True):
        st.session_state[order_key] = normalize_manual_order(edited_order)
        st.rerun()
    with reset_col:
      if st.button("↺ Reset Suggested Order", use_container_width=True):
        st.session_state[order_key] = suggested_order(room_books, preferences)
        st.rerun()

    st.subheader("📚 Shelf Preview")
    preview = st.session_state[order_key]
    for shelf, shelf_books in preview.groupby("Shelf", sort=False):
      with st.expander(f"📚 {shelf} ({len(shelf_books)} books)", expanded=True):
        for _, book in shelf_books.sort_values("Position").iterrows():
          st.write(
            f"{int(book['Position'])}. **{book.get('Author', '')}** — "
            f"{book.get('Title', '')}"
          )

  st.divider()
  st.subheader("🖨️ Printable Library")
  st.caption(
    "The PDF uses a compact two-column layout and includes the entire library, "
    "grouped by room and shelf. Your applied manual order for this room is included."
  )

  manual_orders = {
    room_name: st.session_state[key]
    for room_name in rooms
    if (key := f"shelf_order::{room_name}") in st.session_state
  }

  try:
    pdf_data = build_library_pdf(
      books,
      manual_orders,
      library_name=preferences["library_name"]
    )
    st.download_button(
      "📄 Download Compact Library PDF",
      data=pdf_data,
      file_name="home_library.pdf",
      mime="application/pdf",
      use_container_width=True
    )
  except ImportError:
    st.error(
      "PDF support needs the ReportLab package. Install the updated requirements "
      "with: pip install -r requirements.txt"
    )
