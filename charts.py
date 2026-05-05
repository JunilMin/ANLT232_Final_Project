import altair as alt
import pandas as pd

def chart_data(df):
    chart_df = df.copy()
    chart_df["label"] = chart_df["name"].astype(str).str.slice(0, 28)
    return chart_df

def rent_bar_chart(df):
    chart_df = chart_data(df).dropna(subset=["rent"])

    return (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X("label:N", title="Apartment / Address", sort="-y", axis=alt.Axis(labelAngle=-45)),
            y=alt.Y("rent:Q", title="Monthly Rent ($)"),
            tooltip=["name", "city", "zip", "rent", "bedrooms", "bathrooms", "distance_from_uop_miles"],
        )
        .properties(title="Monthly Rent by Listing", height=360)
    )

def distance_vs_rent_chart(df):
    chart_df = chart_data(df).dropna(subset=["rent", "distance_from_uop_miles"])

    if chart_df.empty:
        return None

    return (
        alt.Chart(chart_df)
        .mark_circle(size=120, opacity=0.8)
        .encode(
            x=alt.X("distance_from_uop_miles:Q", title="Distance from UOP Stockton (miles)"),
            y=alt.Y("rent:Q", title="Monthly Rent ($)"),
            size=alt.Size("bedrooms:Q", title="Bedrooms"),
            tooltip=["name", "rent", "bedrooms", "bathrooms", "distance_from_uop_miles"],
        )
        .properties(title="Distance from UOP vs. Rent", height=380)
    )

def rent_distribution_chart(df):
    chart_df = chart_data(df).dropna(subset=["rent"])

    return (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X("rent:Q", bin=alt.Bin(maxbins=8), title="Monthly Rent ($)"),
            y=alt.Y("count():Q", title="Number of Listings"),
            tooltip=[alt.Tooltip("count():Q", title="Number of Listings")],
        )
        .properties(title="Rent Distribution", height=330)
    )