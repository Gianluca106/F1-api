"""OpenF1 API data access layer: races, driver grids, laps and car telemetry."""

import time
from datetime import datetime, timezone

import pandas as pd
import requests
import streamlit as st

BASE_URL = "https://api.openf1.org/v1"


def _get(path: str, params: dict, timeout: int, retries: int = 3) -> list:
    """GET a JSON list from OpenF1, retrying with backoff on rate limits (429)."""
    for attempt in range(retries):
        r = requests.get(f"{BASE_URL}/{path}", params=params, timeout=timeout)
        if r.status_code == 429 and attempt < retries - 1:
            time.sleep(1.5 * (attempt + 1))
            continue
        r.raise_for_status()
        return r.json()
    return []


def relevant_years() -> list[int]:
    """Seasons the app offers: this year and last year."""
    current = datetime.now(timezone.utc).year
    return [current, current - 1]


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_races(year: int) -> pd.DataFrame:
    """Fetch all Race sessions already held in a given year, most recent first."""
    data = _get("sessions", {"year": year, "session_name": "Race"}, timeout=15)
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    if "is_cancelled" in df.columns:
        df = df[~df["is_cancelled"]]
    df["date_start"] = pd.to_datetime(df["date_start"], format="ISO8601")
    df = df[df["date_start"] < pd.Timestamp.now(tz="UTC")]
    if df.empty:
        return df
    df["label"] = df["circuit_short_name"] + " GP " + df["year"].astype(str)
    return df.sort_values("date_start", ascending=False).reset_index(drop=True)


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_grid(session_key: int) -> pd.DataFrame:
    """Fetch the full driver grid for a given race session."""
    data = _get("drivers", {"session_key": session_key}, timeout=15)
    if not data:
        return pd.DataFrame()

    df = pd.DataFrame(data)
    df = df.drop_duplicates(subset="driver_number")
    df["display_name"] = df["first_name"].str.title() + " " + df["last_name"].str.title()
    return df.sort_values("driver_number").reset_index(drop=True)


def _is_real_photo(url: str) -> bool:
    """
    F1's own media CDN returns a tiny generic grey-silhouette graphic
    (~700 bytes at this thumbnail size) for drivers it has no real headshot
    for yet, at the exact same URL shape as everyone else's — so the URL
    alone can't tell them apart. Real headshots at this same size run
    ~4-13KB, so a cheap HEAD request's Content-Length reliably tells the
    two apart.
    """
    try:
        r = requests.head(url, timeout=5, allow_redirects=True)
        size = int(r.headers.get("Content-Length", 0))
        return size > 2000
    except requests.exceptions.RequestException:
        return True  # can't check right now — don't punish the driver for it


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_latest_driver_info(races_df: pd.DataFrame, max_races: int = 6) -> pd.DataFrame:
    """
    Best-known grid row (photo, team colour, ...) per driver, scanning the most
    recent races backwards. A driver can be absent from the very latest race's
    grid (a reserve stood in) — looking a few races further back resolves that.

    Team colour / driver number always come from the driver's most recent
    appearance. The headshot is handled separately: if that most recent
    appearance only has F1's generic placeholder graphic on file, every other
    scanned race is checked for a real photo before giving up — a driver can
    go a whole season without F1 ever uploading a proper headshot for them.
    """
    found: dict[str, pd.Series] = {}
    grids: list[pd.DataFrame] = []
    for i, (_, race) in enumerate(races_df.head(max_races).iterrows()):
        if i > 0:
            time.sleep(0.3)  # be gentle with OpenF1's rate limit
        try:
            grid = fetch_grid(int(race["session_key"]))
        except requests.exceptions.RequestException:
            continue  # this race's data is unavailable right now, try the next
        if grid.empty:
            continue
        grids.append(grid)
        for _, row in grid.iterrows():
            code = row["name_acronym"]
            if code not in found:
                found[code] = row.copy()

    if not found:
        return pd.DataFrame()

    for code, row in found.items():
        url = row.get("headshot_url")
        if pd.notna(url) and _is_real_photo(url):
            continue
        real_url = None
        for grid in grids:
            match = grid.loc[grid["name_acronym"] == code, "headshot_url"]
            if match.empty or pd.isna(match.iloc[0]):
                continue
            if _is_real_photo(match.iloc[0]):
                real_url = match.iloc[0]
                break
        found[code]["headshot_url"] = real_url  # None if nowhere to be found

    return pd.DataFrame(found.values()).reset_index(drop=True)


@st.cache_data(ttl=300, show_spinner=False)
def fetch_laps(session_key: int, driver_number: int) -> pd.DataFrame | None:
    """Fetch every completed lap driven by a driver in a session."""
    data = _get("laps", {"session_key": session_key, "driver_number": driver_number}, timeout=15)
    if not data:
        return None
    df = pd.DataFrame(data)
    df["lap_duration"] = pd.to_numeric(df["lap_duration"], errors="coerce")
    return df.dropna(subset=["lap_duration"])


@st.cache_data(ttl=300, show_spinner=False)
def fetch_telemetry(session_key: int, driver_number: int, date_start: str, date_end: str) -> pd.DataFrame | None:
    """Fetch car telemetry samples within a time window."""
    data = _get("car_data", {
        "session_key": session_key,
        "driver_number": driver_number,
        "date>": date_start,
        "date<": date_end,
    }, timeout=20)
    if not data:
        return None
    df = pd.DataFrame(data)
    # OpenF1 timestamps sometimes drop the fractional seconds, which breaks
    # pandas' format auto-detection when it varies within the same column.
    df["date"] = pd.to_datetime(df["date"], format="ISO8601")
    df = df.sort_values("date").reset_index(drop=True)
    df["t_sec"] = (df["date"] - df["date"].iloc[0]).dt.total_seconds()
    return df
