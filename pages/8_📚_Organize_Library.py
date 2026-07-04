import streamlit as st
from library.page import setup_page
from library.utils import author_sort_key

library = setup_page(
  title="Organize Library",
  icon="📚"
)

st.title("📚 Organize Library")

books = library.books

if books.empty:
  st.info("Your library is empty.")

else:
  if "Room" not in books.columns:
    st.warning("Room column not found yet.")
  else:
    room = sorted(
      books["Room"]
      .replace("", "Unknown")
      .fillna("Unknown")
      .unique()
    )

    selected_room = st.selectbox(
      "Choose a room",
      room
    )

    room_books = books[
      books["Room"].replace("", "Unknown").fillna("Unknown")
      == selected_room
    ]

    st.subheader(f"{selected_room}")

    st.write(f"**{len(room_books)}** books in this room.")

    st.divider()

    if st.button("📖 Generate Shelf Order"):
        st.session_state["show_shelf_order"] = True

    if st.session_state.get("show_shelf_order", False):

        st.subheader("📖 Suggested Shelf Order")

        shelf_order = room_books.copy()

        shelf_order["Genre"] = (
            shelf_order["Genre"]
            .replace("", "Uncategorized")
            .fillna("Uncategorized")
        )

        shelf_order["Author Sort"] = shelf_order["Author"].apply(author_sort_key)

        shelf_order = shelf_order.sort_values(
            by=["Genre", "Author Sort", "Title"],
            na_position="last"
        )

        current_genre = None

        for _, book in shelf_order.iterrows():

            if book["Genre"] != current_genre:
                current_genre = book["Genre"]
                st.markdown(f"### 📚 {current_genre}")

            st.write(
                f"**{book.get('Author', '')}** — {book.get('Title', '')}"
            )

        st.divider()

    genres = sorted(
      room_books["Genre"]
      .replace("", "Uncategorized")
      .fillna("Uncategorized")
      .unique()
    )

    for genre in genres:
      genre_books = room_books[
          room_books["Genre"].replace("", "Uncategorized").fillna("Uncategorized")
          == genre
      ].copy()

      genre_books["Author Sort"] = genre_books["Author"].apply(author_sort_key)

      genre_books = genre_books.sort_values(
          by=["Author Sort", "Title"],
          na_position="last"
      )

      with st.expander(f"📚 {genre} ({len(genre_books)} books)", expanded=True):
        for _, book in genre_books.iterrows():
          author = book.get("Author", "")
          title = book.get("Title", "")
          rating = book.get("Rating", "")

          st.write(f"**{author}** - {title}")

          if rating and str(rating).lower() != "nan":
            try:
              rating_num = int(float(rating))
              st.caption("★" * rating_num + "☆" * (5 - rating_num))
            except ValueError:
              pass

        st.divider()