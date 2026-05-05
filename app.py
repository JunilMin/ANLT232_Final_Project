import pydeck as pdk
import streamlit as st

from charts import distance_vs_rent_chart, rent_bar_chart, rent_distribution_chart
from data_utils import (
    UOP_LAT,
    UOP_LON,
    build_map_dataframe,
    filter_and_rank_listings,
    listings_to_dataframe,
)
from rentcast_api import get_api_key, search_rental_listings

st.set_page_config(page_title="UOP Stockton Apartment Rent Explorer", layout="wide")

st.title("UOP Stockton Apartment Rent Explorer")

st.write(
    "It helps you to compare rental listings near the University of the Pacific "
    "Stockton campus. It uses the RentCast API, calculates distance from UOP, and recommends "
    "apartments based on distance and rent."
)

st.header("Project Story")

st.write(
    "Finding housing near campus is not only about rent. Distance, location, and apartment features "
    "also matter. You can explore affordable and convenient rental options near UOP Stockton."
)

if not get_api_key():
    st.error("RENTCAST_API_KEY is missing. Add it to your .env file.")
    st.stop()

def show_pydeck_map(results_df):
    map_df = build_map_dataframe(results_df).dropna(subset=["latitude", "longitude"])

    if map_df.empty:
        st.warning("No location data is available for the map.")
        return

    rental_df = map_df[map_df["type"] == "Rental"]
    uop_df = map_df[map_df["type"] == "University"]

    layers = []

    if not rental_df.empty:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=rental_df,
                get_position="[longitude, latitude]",
                get_radius=140,
                get_fill_color=[60, 140, 255, 180],
                pickable=True,
            )
        )

    if not uop_df.empty:
        layers.append(
            pdk.Layer(
                "ScatterplotLayer",
                data=uop_df,
                get_position="[longitude, latitude]",
                get_radius=260,
                get_fill_color=[255, 60, 60, 230],
                pickable=True,
            )
        )

    view_state = pdk.ViewState(
        latitude=UOP_LAT,
        longitude=UOP_LON,
        zoom=10,
        pitch=0,
    )

    tooltip = {
        "html": """
        <b>{name}</b><br/>
        Type: {type}<br/>
        Rent: ${rent}<br/>
        Distance from UOP: {distance_from_uop_miles} miles
        """,
        "style": {
            "backgroundColor": "black",
            "color": "white",
        },
    }

    st.pydeck_chart(
        pdk.Deck(
            layers=layers,
            initial_view_state=view_state,
            tooltip=tooltip,
        )
    )

    st.caption("Red point is the UOP Stockton. Blue points are rental listings.")

with st.sidebar:
    st.header("Search Options")

    search_mode = st.radio("Search by", ["City", "ZIP Code"], horizontal=True)

    if search_mode == "City":
        city = st.text_input("City", value="Stockton")
        zip_code = ""
    else:
        city = ""
        zip_code = st.text_input("ZIP Code", value="95203")

    state = st.text_input("State", value="CA")
    limit = st.slider("Number of listings", 5, 50, 20, step=5)

    st.header("Filters")

    max_rent = st.slider("Maximum monthly rent", 500, 7000, 4000, step=100)

    max_distance = st.slider(
        "Maximum distance from UOP (miles)",
        1.0,
        150.0,
        100.0,
        step=1.0,
    )

    min_bedrooms = st.slider("Minimum bedrooms", 0, 5, 0)

    show_table = st.checkbox("Show detailed table", value=True)

    run_search = st.button("Search rentals", type="primary")

if not run_search:
    st.info("Choose a city or ZIP code in the sidebar, then click 'Search rentals'.")
    st.stop()

try:
    with st.spinner("Fetching rental listings from RentCast API..."):
        listings = search_rental_listings(
            city=city,
            state=state,
            zip_code=zip_code,
            limit=limit,
        )
        raw_df = listings_to_dataframe(listings)
        # print(raw_df.columns)
        # print(raw_df.head())


except Exception as exc:
    st.error(f"API request failed: {exc}")
    st.stop()

if raw_df.empty:
    st.warning("No rental listings were returned. Try another city or ZIP code.")
    st.stop()

filtered_df = filter_and_rank_listings(
    raw_df,
    max_rent,
    max_distance,
    min_bedrooms,
)

results_df = filtered_df if not filtered_df.empty else raw_df

if filtered_df.empty:
    st.warning(
        "Listings were found, but none matched the current filters. "
        "Showing unfiltered results instead."
    )

avg_rent = results_df["rent"].mean()
median_rent = results_df["rent"].median()

closest = (
    results_df.dropna(subset=["distance_from_uop_miles"])
    .sort_values("distance_from_uop_miles")
    .head(1)
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Average Rent", f"${avg_rent:,.0f}")
col2.metric("Median Rent", f"${median_rent:,.0f}")
col3.metric("Listings Shown", f"{len(results_df)}")

col4.metric(
    "Closest to UOP",
    f"{closest.iloc[0]['distance_from_uop_miles']:.1f} mi"
    if not closest.empty
    else "N/A",
)

tab1, tab2, tab3, tab4 = st.tabs(
    ["Overview", "Recommended Apartments", "Map", "Data Table"]
)

with tab1:
    st.subheader("Monthly rent by listing")

    bar_chart = rent_bar_chart(results_df)

    if bar_chart is not None:
        st.altair_chart(bar_chart, use_container_width=True)

    st.subheader("Distance from UOP vs. rent")

    scatter = distance_vs_rent_chart(results_df)

    if scatter is not None:
        st.altair_chart(scatter, use_container_width=True)
    else:
        st.info("Distance data is not available for these listings.")

    st.subheader("Rent distribution")

    distribution = rent_distribution_chart(results_df)

    if distribution is not None:
        st.altair_chart(distribution, use_container_width=True)

with tab2:
    st.subheader("Recommended apartments")

    st.write("Listings are ranked by shorter distance from UOP first, then lower rent.")

    display_cols = [
        "recommendation_rank",
        "name",
        "city",
        "zip",
        "rent",
        "bedrooms",
        "bathrooms",
        "sqft",
        "distance_from_uop_miles",
        "listing_url",
    ]

    available_cols = [col for col in display_cols if col in results_df.columns]

    st.dataframe(
        results_df[available_cols],
        use_container_width=True,
        hide_index=True,
    )

with tab3:
    st.subheader("Map: UOP Stockton and rental listings")

    show_pydeck_map(results_df)

with tab4:
    if show_table:
        st.subheader("Cleaned API data")

        st.dataframe(
            results_df,
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Turn on 'Show detailed table' in the sidebar to view the data table.")

st.caption(
    "Data source: RentCast API. Distances are calculated using UOP Stockton campus coordinates."
)