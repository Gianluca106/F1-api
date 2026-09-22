"""Jolpica-F1 (Ergast successor) data access: drivers' championship standings."""

import pandas as pd
import requests
import streamlit as st

STANDINGS_URL = "https://api.jolpi.ca/ergast/f1/{year}/driverStandings.json"


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_driver_standings(year: int) -> pd.DataFrame:
    """Fetch the drivers' championship standings for a season, ordered by position."""
    r = requests.get(STANDINGS_URL.format(year=year), timeout=15)
    r.raise_for_status()
    standings_lists = r.json()["MRData"]["StandingsTable"]["StandingsLists"]
    if not standings_lists:
        return pd.DataFrame()

    rows = []
    for entry in standings_lists[0]["DriverStandings"]:
        constructors = entry.get("Constructors") or []
        rows.append({
            "position": int(entry["position"]),
            "points": float(entry["points"]),
            "wins": int(entry["wins"]),
            "code": entry["Driver"]["code"],
            "given_name": entry["Driver"]["givenName"],
            "family_name": entry["Driver"]["familyName"],
            "constructor": constructors[0]["name"] if constructors else "",
        })
    return pd.DataFrame(rows).sort_values("position").reset_index(drop=True)
