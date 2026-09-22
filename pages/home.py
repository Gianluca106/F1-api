import pandas as pd
import streamlit as st

from f1_data import fetch_latest_driver_info, fetch_races, relevant_years
from f1_standings import fetch_driver_standings

st.markdown("### 🏆 Drivers' Championship Standings")

years = relevant_years()

# Standings: try this year first, fall back to last year if the season hasn't
# produced any results yet (e.g. before round 1).
standings_df, season = pd.DataFrame(), None
for year in years:
    standings_df = fetch_driver_standings(year)
    if not standings_df.empty:
        season = year
        break

if standings_df.empty:
    st.error("Couldn't load the championship standings right now. Try again later.")
    st.stop()

# Driver photos & team colours: scan the last few races, since a driver can be
# missing from the very latest one (reserve stand-in) or have no headshot yet.
races_df = pd.DataFrame()
for year in years:
    races_df = fetch_races(year)
    if not races_df.empty:
        break

info_df = fetch_latest_driver_info(races_df) if not races_df.empty else pd.DataFrame()

if not info_df.empty:
    merged = standings_df.merge(
        info_df[["name_acronym", "headshot_url", "team_colour", "driver_number", "session_key"]],
        left_on="code", right_on="name_acronym", how="left"
    )
else:
    merged = standings_df.copy()
    for col in ("headshot_url", "team_colour", "driver_number", "session_key"):
        merged[col] = None

merged = merged.sort_values("position").reset_index(drop=True)

st.caption(f"Season {season} · standings update after every race · click a driver for their latest telemetry")

slots = []
for _, row in merged.iterrows():
    color = f"#{row['team_colour']}" if pd.notna(row["team_colour"]) else "#e8002d"
    if pd.notna(row["headshot_url"]):
        photo_html = f'<img src="{row["headshot_url"]}" class="driver-photo" />'
    else:
        photo_html = '<div class="driver-photo placeholder"></div>'

    if pd.notna(row["driver_number"]):
        target = f'/telemetry?driver={int(row["driver_number"])}&session={int(row["session_key"])}'
    else:
        target = "/telemetry"

    wins_label = f"{int(row['wins'])} WIN{'S' if row['wins'] != 1 else ''}"
    # target="_self" makes it explicit this stays in the current tab
    # (Streamlit's markdown sanitizer strips onclick/JS handlers, so a plain
    # link is the only way to make the card clickable).
    slot_class = "pole" if len(slots) % 2 == 0 else "pair"
    slots.append(
        f'<a class="driver-card {slot_class}" href="{target}" target="_self" style="border-left-color:{color}">'
        f'<div class="driver-pos" style="color:{color}">P{int(row["position"])}</div>'
        f'{photo_html}'
        f'<div class="grid-info">'
        f'<div class="grid-name">{row["given_name"]} {row["family_name"]}</div>'
        f'<div class="grid-team" style="color:{color}">{row["constructor"]}</div>'
        f'<div class="grid-points">{row["points"]:.0f} PTS · {wins_label}</div>'
        f'</div>'
        f'</a>'
    )

# Pair drivers up two-by-two, staggered like a real F1 starting grid.
cards = ['<div class="standings-grid">']
for i in range(0, len(slots), 2):
    pair = slots[i:i + 2]
    if len(pair) == 1:
        pair.append('<div class="driver-card empty"></div>')
    cards.append(f'<div class="grid-row">{"".join(pair)}</div>')
cards.append("</div>")

st.markdown("".join(cards), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div class="source-badge">
📡 <b>Data source</b><br>
Standings: api.jolpi.ca (Jolpica-F1) · Driver photos & team colours: api.openf1.org
</div>
""", unsafe_allow_html=True)
