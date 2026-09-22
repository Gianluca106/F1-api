"""Shared dark racing theme, applied once from the entry script."""

import streamlit as st


def apply_theme() -> None:
    st.markdown("""
    <style>
        /* Dark racing background */
        .stApp { background-color: #0a0a0f; }
        section[data-testid="stSidebar"] { background-color: #111118; border-right: 1px solid #222; }

        /* Header banner */
        .f1-header {
            background: linear-gradient(135deg, #e8002d 0%, #cc0000 50%, #8b0000 100%);
            padding: 20px 28px;
            border-radius: 12px;
            margin-bottom: 24px;
            font-family: 'Courier New', monospace;
            letter-spacing: 2px;
        }
        .f1-header h1 { color: white; margin: 0; font-size: 2rem; }
        .f1-header p  { color: #ffcccc; margin: 4px 0 0; font-size: 0.85rem; }

        /* Metric card */
        .metric-card {
            background: #16161e;
            border: 1px solid #2a2a35;
            border-radius: 10px;
            padding: 16px 20px;
            text-align: center;
        }
        .metric-card .label { font-size: 0.75rem; color: #666; letter-spacing: 2px; text-transform: uppercase; }
        .metric-card .value { font-size: 1.8rem; font-weight: 700; color: #e8002d; font-family: 'Courier New', monospace; }
        .metric-card .unit  { font-size: 0.8rem; color: #888; }

        /* Data source badge */
        .source-badge {
            background: #16161e;
            border: 1px solid #2a2a35;
            border-left: 3px solid #e8002d;
            border-radius: 6px;
            padding: 10px 14px;
            font-size: 0.78rem;
            color: #888;
            font-family: 'Courier New', monospace;
            margin-bottom: 12px;
        }

        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #e8002d, #cc0000) !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
            letter-spacing: 1px !important;
            width: 100% !important;
        }
        .stButton > button:hover { opacity: 0.85 !important; }

        /* Selectbox */
        .stSelectbox label { color: #888 !important; font-size: 0.8rem !important; }

        /* Section titles */
        h3 { color: #e8002d !important; font-family: 'Courier New', monospace; }
        h2 { color: #ffffff !important; }

        /* Divider */
        hr { border-color: #222 !important; }

        /* Top nav (st.navigation position="top") */
        [data-testid="stTopNav"] {
            background-color: #111118 !important;
            border-bottom: 1px solid #222 !important;
        }

        /* Championship standings — real F1 starting-grid formation: */
        /* small, uniform cards, two per row, staggered like grid slots. */
        .standings-grid {
            display: flex;
            flex-direction: column;
            max-width: 640px;
            margin: 12px auto 0;
        }
        .grid-row {
            display: flex;
            gap: 16px;
            margin-bottom: 16px;
        }
        .driver-card {
            flex: 1;
            min-width: 0;
            height: 68px;
            box-sizing: border-box;
            background: #16161e;
            border: 1px solid #2a2a35;
            border-left: 4px solid #e8002d;
            border-radius: 10px;
            padding: 12px 14px;
            display: flex;
            align-items: center;
            gap: 10px;
            cursor: pointer;
            text-decoration: none !important;
            color: inherit !important;
            transition: transform 0.15s ease, background 0.15s ease;
        }
        .driver-card.pair { margin-top: 34px; }
        .driver-card.empty { visibility: hidden; }
        .driver-card:hover {
            transform: translateY(-3px);
            background: #1c1c26;
        }
        .driver-pos {
            font-family: 'Courier New', monospace;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 1px;
            color: #666;
            background: rgba(255, 255, 255, 0.06);
            border-radius: 4px;
            padding: 2px 4px;
            width: 34px;
            box-sizing: border-box;
            text-align: center;
            flex-shrink: 0;
            align-self: flex-start;
        }
        .driver-photo {
            width: 44px;
            height: 44px;
            border-radius: 50%;
            object-fit: cover;
            background: #0d0d14;
            flex-shrink: 0;
        }
        .driver-photo.placeholder { border: 1px dashed #333; }
        .grid-info { overflow: hidden; }
        .grid-name {
            color: #fff;
            font-weight: 700;
            font-size: 0.88rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .grid-team {
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .grid-points {
            font-family: 'Courier New', monospace;
            font-size: 0.7rem;
            color: #888;
            margin-top: 2px;
        }
    </style>
    """, unsafe_allow_html=True)
