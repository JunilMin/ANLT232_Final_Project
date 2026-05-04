import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.rentcast.io/v1"


def get_api_key():
    return (os.getenv("RENTCAST_API_KEY") or "").strip()


def search_rental_listings(city: str = "", state: str = "CA", zip_code: str = "", limit: int = 20):
    params: dict[str, Any] = {"status": "Active", "limit": limit}

    if city.strip():
        params["city"] = city.strip()
    if state.strip():
        params["state"] = state.strip()
    if zip_code.strip():
        params["zipCode"] = zip_code.strip()

    response = requests.get(
        f"{BASE_URL}/listings/rental/long-term",
        headers={"X-Api-Key": get_api_key(), "Accept": "application/json"},
        params=params,
        timeout=30,
    )
    response.raise_for_status()

    data = response.json()
    if isinstance(data, list):
        return data
    return data.get("data") or data.get("listings") or data.get("results") or []
