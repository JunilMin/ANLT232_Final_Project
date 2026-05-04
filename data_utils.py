from math import asin, cos, radians, sin, sqrt
from typing import Any

import pandas as pd

UOP_LAT = 37.9806
UOP_LON = -121.3123
UOP_NAME = "University of the Pacific - Stockton"


def haversine_miles(lat1, lon1, lat2, lon2):
    radius_miles = 3958.8
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return radius_miles * 2 * asin(sqrt(a))


def first_value(item, keys, default=None):
    for key in keys:
        value = item.get(key)
        if value not in (None, "", []):
            return value
    return default


def listings_to_dataframe(listings):
    rows = []

    for item in listings:
        address = first_value(item, ["formattedAddress", "addressLine1", "address", "streetAddress"], "")
        city = first_value(item, ["city"], "")
        state = first_value(item, ["state"], "")
        zip_code = first_value(item, ["zipCode", "zipcode", "zip"], "")
        lat = first_value(item, ["latitude", "lat"])
        lon = first_value(item, ["longitude", "lon", "lng"])
        rent = first_value(item, ["price", "rent", "monthlyRent", "listPrice"])

        lat = pd.to_numeric(lat, errors="coerce")
        lon = pd.to_numeric(lon, errors="coerce")
        rent = pd.to_numeric(rent, errors="coerce")
        distance = haversine_miles(UOP_LAT, UOP_LON, lat, lon) if pd.notna(lat) and pd.notna(lon) else None

        rows.append(
            {
                "name": address or f"{city}, {state} {zip_code}".strip(),
                "address": address,
                "city": city,
                "state": state,
                "zip": zip_code,
                "rent": rent,
                "bedrooms": first_value(item, ["bedrooms", "beds"]),
                "bathrooms": first_value(item, ["bathrooms", "baths"]),
                "sqft": first_value(item, ["squareFootage", "sqft", "livingArea"]),
                "property_type": first_value(item, ["propertyType", "type"], "Rental"),
                "latitude": lat,
                "longitude": lon,
                "distance_from_uop_miles": distance,
                "listing_url": first_value(item, ["listingUrl", "url"], ""),
            }
        )

    df = pd.DataFrame(rows)

    for col in ["rent", "bedrooms", "bathrooms", "sqft", "latitude", "longitude", "distance_from_uop_miles"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


def filter_and_rank_listings(df, max_rent, max_distance, min_bedrooms):
    filtered = df.dropna(subset=["rent"]).copy()
    filtered = filtered[filtered["rent"] <= max_rent]
    filtered = filtered[filtered["distance_from_uop_miles"].isna() | (filtered["distance_from_uop_miles"] <= max_distance)]

    if min_bedrooms > 0:
        filtered = filtered[filtered["bedrooms"].isna() | (filtered["bedrooms"] >= min_bedrooms)]

    filtered = filtered.sort_values(["distance_from_uop_miles", "rent"], ascending=[True, True], na_position="last")
    filtered.insert(0, "recommendation_rank", range(1, len(filtered) + 1))
    return filtered


def build_map_dataframe(df):
    uop_row = pd.DataFrame(
        [{"name": UOP_NAME, "latitude": UOP_LAT, "longitude": UOP_LON, "rent": None, "type": "University"}]
    )

    rental_rows = df.dropna(subset=["latitude", "longitude"]).copy()
    rental_rows["type"] = "Rental"

    return pd.concat([uop_row, rental_rows], ignore_index=True)
