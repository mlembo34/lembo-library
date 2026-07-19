import pandas as pd
import streamlit as st

from library.page import setup_page
from library.preferences import load_preferences, save_preferences
from library.print_export import build_library_pdf


def clean_values(series):
    values = series.fillna("").astype(str).str.strip()
    return sorted(value for value in values.unique() if value and value.lower() != "nan")


def show_message():
    message = st.session_state.pop("settings_message", None)
    if message:
        st.success(message)


library = setup_page(title="Settings", icon="⚙️")
books = library.books
preferences = load_preferences()

st.title("⚙️ Settings")
show_message()

st.subheader("Library Preferences")
existing_rooms = clean_values(books["Room"]) if "Room" in books.columns else []
room_options = list(dict.fromkeys(existing_rooms + ["Office", "Bedroom", "Classroom", "Unknown"]))
if preferences["default_room"] not in room_options:
    room_options.append(preferences["default_room"])

with st.form("library_preferences"):
    library_name = st.text_input("Library name", value=preferences["library_name"])
    default_room = st.selectbox(
        "Default room for new books",
        room_options,
        index=room_options.index(preferences["default_room"])
    )
    shelf_sort = st.selectbox(
        "Sort books within each shelf by",
        ["Author", "Title"],
        index=["Author", "Title"].index(preferences["shelf_sort"])
    )
    read_not_owned_position = st.selectbox(
        'Place the "Read - Not Owned" shelf',
        ["Last", "First"],
        index=["Last", "First"].index(preferences["read_not_owned_position"])
    )
    if st.form_submit_button("Save Preferences", type="primary"):
        save_preferences({
            "library_name": library_name.strip() or "My Library",
            "default_room": default_room,
            "shelf_sort": shelf_sort,
            "read_not_owned_position": read_not_owned_position,
        })
        st.session_state["settings_message"] = "Library preferences saved."
        st.rerun()

st.divider()
st.subheader("Export and Backup")
st.caption("CSV is the best complete data backup. The PDF is formatted for printing.")

export_col1, export_col2 = st.columns(2)
with export_col1:
    st.download_button(
        "Download Library CSV",
        data=books.to_csv(index=False).encode("utf-8"),
        file_name="library_backup.csv",
        mime="text/csv",
        use_container_width=True
    )
with export_col2:
    try:
        pdf_data = build_library_pdf(
            books,
            library_name=preferences["library_name"]
        )
        st.download_button(
            "Download Printable PDF",
            data=pdf_data,
            file_name="library.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except ImportError:
        st.error("Install the updated requirements to enable PDF exports.")

st.divider()
st.subheader("Data Quality")

nonblank_isbns = pd.Series(dtype=str)
if "ISBN" in books.columns:
    nonblank_isbns = books["ISBN"].fillna("").astype(str).str.strip()
    nonblank_isbns = nonblank_isbns[~nonblank_isbns.str.lower().isin(["", "nan", "none"])]

duplicate_isbns = int(nonblank_isbns.duplicated(keep=False).sum())
missing_genres = int(books["Genre"].fillna("").astype(str).str.strip().isin(["", "nan"]).sum())
missing_authors = int(books["Author"].fillna("").astype(str).str.strip().isin(["", "nan"]).sum())
missing_rooms = (
    int(books["Room"].fillna("").astype(str).str.strip().isin(["", "nan"]).sum())
    if "Room" in books.columns else len(books)
)

quality_cols = st.columns(4)
quality_cols[0].metric("Duplicate ISBN Entries", duplicate_isbns)
quality_cols[1].metric("Missing Genres", missing_genres)
quality_cols[2].metric("Missing Authors", missing_authors)
quality_cols[3].metric("Missing Rooms", missing_rooms)

if not any([duplicate_isbns, missing_genres, missing_authors, missing_rooms]):
    st.success("No common data-quality problems found.")
else:
    st.caption("Use Edit Books to correct individual missing or duplicate records.")

st.divider()
st.subheader("Bulk Rename")
st.caption("Rename a genre, room, or reading status across every matching book.")

field = st.selectbox("Field to rename", ["Genre", "Room", "Reading Status"])
field_values = clean_values(books[field]) if field in books.columns else []

if field_values:
    with st.form("bulk_rename"):
        old_value = st.selectbox("Current value", field_values)
        new_value = st.text_input("New value")
        submitted = st.form_submit_button("Rename All Matching Books")

    if submitted:
        replacement = new_value.strip()
        if not replacement:
            st.error("Enter a new value.")
        elif replacement == old_value:
            st.warning("The new value is the same as the current value.")
        else:
            changed = library.bulk_update_field(field, old_value, replacement)
            st.session_state["settings_message"] = (
                f'Updated {changed} book{"s" if changed != 1 else ""}: '
                f'"{old_value}" is now "{replacement}".'
            )
            st.rerun()
else:
    st.info(f"There are no {field.lower()} values to rename.")

st.divider()
st.subheader("Library Maintenance")

finished_count = 0
if "Reading Status" in books.columns:
    finished_count = int(books["Reading Status"].fillna("").eq("Finished").sum())

st.write(f"Books still labeled **Finished**: **{finished_count}**")
if finished_count and st.button('Change all "Finished" statuses to "Read"'):
    changed = library.update_reading_status("Finished", "Read")
    st.session_state["settings_message"] = (
        f'Updated {changed} book{"s" if changed != 1 else ""} to "Read".'
    )
    st.rerun()
elif not finished_count:
    st.caption('No books need to be changed from "Finished" to "Read".')
