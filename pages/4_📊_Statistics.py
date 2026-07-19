import pandas as pd
import streamlit as st

from library.page import setup_page
from library.preferences import load_preferences


def clean_categories(series, fallback):
    cleaned = series.fillna("").astype(str).str.strip()
    return cleaned.mask(cleaned.str.lower().isin(["", "nan", "none"]), fallback)


def count_chart(series, label, limit=None):
    counts = series.value_counts().head(limit).rename("Books").to_frame()
    counts.index.name = label
    return counts


library = setup_page(title="Library Statistics", icon="📊")

preferences = load_preferences()

st.title(f"📊 {preferences['library_name']} Statistics")

books = library.books.copy()

if books.empty:
    st.info("Your library is empty.")
else:
    genres = clean_categories(books["Genre"], "Uncategorized")
    authors = clean_categories(books["Author"], "Unknown Author")

    if "Reading Status" in books.columns:
        statuses = clean_categories(books["Reading Status"], "Not Set")
        # Treat legacy records as read even before the Settings migration runs.
        statuses = statuses.replace("Finished", "Read")
    else:
        statuses = pd.Series("Not Set", index=books.index)

    rating_values = books.get("Rating", pd.Series(index=books.index, dtype=float))
    ratings = pd.to_numeric(rating_values, errors="coerce")
    valid_ratings = ratings.where(ratings.between(1, 5))
    read_count = int(statuses.isin(["Read", "Read - Not Owned"]).sum())
    read_percentage = round((read_count / len(books)) * 100) if len(books) else 0

    metric_cols = st.columns(4)
    metric_cols[0].metric("Total Books", len(books))
    metric_cols[1].metric("Unique Authors", authors[authors != "Unknown Author"].nunique())
    metric_cols[2].metric("Genres", genres[genres != "Uncategorized"].nunique())
    metric_cols[3].metric("Books Read", read_count)
    metric_cols[3].caption(f"{read_percentage}% of library")

    secondary_cols = st.columns(4)
    average_rating = valid_ratings.mean()
    secondary_cols[0].metric(
        "Average Rating",
        f"{average_rating:.1f} / 5" if pd.notna(average_rating) else "No ratings"
    )
    secondary_cols[1].metric("Rated Books", int(valid_ratings.notna().sum()))
    secondary_cols[2].metric("Unrated Books", int(valid_ratings.isna().sum()))
    secondary_cols[3].metric("Want to Read", int((statuses == "Want to Read").sum()))

    st.divider()

    st.subheader("Books by Genre")
    st.caption("All genres, ordered from the largest part of your collection to the smallest.")
    st.bar_chart(count_chart(genres, "Genre"), use_container_width=True)

    st.subheader("Top Authors")
    known_authors = authors[authors != "Unknown Author"]
    if known_authors.empty:
        st.info("No authors have been entered yet.")
    else:
        st.caption("The 15 authors with the most books in your library.")
        st.bar_chart(
            count_chart(known_authors, "Author", limit=15),
            use_container_width=True
        )

    st.subheader("Books Read")
    read_cols = st.columns([1, 2])
    with read_cols[0]:
        st.metric("Read", read_count)
        st.metric("Not Yet Read", len(books) - read_count)
        st.caption('Includes both "Read" and "Read - Not Owned."')
    with read_cols[1]:
        st.bar_chart(
            pd.DataFrame(
                {"Books": [read_count, len(books) - read_count]},
                index=pd.Index(["Read", "Not Yet Read"], name="Progress")
            ),
            use_container_width=True
        )

    st.subheader("Books by Rating")
    rating_labels = valid_ratings.map(
        lambda value: f"{int(value)} Star" if pd.notna(value) else "Unrated"
    )
    rating_order = ["1 Star", "2 Star", "3 Star", "4 Star", "5 Star", "Unrated"]
    rating_counts = rating_labels.value_counts().reindex(rating_order, fill_value=0)
    rating_counts.index.name = "Rating"
    st.bar_chart(rating_counts.rename("Books").to_frame(), use_container_width=True)

    st.divider()
    st.subheader("More Library Insights")

    if "Reading Status" in books.columns:
        st.markdown("#### Reading Status")
        st.bar_chart(
            count_chart(statuses, "Status"),
            use_container_width=True
        )

    if "Room" in books.columns:
        rooms = clean_categories(books["Room"], "Unknown")
        st.markdown("#### Books by Room")
        st.bar_chart(count_chart(rooms, "Room"), use_container_width=True)

    if "Publisher" in books.columns:
        publishers = clean_categories(books["Publisher"], "Unknown Publisher")
        known_publishers = publishers[publishers != "Unknown Publisher"]
        if not known_publishers.empty:
            st.markdown("#### Top Publishers")
            st.caption("The 10 most represented publishers.")
            st.bar_chart(
                count_chart(known_publishers, "Publisher", limit=10),
                use_container_width=True
            )

    if "Published Date" in books.columns:
        publication_years = pd.to_numeric(
            books["Published Date"].astype(str).str.extract(r"(\d{4})", expand=False),
            errors="coerce"
        )
        plausible_years = publication_years.between(1000, pd.Timestamp.now().year)
        decades = (publication_years[plausible_years] // 10 * 10).astype(int)
        if not decades.empty:
            decade_labels = decades.map(lambda year: f"{year}s")
            decade_counts = decade_labels.value_counts().sort_index()
            decade_counts.index.name = "Decade"
            st.markdown("#### Books by Publication Decade")
            st.bar_chart(
                decade_counts.rename("Books").to_frame(),
                use_container_width=True
            )

    missing_cols = st.columns(2)
    missing_cols[0].metric("Uncategorized Books", int((genres == "Uncategorized").sum()))
    missing_cols[1].metric("Books Missing an Author", int((authors == "Unknown Author").sum()))
