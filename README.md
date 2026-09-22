# F1 Telemetry Pro

Interactive Streamlit dashboard for exploring live Formula 1 data: current drivers' championship standings and lap-by-lap car telemetry (speed, gear, throttle/brake, RPM), built on public F1 data APIs.

## Features

- **Standings** — drivers' championship standings for the current season (falling back to the previous one before round 1), with team colors and driver photos, laid out like a starting grid
- **Telemetry** — pick any race and driver to see their fastest lap broken down into a 4-panel chart: speed, gear, throttle vs brake, RPM
- Deep links from a driver's standings card straight into their telemetry page
- Response caching (TTL-based) and retry-with-backoff to stay resilient to API rate limits

## Data sources

- [Jolpica-F1](https://api.jolpi.ca) (Ergast successor) — championship standings
- [OpenF1](https://openf1.org) — sessions, driver grids, laps, car telemetry

## Tech stack

Python, Streamlit, Pandas, Plotly, Requests

## Getting started

```bash
git clone <repo-url>
cd F1-api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run main.py
```

## Project structure

```
main.py           # entry point: page config, theme, navigation
f1_data.py        # OpenF1 API access (races, grids, laps, telemetry)
f1_standings.py   # Jolpica-F1 API access (championship standings)
styles.py         # shared dark racing theme (CSS)
pages/
  home.py         # standings page
  telemetry.py    # telemetry page
```

## Status

Work in progress — standings and telemetry pages are functional; UI polish and additional features are ongoing.
