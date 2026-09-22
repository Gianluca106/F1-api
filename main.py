import streamlit as st

from styles import apply_theme

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="F1 Telemetry Pro",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_theme()

# ─────────────────────────────────────────────
# HEADER (shown above every page)
# ─────────────────────────────────────────────
st.markdown("""
<div class="f1-header">
  <h1>🏎️ F1 TELEMETRY PRO</h1>
  <p>Fastest lap analysis · Live data from OpenF1 API · open source & free</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TOP NAVIGATION
# ─────────────────────────────────────────────
page = st.navigation(
    [
        st.Page("pages/home.py", title="Standings", icon="🏆", default=True),
        st.Page("pages/telemetry.py", title="Telemetry", icon="🏎️"),
    ],
    position="top",
)
page.run()
