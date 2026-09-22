import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from datetime import timedelta

from f1_data import fetch_races, fetch_grid, fetch_laps, fetch_telemetry, relevant_years

# ─────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────

# Gear labels for the Y axis
GEAR_LABELS = {0: "N", 1: "1", 2: "2", 3: "3", 4: "4", 5: "5", 6: "6", 7: "7", 8: "8"}

CHART_EXPLANATIONS = {
    "Lap Time Distribution": "Bar chart of every lap the driver completed in the race. "
        "The red bar marks the lap analyzed below — usually the fastest one.",
    "Speed": "Car speed in km/h across the lap, sampled roughly every 270ms. "
        "Peaks are straights, dips are braking zones and corners.",
    "Gear": "Gear selected by the driver at each point of the lap (N = neutral, 1-8 = gears).",
    "Throttle vs Brake": "Throttle (green) and brake (red) pedal position as a percentage, 0-100%. "
        "They rarely overlap, except briefly during trail-braking.",
    "RPM": "Engine speed in revolutions per minute. Spikes align with gear shifts and full-throttle zones.",
}


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def format_lap_time(seconds: float) -> str:
    """Convert seconds into mm:ss.mmm format."""
    m = int(seconds // 60)
    s = seconds % 60
    return f"{m}:{s:06.3f}"


# ─────────────────────────────────────────────
# CHARTS
# ─────────────────────────────────────────────

def plot_full_telemetry(df: pd.DataFrame, driver_name: str, color: str, lap_number: int) -> go.Figure:
    """
    4-panel stacked dashboard with a shared X axis (seconds from lap start):
      1. Speed (km/h)
      2. Gear
      3. Throttle vs Brake (%)
      4. RPM
    """
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        subplot_titles=(
            "🚀 Speed (km/h)",
            "⚙️ Gear",
            "🎮 Throttle vs Brake (%)",
            "🔧 RPM"
        ),
        row_heights=[0.35, 0.2, 0.25, 0.2]
    )

    x = df["t_sec"]

    # — 1. Speed —
    fig.add_trace(go.Scatter(
        x=x, y=df["speed"],
        mode="lines",
        name="Speed",
        line=dict(color=color, width=2),
        fill="tozeroy",
        fillcolor=f"rgba{tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.12,)}",
        hovertemplate="<b>%{y} km/h</b><br>t=%{x:.2f}s<extra></extra>"
    ), row=1, col=1)

    # — 2. Gear —
    fig.add_trace(go.Scatter(
        x=x, y=df["n_gear"],
        mode="lines",
        name="Gear",
        line=dict(color="#ffcc00", width=2, shape="hv"),
        hovertemplate="<b>Gear %{y}</b><br>t=%{x:.2f}s<extra></extra>"
    ), row=2, col=1)

    # — 3. Throttle & Brake —
    fig.add_trace(go.Scatter(
        x=x, y=df["throttle"],
        mode="lines", name="Throttle",
        line=dict(color="#00ff88", width=1.5),
        fill="tozeroy", fillcolor="rgba(0,255,136,0.08)",
        hovertemplate="Throttle: <b>%{y}%</b><extra></extra>"
    ), row=3, col=1)
    fig.add_trace(go.Scatter(
        x=x, y=df["brake"],
        mode="lines", name="Brake",
        line=dict(color="#e8002d", width=1.5),
        fill="tozeroy", fillcolor="rgba(232,0,45,0.12)",
        hovertemplate="Brake: <b>%{y}%</b><extra></extra>"
    ), row=3, col=1)

    # — 4. RPM —
    fig.add_trace(go.Scatter(
        x=x, y=df["rpm"],
        mode="lines", name="RPM",
        line=dict(color="#aa88ff", width=1.5),
        hovertemplate="RPM: <b>%{y:,}</b><extra></extra>"
    ), row=4, col=1)

    # Global layout
    fig.update_layout(
        height=700,
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#0d0d14",
        font=dict(family="Courier New", color="#999", size=11),
        title=dict(
            text=f"TELEMETRY — {driver_name.upper()} — LAP #{lap_number}",
            font=dict(size=14, color="#e8002d", family="Courier New"),
            x=0.01
        ),
        legend=dict(
            orientation="h", y=1.03, x=0,
            bgcolor="rgba(0,0,0,0)",
            font=dict(size=10, color="#888")
        ),
        hovermode="x unified",
        margin=dict(t=60, b=40, l=60, r=20)
    )

    # Axes
    for row in range(1, 5):
        fig.update_xaxes(
            showgrid=True, gridcolor="#1a1a22",
            zeroline=False, tickfont=dict(size=9),
            row=row, col=1
        )
        fig.update_yaxes(
            showgrid=True, gridcolor="#1a1a22",
            zeroline=False, tickfont=dict(size=9),
            row=row, col=1
        )

    fig.update_xaxes(title_text="Seconds from lap start", row=4, col=1)
    fig.update_yaxes(
        tickvals=list(GEAR_LABELS.keys()),
        ticktext=list(GEAR_LABELS.values()),
        row=2, col=1
    )

    return fig


def plot_lap_distribution(df_laps: pd.DataFrame, best_lap_number: int) -> go.Figure:
    """Bar chart of every lap time, with the best lap highlighted."""
    colors = ["#e8002d" if int(ln) == int(best_lap_number) else "#2a2a35"
              for ln in df_laps["lap_number"]]

    fig = go.Figure(go.Bar(
        x=df_laps["lap_number"],
        y=df_laps["lap_duration"],
        marker_color=colors,
        text=[format_lap_time(t) for t in df_laps["lap_duration"]],
        textposition="outside",
        textfont=dict(size=8, color="#666"),
        hovertemplate="Lap %{x}<br>Time: <b>%{text}</b><extra></extra>"
    ))
    fig.update_layout(
        height=280,
        paper_bgcolor="#0a0a0f",
        plot_bgcolor="#0d0d14",
        font=dict(family="Courier New", color="#888", size=10),
        title=dict(text="⏱ LAP TIME DISTRIBUTION (🔴 = analyzed lap)",
                   font=dict(size=12, color="#888"), x=0.01),
        xaxis=dict(title="Lap #", showgrid=False, tickfont=dict(size=9)),
        yaxis=dict(title="Duration (s)", showgrid=True, gridcolor="#1a1a22"),
        margin=dict(t=50, b=40, l=60, r=20),
        bargap=0.2
    )
    return fig


# ─────────────────────────────────────────────
# PAGE HEADER + CHART GUIDE
# ─────────────────────────────────────────────
st.markdown("### 🏎️ Lap Telemetry")

with st.expander("ℹ️ Chart guide — what am I looking at?"):
    chart_choice = st.selectbox("Pick a chart", list(CHART_EXPLANATIONS.keys()))
    st.markdown(CHART_EXPLANATIONS[chart_choice])


# ─────────────────────────────────────────────
# DEEP LINK — arriving from a driver card on the Standings page
# (e.g. /telemetry?driver=12&session=11369)
# ─────────────────────────────────────────────
qp_driver = st.query_params.get("driver")
qp_session = st.query_params.get("session")

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    st.markdown("---")

    # Races held this year and last year, most recent first
    races_by_year = [df for df in (fetch_races(y) for y in relevant_years()) if not df.empty]
    if not races_by_year:
        st.error("Couldn't load the race calendar from OpenF1. Try again later.")
        st.stop()
    races_df = pd.concat(races_by_year, ignore_index=True).sort_values("date_start", ascending=False).reset_index(drop=True)

    race_index = 0
    if qp_session:
        matches = races_df.index[races_df["session_key"] == int(qp_session)].tolist()
        if matches:
            race_index = matches[0]

    race_label = st.selectbox("🏁 Race", races_df["label"], index=race_index)
    race_row = races_df[races_df["label"] == race_label].iloc[0]
    session_key = int(race_row["session_key"])

    # Full driver grid for the selected race
    grid_df = fetch_grid(session_key)
    if grid_df.empty:
        st.error("Couldn't load the driver grid for this race.")
        st.stop()
    grid_df["option"] = grid_df["display_name"] + " (" + grid_df["driver_number"].astype(str) + ")"

    driver_index = 0
    if qp_driver:
        matches = grid_df.index[grid_df["driver_number"] == int(qp_driver)].tolist()
        if matches:
            driver_index = matches[0]

    driver_option = st.selectbox("👤 Driver", grid_df["option"], index=driver_index)
    driver_row = grid_df[grid_df["option"] == driver_option].iloc[0]
    driver_number = int(driver_row["driver_number"])
    driver_name = driver_row["display_name"]
    driver_color = "#" + str(driver_row["team_colour"])

    st.markdown("---")
    load = st.button("🚀 LOAD TELEMETRY")

    # Auto-load once per distinct deep link, so clicking a driver on the
    # Standings page shows their telemetry immediately.
    if qp_driver:
        deep_link_id = f"{qp_driver}:{qp_session}"
        if st.session_state.get("last_deep_link") != deep_link_id:
            st.session_state["last_deep_link"] = deep_link_id
            load = True

    st.markdown("---")
    # Data source info
    st.markdown("""
    <div class="source-badge">
    📡 <b>Data source</b><br>
    api.openf1.org<br>
    Endpoints: /v1/sessions · /v1/drivers · /v1/laps · /v1/car_data<br>
    Refreshed every ~5-60 min (cached)
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="source-badge">
    ℹ️ Telemetry data is sampled<br>
    at ~3.7 Hz (every ~270ms)<br>
    during the fastest lap
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN LOGIC
# ─────────────────────────────────────────────
if load:

    # — STEP 1: Laps —
    with st.spinner(f"📡 Fetching lap data from OpenF1 (session {session_key})..."):
        try:
            df_laps = fetch_laps(session_key, driver_number)
        except Exception as e:
            st.error(f"❌ Error fetching laps: {e}")
            st.stop()

    if df_laps is None or df_laps.empty:
        st.error("No valid laps found. The driver may not have raced in this session.")
        st.stop()

    # Fastest lap
    best_lap = df_laps.sort_values("lap_duration").iloc[0]
    lap_number    = int(best_lap["lap_number"])
    lap_time      = float(best_lap["lap_duration"])
    start_time_dt = pd.to_datetime(best_lap["date_start"], format="ISO8601")
    end_time_dt   = start_time_dt + timedelta(seconds=lap_time)
    start_str     = start_time_dt.isoformat().replace("+00:00", "Z")
    end_str       = end_time_dt.isoformat().replace("+00:00", "Z")

    # — LAP KPIs —
    st.markdown("### 🏆 Fastest lap found")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card">
            <div class="label">Driver</div>
            <div class="value" style="font-size:1.1rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="{driver_name}">{driver_name}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card">
            <div class="label">Lap #</div>
            <div class="value">{lap_number}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card">
            <div class="label">Time</div>
            <div class="value" style="font-size:1.4rem">{format_lap_time(lap_time)}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card">
            <div class="label">Race</div>
            <div class="value" style="font-size:0.9rem">{race_label}</div>
        </div>""", unsafe_allow_html=True)

    # — LAP DISTRIBUTION CHART —
    st.plotly_chart(plot_lap_distribution(df_laps, lap_number), use_container_width=True)

    # — STEP 2: Telemetry —
    with st.spinner("📡 Fetching lap telemetry..."):
        try:
            df_tel = fetch_telemetry(session_key, driver_number, start_str, end_str)
        except Exception as e:
            st.error(f"❌ Error fetching telemetry: {e}")
            st.stop()

    if df_tel is None or df_tel.empty:
        st.warning("⚠️ Lap found, but no telemetry data is available for this time window.")
        st.info(f"Requested window: {start_str} → {end_str}")
        st.stop()

    # — TELEMETRY KPIs —
    st.markdown("### 📊 Telemetry statistics")
    k1, k2, k3, k4, k5 = st.columns(5)
    kpi_data = [
        ("Max Speed", f"{int(df_tel['speed'].max())}", "km/h"),
        ("Avg Speed", f"{int(df_tel['speed'].mean())}", "km/h"),
        ("Max RPM", f"{int(df_tel['rpm'].max()):,}", "rpm"),
        ("Top Gear", f"{int(df_tel['n_gear'].max())}", ""),
        ("Samples", f"{len(df_tel)}", "points ~270ms"),
    ]
    for col, (label, val, unit) in zip([k1, k2, k3, k4, k5], kpi_data):
        with col:
            st.markdown(f"""<div class="metric-card">
                <div class="label">{label}</div>
                <div class="value">{val}</div>
                <div class="unit">{unit}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # — MAIN TELEMETRY CHART —
    st.plotly_chart(
        plot_full_telemetry(df_tel, driver_name, driver_color, lap_number),
        use_container_width=True
    )

    # — TECHNICAL NOTES + RAW DATA —
    with st.expander("🔍 Technical details & raw data"):
        st.markdown(f"""
        **Data source:** [api.openf1.org](https://api.openf1.org)
        **Laps endpoint:** `GET /v1/laps?session_key={session_key}&driver_number={driver_number}`
        **Telemetry endpoint:** `GET /v1/car_data?session_key={session_key}&driver_number={driver_number}&date>={start_str}&date<={end_str}`
        **Lap time window:** `{start_str}` → `{end_str}`
        **Lap duration:** `{lap_time:.3f}s` = `{format_lap_time(lap_time)}`
        **Sampling rate:** ~3.7 Hz (one sample every ~270ms)
        **Telemetry points downloaded:** `{len(df_tel)}`
        """)
        st.markdown("**Raw data (first 20 samples):**")
        st.dataframe(
            df_tel[["t_sec", "speed", "n_gear", "throttle", "brake", "rpm"]].head(20),
            use_container_width=True,
            hide_index=True
        )

else:
    # Initial state
    st.markdown("""
    <div style="
        background:#13131a;
        border:1px solid #2a2a35;
        border-radius:12px;
        padding:48px;
        text-align:center;
        margin-top:32px;
    ">
        <div style="font-size:3rem">🏁</div>
        <h2 style="color:#e8002d !important; font-family:'Courier New';margin:16px 0 8px">READY TO GO</h2>
        <p style="color:#666; font-size:0.9rem">
            Select a race and driver in the left panel,<br>
            then press <b style="color:#e8002d">LOAD TELEMETRY</b> to analyze the fastest lap.
        </p>
        <br>
        <p style="color:#444; font-size:0.78rem; font-family:'Courier New'">
            Data provided by api.openf1.org · Open Source · Free
        </p>
    </div>
    """, unsafe_allow_html=True)
