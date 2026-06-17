"""
🚆 ระบบแจ้งเตือนสภาพอากาศโครงข่ายรถไฟไทย v3.0
Thai Railway Network — Weather · Water · Disaster Alert System
การรถไฟแห่งประเทศไทย × กรมอุตุนิยมวิทยา × สำนักทรัพยากรน้ำ × คลังข้อมูลน้ำแห่งชาติ
"""

import streamlit as st
import requests
import json
import math
import base64
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz

# ══════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="SRT Weather & Water Alert · ระบบแจ้งเตือนรถไฟ",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "[data.tmd.go.th](https://data.tmd.go.th/api/index1.php)",
        "About": "ระบบแจ้งเตือนสภาพอากาศและน้ำท่วมโครงข่ายรถไฟไทย v3.0",
    },
)

TZ_TH = pytz.timezone("Asia/Bangkok")

# ══════════════════════════════════════════════════════════════
#  THEME & CSS — ENHANCED
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('[fonts.googleapis.com](https://fonts.googleapis.com/css2?family=Sarabun:ital,wght@0,300;0,400;0,600;0,700;0,800;1,400&family=Inter:wght@400;600;700;800&display=swap)');

html, body, [class*="css"], * {
    font-family: 'Sarabun', 'Inter', 'Segoe UI', sans-serif !important;
}

/* ── Animated background ── */
.stApp {
    background: #060d18;
    background-image:
        radial-gradient(ellipse at 20% 20%, rgba(0,80,160,0.08) 0%, transparent 60%),
        radial-gradient(ellipse at 80% 80%, rgba(0,40,100,0.12) 0%, transparent 60%),
        repeating-linear-gradient(90deg, transparent, transparent 79px,
            rgba(255,255,255,0.012) 79px, rgba(255,255,255,0.012) 80px),
        repeating-linear-gradient(0deg, transparent, transparent 79px,
            rgba(255,255,255,0.006) 79px, rgba(255,255,255,0.006) 80px);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #040a13 0%, #07111e 50%, #040a13 100%) !important;
    border-right: 1px solid rgba(91,200,255,0.12) !important;
}
[data-testid="stSidebar"] * { color: #8ab8d4 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #5bc8ff !important; }

/* Rail track decoration */
[data-testid="stSidebar"]::after {
    content: '';
    position: fixed; bottom: 0; left: 0; width: 280px; height: 6px;
    background: repeating-linear-gradient(90deg,
        #c8a84b 0, #c8a84b 18px, transparent 18px, transparent 26px);
    opacity: 0.5;
}

/* ── Animated header ── */
.rail-header {
    background: linear-gradient(135deg,
        #061628 0%, #0a2448 35%, #061a38 65%, #04111f 100%);
    border: 1px solid rgba(91,200,255,0.18);
    border-left: 5px solid #c8a84b;
    border-radius: 0 16px 16px 0;
    padding: 22px 32px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.rail-header::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg,
        #c8a84b 0%, #e8c86b 30%, #c8a84b 60%, transparent 100%);
}
.rail-header::after {
    content: '';
    position: absolute; bottom: 0; left: 0; right: 0; height: 2px;
    background: repeating-linear-gradient(90deg,
        #c8a84b 0, #c8a84b 20px, transparent 20px, transparent 28px);
}
.rail-header .glow-orb {
    position: absolute; right: -40px; top: -40px;
    width: 200px; height: 200px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(91,200,255,0.06) 0%, transparent 70%);
}
.rail-header h1 {
    color: #fff !important;
    font-size: 1.75rem !important;
    font-weight: 800 !important;
    margin: 0 0 6px 0 !important;
    letter-spacing: -0.3px;
    text-shadow: 0 0 40px rgba(91,200,255,0.3);
}
.rail-header .sub-badges {
    display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px;
}
.rail-header .mini-badge {
    background: rgba(91,200,255,0.08);
    border: 1px solid rgba(91,200,255,0.2);
    border-radius: 20px;
    padding: 2px 10px;
    color: #7ec8e3 !important;
    font-size: 0.75rem;
    font-weight: 600;
}
.rail-header .mini-badge.gold {
    background: rgba(200,168,75,0.1);
    border-color: rgba(200,168,75,0.3);
    color: #e8c86b !important;
}

/* ── Source status pills ── */
.source-bar {
    display: flex; gap: 8px; flex-wrap: wrap;
    background: rgba(4,10,19,0.8);
    border: 1px solid rgba(91,200,255,0.08);
    border-radius: 10px;
    padding: 10px 16px;
    margin-bottom: 16px;
    align-items: center;
}
.source-pill {
    display: flex; align-items: center; gap: 6px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(91,200,255,0.1);
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.76rem;
}
.source-pill.ok   { border-color: rgba(16,185,129,0.3); }
.source-pill.warn { border-color: rgba(245,158,11,0.3); }
.source-pill.err  { border-color: rgba(239,68,68,0.3);  }
.source-dot { width: 7px; height: 7px; border-radius: 50%; }
.source-dot.ok   { background: #10b981; box-shadow: 0 0 6px #10b981; }
.source-dot.warn { background: #f59e0b; box-shadow: 0 0 6px #f59e0b; }
.source-dot.err  { background: #ef4444; box-shadow: 0 0 6px #ef4444; }

/* ── KPI Cards ── */
.kpi-grid { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 14px; }
.kpi-card {
    flex: 1; min-width: 130px;
    background: linear-gradient(160deg,
        rgba(10,28,50,0.98) 0%, rgba(6,16,32,0.98) 100%);
    border: 1px solid rgba(91,200,255,0.1);
    border-top: 3px solid var(--accent, #5bc8ff);
    border-radius: 12px;
    padding: 16px 18px;
    position: relative;
    overflow: hidden;
    transition: transform 0.15s, box-shadow 0.15s;
}
.kpi-card::after {
    content: '';
    position: absolute; top: -30px; right: -30px;
    width: 80px; height: 80px; border-radius: 50%;
    background: radial-gradient(circle, rgba(var(--accent-rgb,91,200,255),0.08) 0%, transparent 70%);
}
.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.4), 0 0 0 1px rgba(91,200,255,0.15);
}
.kpi-card .kpi-icon { font-size: 1.4rem; margin-bottom: 8px; display: block; }
.kpi-card .kpi-label {
    color: #4a7090; font-size: 0.69rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;
}
.kpi-card .kpi-value { color: #fff; font-size: 1.9rem; font-weight: 800; line-height: 1; }
.kpi-card .kpi-sub   { color: #5a8099; font-size: 0.72rem; margin-top: 5px; }
.kpi-red    { --accent: #ef4444; }
.kpi-orange { --accent: #f59e0b; }
.kpi-blue   { --accent: #3b82f6; }
.kpi-green  { --accent: #10b981; }
.kpi-gold   { --accent: #c8a84b; }
.kpi-purple { --accent: #a78bfa; }
.kpi-teal   { --accent: #06b6d4; }
.kpi-water  { --accent: #0ea5e9; }

/* ── Water level card ── */
.water-card {
    background: linear-gradient(135deg,
        rgba(6,182,212,0.08) 0%, rgba(14,165,233,0.05) 100%);
    border: 1px solid rgba(6,182,212,0.2);
    border-radius: 12px;
    padding: 14px 18px;
    margin: 5px 0;
    position: relative;
    overflow: hidden;
}
.water-card::before {
    content: '';
    position: absolute; bottom: 0; left: 0; right: 0;
    height: var(--fill, 30%);
    background: linear-gradient(180deg, transparent, rgba(6,182,212,0.06));
    transition: height 0.5s;
}
.water-title { color: #67e8f9; font-weight: 700; font-size: 0.88rem; margin-bottom: 6px; }
.water-level { color: #fff; font-size: 1.4rem; font-weight: 800; }
.water-status { font-size: 0.75rem; margin-top: 3px; }

/* ── Alert cards ── */
.alert-card {
    border-radius: 10px; padding: 13px 16px; margin: 5px 0;
    position: relative; overflow: hidden;
}
.alert-critical {
    background: linear-gradient(135deg, rgba(127,29,29,0.15), rgba(239,68,68,0.05));
    border: 1px solid rgba(239,68,68,0.3); border-left: 4px solid #ef4444;
}
.alert-warning {
    background: linear-gradient(135deg, rgba(120,53,15,0.15), rgba(245,158,11,0.05));
    border: 1px solid rgba(245,158,11,0.3); border-left: 4px solid #f59e0b;
}
.alert-info {
    background: linear-gradient(135deg, rgba(30,58,95,0.15), rgba(59,130,246,0.05));
    border: 1px solid rgba(59,130,246,0.25); border-left: 4px solid #3b82f6;
}
.alert-ok {
    background: linear-gradient(135deg, rgba(6,78,59,0.12), rgba(16,185,129,0.04));
    border: 1px solid rgba(16,185,129,0.2); border-left: 4px solid #10b981;
}
.alert-water {
    background: linear-gradient(135deg, rgba(6,182,212,0.10), rgba(14,165,233,0.04));
    border: 1px solid rgba(6,182,212,0.25); border-left: 4px solid #06b6d4;
}
.alert-card-title { color: #f0f8ff; font-weight: 700; font-size: 0.92rem; margin: 0 0 5px 0; }
.alert-card-body  { color: #8ab8d4; font-size: 0.82rem; margin: 0; line-height: 1.55; }
.alert-card-meta  { color: #3a6070; font-size: 0.73rem; margin-top: 6px; }

/* ── Section title ── */
.sec-title {
    color: #5bc8ff; font-size: 0.95rem; font-weight: 700;
    border-bottom: 1px solid rgba(91,200,255,0.15);
    padding-bottom: 8px; margin: 20px 0 12px 0;
    display: flex; align-items: center; gap: 8px;
}
.sec-title-water {
    color: #06b6d4; font-size: 0.95rem; font-weight: 700;
    border-bottom: 1px solid rgba(6,182,212,0.2);
    padding-bottom: 8px; margin: 20px 0 12px 0;
    display: flex; align-items: center; gap: 8px;
}

/* ── Risk badge ── */
.badge {
    display: inline-block; padding: 2px 10px;
    border-radius: 12px; font-size: 0.71rem; font-weight: 700;
}
.badge-critical { background: rgba(127,29,29,0.6); color: #fca5a5; border: 1px solid #ef4444; }
.badge-high     { background: rgba(120,53,15,0.6); color: #fde68a; border: 1px solid #f59e0b; }
.badge-medium   { background: rgba(30,58,95,0.6);  color: #93c5fd; border: 1px solid #3b82f6; }
.badge-low      { background: rgba(6,78,59,0.6);   color: #6ee7b7; border: 1px solid #10b981; }
.badge-na       { background: rgba(20,30,45,0.6);  color: #4a6070; border: 1px solid #1e3a50; }
.badge-water-critical { background: rgba(8,51,68,0.6); color: #67e8f9; border: 1px solid #06b6d4; }
.badge-flood    { background: rgba(30,58,138,0.6); color: #bfdbfe; border: 1px solid #3b82f6; }

/* ── Station row ── */
.stn-row {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1.2fr;
    align-items: center; gap: 6px;
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(91,200,255,0.06);
    border-radius: 8px; padding: 8px 12px; margin: 3px 0;
    transition: background 0.15s, border-color 0.15s;
}
.stn-row:hover {
    background: rgba(91,200,255,0.05);
    border-color: rgba(91,200,255,0.15);
}
.stn-name { color: #c8e4f8; font-weight: 600; font-size: 0.86rem; }
.stn-prov { color: #3a6070; font-size: 0.74rem; }
.stn-val  { color: #d0ecff; font-size: 0.85rem; text-align: right; }

/* ── Progress bar ── */
.prog-wrap {
    background: rgba(255,255,255,0.05);
    border-radius: 6px; height: 6px; overflow: hidden; margin-top: 3px;
}
.prog-fill {
    height: 100%; border-radius: 6px;
    transition: width 0.5s cubic-bezier(0.4,0,0.2,1);
}

/* ── Gauge ── */
.gauge-wrap {
    width: 100%; height: 8px;
    background: linear-gradient(90deg,
        #10b981 0%, #10b981 30%,
        #3b82f6 30%, #3b82f6 60%,
        #f59e0b 60%, #f59e0b 80%,
        #ef4444 80%);
    border-radius: 4px;
    position: relative;
    margin: 6px 0;
}
.gauge-marker {
    position: absolute; top: -3px;
    width: 3px; height: 14px;
    background: #fff; border-radius: 2px;
    box-shadow: 0 0 6px rgba(255,255,255,0.8);
    transform: translateX(-50%);
}

/* ── Metric ── */
div[data-testid="stMetric"] {
    background: rgba(8,20,38,0.85) !important;
    border: 1px solid rgba(91,200,255,0.12) !important;
    border-radius: 10px !important;
    padding: 14px 16px !important;
    transition: border-color 0.2s !important;
}
div[data-testid="stMetric"]:hover {
    border-color: rgba(91,200,255,0.25) !important;
}
div[data-testid="stMetric"] label { color: #4a7090 !important; font-size: 0.75rem !important; font-weight: 700 !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #fff !important; font-weight: 800 !important; }
div[data-testid="stMetric"] [data-testid="stMetricDelta"] { font-size: 0.75rem !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(6,14,26,0.8) !important;
    border-radius: 12px !important;
    gap: 3px !important;
    padding: 4px !important;
    border: 1px solid rgba(91,200,255,0.08) !important;
}
.stTabs [data-baseweb="tab"] {
    color: #4a6070 !important;
    border-radius: 9px !important;
    padding: 7px 16px !important;
    font-weight: 600 !important;
    font-size: 0.83rem !important;
    transition: all 0.2s !important;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg,
        rgba(91,200,255,0.15), rgba(59,130,246,0.1)) !important;
    color: #5bc8ff !important;
    box-shadow: inset 0 1px 0 rgba(91,200,255,0.2) !important;
}

/* ── Expander ── */
div[data-testid="stExpander"] {
    background: rgba(6,14,26,0.6) !important;
    border: 1px solid rgba(91,200,255,0.1) !important;
    border-radius: 12px !important;
    transition: border-color 0.2s !important;
}
div[data-testid="stExpander"]:hover { border-color: rgba(91,200,255,0.2) !important; }
div[data-testid="stExpander"] summary { color: #7ec8e3 !important; font-weight: 600 !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #082040, #0a3060) !important;
    color: #c0dff8 !important;
    border: 1px solid rgba(91,200,255,0.25) !important;
    border-radius: 9px !important; font-weight: 600 !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #0a3060, #0e4a90) !important;
    box-shadow: 0 0 18px rgba(91,200,255,0.2), inset 0 1px 0 rgba(91,200,255,0.2) !important;
    border-color: rgba(91,200,255,0.4) !important;
}

/* ── Select/Input ── */
div[data-baseweb="select"] > div {
    background: rgba(6,14,26,0.9) !important;
    border-color: rgba(91,200,255,0.18) !important;
    border-radius: 8px !important;
}
div[data-baseweb="select"] * { color: #8ab8d4 !important; }

/* ── Dataframe ── */
.stDataFrame { border-radius: 10px !important; overflow: hidden !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: #040a13; }
::-webkit-scrollbar-thumb { background: #1a3050; border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: #2a4a70; }

/* ── Status dot ── */
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 5px; }
.dot-green  { background: #10b981; box-shadow: 0 0 8px #10b981; }
.dot-red    { background: #ef4444; box-shadow: 0 0 8px #ef4444; }
.dot-yellow { background: #f59e0b; box-shadow: 0 0 8px #f59e0b; }
.dot-cyan   { background: #06b6d4; box-shadow: 0 0 8px #06b6d4; }
.dot-grey   { background: #2a3a4a; }

/* ── Dashboard box ── */
.dash-box {
    background: linear-gradient(160deg,
        rgba(8,20,40,0.95) 0%, rgba(4,12,26,0.98) 100%);
    border: 1px solid rgba(91,200,255,0.1);
    border-radius: 14px;
    padding: 18px 20px;
    height: 100%;
    position: relative;
    overflow: hidden;
}
.dash-box::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(91,200,255,0.15), transparent);
}
.dash-box h4 {
    color: #5bc8ff; font-size: 0.78rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1px;
    margin: 0 0 14px 0; padding-bottom: 8px;
    border-bottom: 1px solid rgba(91,200,255,0.1);
}
.dash-box.water h4 { color: #06b6d4; border-bottom-color: rgba(6,182,212,0.15); }

/* ── River gauge ── */
.river-row {
    display: flex; align-items: center; gap: 10px;
    padding: 7px 0; border-bottom: 1px solid rgba(255,255,255,0.04);
}
.river-row:last-child { border-bottom: none; }
.river-name { color: #a8cce0; font-size: 0.78rem; font-weight: 600; flex: 1.5; }
.river-loc  { color: #3a6070; font-size: 0.7rem; flex: 1; }
.river-val  { color: #67e8f9; font-size: 0.85rem; font-weight: 700; text-align:right; min-width:50px; }
.river-bar  { flex: 1.5; }

/* ── Flood risk indicator ── */
.flood-risk {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 3px 10px; border-radius: 20px; font-size: 0.72rem; font-weight: 700;
}
.flood-risk.normal   { background: rgba(16,185,129,0.12); color: #34d399; border: 1px solid rgba(16,185,129,0.25); }
.flood-risk.watch    { background: rgba(59,130,246,0.12); color: #60a5fa; border: 1px solid rgba(59,130,246,0.25); }
.flood-risk.warning  { background: rgba(245,158,11,0.12); color: #fbbf24; border: 1px solid rgba(245,158,11,0.25); }
.flood-risk.critical { background: rgba(239,68,68,0.12); color: #f87171; border: 1px solid rgba(239,68,68,0.25); }

/* ── Sparkline container ── */
.spark-wrap {
    height: 40px; display:flex; align-items:flex-end; gap:2px;
}
.spark-bar {
    flex: 1; border-radius: 2px 2px 0 0;
    min-width: 4px; transition: height 0.3s;
}

/* ── Timeline ── */
.timeline-item {
    display: flex; gap: 12px; padding: 8px 0;
    border-bottom: 1px solid rgba(91,200,255,0.05);
}
.timeline-dot {
    width: 10px; height: 10px; border-radius: 50%; margin-top: 3px;
    flex-shrink: 0; box-shadow: 0 0 6px currentColor;
}
.timeline-content { flex: 1; }
.timeline-time  { color: #3a6070; font-size: 0.7rem; }
.timeline-title { color: #c0dff8; font-size: 0.82rem; font-weight: 600; margin: 1px 0; }
.timeline-body  { color: #5a8099; font-size: 0.76rem; }

/* ── Info chip ── */
.chip {
    display: inline-block;
    background: rgba(91,200,255,0.08);
    border: 1px solid rgba(91,200,255,0.15);
    border-radius: 20px; padding: 2px 9px;
    font-size: 0.72rem; color: #7ec8e3; margin: 2px;
}
.chip.water {
    background: rgba(6,182,212,0.08);
    border-color: rgba(6,182,212,0.2); color: #67e8f9;
}

/* ── Stagger animation ── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
.anim { animation: fadeUp 0.35s ease forwards; }

/* Input fields */
input[type="text"], input[type="password"] {
    background: rgba(6,14,26,0.9) !important;
    border: 1px solid rgba(91,200,255,0.18) !important;
    border-radius: 8px !important;
    color: #a8cce0 !important;
}
input:focus { border-color: rgba(91,200,255,0.4) !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  TOKEN SETUP  (TMD)
# ══════════════════════════════════════════════════════════════
def _decode_jwt_payload(token: str) -> dict:
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload))
    except Exception:
        return {}

def _set_token(raw: str) -> None:
    d = _decode_jwt_payload(raw)
    st.session_state["_tmd_token"]    = raw
    st.session_state["_tmd_uid"]      = str(d.get("sub", ""))
    st.session_state["_tmd_jwt_data"] = d

if "_tmd_token" not in st.session_state:
    _boot = ""
    try:
        _secrets = dict(st.secrets)
        _boot = (_secrets.get("TMD_TOKEN") or _secrets.get("tmd_token") or "")
    except Exception:
        pass
    if not _boot:
        import os
        _boot = os.environ.get("TMD_TOKEN", "")
    _set_token(_boot)

def _uid()  -> str:  return st.session_state.get("_tmd_uid", "")
def _ukey() -> str:  return st.session_state.get("_tmd_token", "")
def _jwt()  -> dict: return st.session_state.get("_tmd_jwt_data", {})


# ══════════════════════════════════════════════════════════════
#  SRT RAILWAY NETWORK DATA
# ══════════════════════════════════════════════════════════════
SRT_LINES = {
    "สายเหนือ": {
        "color": "#ef4444", "short": "N", "icon": "🔴",
        "desc": "กรุงเทพ → เชียงใหม่ | 751 กม.",
        "region": "ภาคเหนือ",
        "stations": [
            {"name":"กรุงเทพ (หัวลำโพง)","lat":13.7401,"lon":100.5178,"province":"กรุงเทพมหานคร","km":0},
            {"name":"ดอนเมือง",           "lat":13.9186,"lon":100.5970,"province":"กรุงเทพมหานคร","km":22},
            {"name":"รังสิต",             "lat":14.0262,"lon":100.6162,"province":"ปทุมธานี","km":43},
            {"name":"อยุธยา",             "lat":14.3554,"lon":100.5679,"province":"พระนครศรีอยุธยา","km":71},
            {"name":"ลพบุรี",             "lat":14.7987,"lon":100.6141,"province":"ลพบุรี","km":133},
            {"name":"สระบุรี (ชุมทาง)",   "lat":14.5291,"lon":100.9101,"province":"สระบุรี","km":107},
            {"name":"นครสวรรค์",          "lat":15.7028,"lon":100.1363,"province":"นครสวรรค์","km":338},
            {"name":"พิจิตร",             "lat":16.4365,"lon":100.3485,"province":"พิจิตร","km":399},
            {"name":"พิษณุโลก",           "lat":16.8204,"lon":100.2714,"province":"พิษณุโลก","km":445},
            {"name":"อุตรดิตถ์",          "lat":17.6236,"lon":100.0987,"province":"อุตรดิตถ์","km":485},
            {"name":"เด่นชัย",            "lat":17.9827,"lon":100.0569,"province":"แพร่","km":535},
            {"name":"ลำปาง",              "lat":18.2896,"lon":99.4905,"province":"ลำปาง","km":642},
            {"name":"ลำพูน",              "lat":18.5746,"lon":99.0094,"province":"ลำพูน","km":703},
            {"name":"เชียงใหม่",          "lat":18.7883,"lon":98.9933,"province":"เชียงใหม่","km":751},
        ]
    },
    "สายตะวันออกเฉียงเหนือ": {
        "color": "#f59e0b", "short": "NE", "icon": "🟡",
        "desc": "กรุงเทพ → หนองคาย | 624 กม.",
        "region": "ภาคตะวันออกเฉียงเหนือ",
        "stations": [
            {"name":"กรุงเทพ (หัวลำโพง)","lat":13.7401,"lon":100.5178,"province":"กรุงเทพมหานคร","km":0},
            {"name":"สระบุรี (ชุมทาง)",   "lat":14.5291,"lon":100.9101,"province":"สระบุรี","km":107},
            {"name":"ปากช่อง",            "lat":14.7043,"lon":101.4180,"province":"นครราชสีมา","km":180},
            {"name":"นครราชสีมา",         "lat":14.9734,"lon":102.1112,"province":"นครราชสีมา","km":264},
            {"name":"บัวใหญ่",            "lat":15.5887,"lon":102.4242,"province":"นครราชสีมา","km":361},
            {"name":"ขอนแก่น",            "lat":16.4419,"lon":102.8330,"province":"ขอนแก่น","km":449},
            {"name":"อุดรธานี",           "lat":17.4043,"lon":102.7877,"province":"อุดรธานี","km":569},
            {"name":"หนองคาย",            "lat":17.8818,"lon":102.7433,"province":"หนองคาย","km":624},
        ]
    },
    "สายอีสานใต้": {
        "color": "#a78bfa", "short": "IS", "icon": "🟣",
        "desc": "ถนนจิระ → อุบลราชธานี | 305 กม.",
        "region": "ภาคตะวันออกเฉียงเหนือ",
        "stations": [
            {"name":"นครราชสีมา (ถนนจิระ)","lat":14.9734,"lon":102.1112,"province":"นครราชสีมา","km":0},
            {"name":"บุรีรัมย์",           "lat":14.9950,"lon":103.1030,"province":"บุรีรัมย์","km":101},
            {"name":"สุรินทร์",            "lat":14.8835,"lon":103.4935,"province":"สุรินทร์","km":142},
            {"name":"ศีขรภูมิ",            "lat":15.1000,"lon":103.9500,"province":"สุรินทร์","km":195},
            {"name":"ศรีสะเกษ",            "lat":15.1174,"lon":104.3221,"province":"ศรีสะเกษ","km":237},
            {"name":"อุบลราชธานี",         "lat":15.2241,"lon":104.8579,"province":"อุบลราชธานี","km":305},
        ]
    },
    "สายใต้": {
        "color": "#34d399", "short": "S", "icon": "🟢",
        "desc": "กรุงเทพ → สุไหงโก-ลก | 1,144 กม.",
        "region": "ภาคใต้",
        "stations": [
            {"name":"กรุงเทพ (หัวลำโพง)","lat":13.7401,"lon":100.5178,"province":"กรุงเทพมหานคร","km":0},
            {"name":"นครปฐม",             "lat":13.8199,"lon":100.0597,"province":"นครปฐม","km":56},
            {"name":"ราชบุรี",            "lat":13.5361,"lon":99.8163,"province":"ราชบุรี","km":117},
            {"name":"เพชรบุรี",           "lat":13.1093,"lon":99.9494,"province":"เพชรบุรี","km":167},
            {"name":"หัวหิน",             "lat":12.5675,"lon":99.9576,"province":"ประจวบคีรีขันธ์","km":229},
            {"name":"ประจวบคีรีขันธ์",    "lat":11.8121,"lon":99.7962,"province":"ประจวบคีรีขันธ์","km":318},
            {"name":"ชุมพร",              "lat":10.4930,"lon":99.1800,"province":"ชุมพร","km":485},
            {"name":"สุราษฎร์ธานี",       "lat":9.1400,"lon":99.3300,"province":"สุราษฎร์ธานี","km":651},
            {"name":"นครศรีธรรมราช",      "lat":8.4330,"lon":99.9630,"province":"นครศรีธรรมราช","km":832},
            {"name":"หาดใหญ่",            "lat":7.0080,"lon":100.4740,"province":"สงขลา","km":945},
            {"name":"ปาดังเบซาร์",        "lat":6.6735,"lon":100.3781,"province":"สงขลา","km":991},
            {"name":"สุไหงโก-ลก",         "lat":6.0277,"lon":101.9784,"province":"นราธิวาส","km":1144},
        ]
    },
    "สายตะวันออก": {
        "color": "#60a5fa", "short": "E", "icon": "🔵",
        "desc": "กรุงเทพ → อรัญประเทศ | 255 กม.",
        "region": "ภาคตะวันออก",
        "stations": [
            {"name":"กรุงเทพ (มักกะสัน)", "lat":13.7524,"lon":100.5684,"province":"กรุงเทพมหานคร","km":0},
            {"name":"ฉะเชิงเทรา",         "lat":13.6903,"lon":101.0768,"province":"ฉะเชิงเทรา","km":61},
            {"name":"ชลบุรี",             "lat":13.3639,"lon":100.9905,"province":"ชลบุรี","km":120},
            {"name":"พัทยา",              "lat":12.9236,"lon":100.8825,"province":"ชลบุรี","km":154},
            {"name":"มาบตาพุด",           "lat":12.6793,"lon":101.1500,"province":"ระยอง","km":179},
            {"name":"อรัญประเทศ",         "lat":13.6942,"lon":102.5062,"province":"สระแก้ว","km":255},
        ]
    },
}

# Flatten unique stations
_seen: set = set()
ALL_STATIONS: list = []
for _line, _ldata in SRT_LINES.items():
    for _s in _ldata["stations"]:
        _key = _s["name"]
        if _key not in _seen:
            _seen.add(_key)
            ALL_STATIONS.append({**_s, "line": _line,
                                  "line_color": _ldata["color"],
                                  "line_short": _ldata["short"],
                                  "line_icon":  _ldata["icon"],
                                  "region":     _ldata["region"]})

# ── River stations near railway lines ──────────────────────
# สถานีวัดน้ำใกล้แนวรถไฟ (ใช้สำหรับ Water Resources API)
RIVER_STATIONS_NEAR_RAIL = [
    {"id":"P.1",  "name":"แม่น้ำปิง ที่ เชียงใหม่",    "river":"ปิง",    "lat":18.7883,"lon":98.9933,"line":"สายเหนือ"},
    {"id":"P.67", "name":"แม่น้ำปิง ที่ ลำพูน",         "river":"ปิง",    "lat":18.5746,"lon":99.0094,"line":"สายเหนือ"},
    {"id":"W.4A", "name":"แม่น้ำวัง ที่ ลำปาง",         "river":"วัง",    "lat":18.2896,"lon":99.4905,"line":"สายเหนือ"},
    {"id":"N.1",  "name":"แม่น้ำน่าน ที่ อุตรดิตถ์",    "river":"น่าน",   "lat":17.6236,"lon":100.0987,"line":"สายเหนือ"},
    {"id":"N.67", "name":"แม่น้ำน่าน ที่ พิษณุโลก",     "river":"น่าน",   "lat":16.8204,"lon":100.2714,"line":"สายเหนือ"},
    {"id":"C.2",  "name":"แม่น้ำเจ้าพระยา ที่ นครสวรรค์","river":"เจ้าพระยา","lat":15.7028,"lon":100.1363,"line":"สายเหนือ"},
    {"id":"C.35", "name":"แม่น้ำเจ้าพระยา ที่ อยุธยา",  "river":"เจ้าพระยา","lat":14.3554,"lon":100.5679,"line":"สายเหนือ"},
    {"id":"M.7",  "name":"แม่น้ำมูล ที่ นครราชสีมา",    "river":"มูล",    "lat":14.9734,"lon":102.1112,"line":"สายตะวันออกเฉียงเหนือ"},
    {"id":"M.11", "name":"แม่น้ำมูล ที่ อุบลราชธานี",   "river":"มูล",    "lat":15.2241,"lon":104.8579,"line":"สายอีสานใต้"},
    {"id":"K.1",  "name":"แม่น้ำชี ที่ ขอนแก่น",        "river":"ชี",     "lat":16.4419,"lon":102.8330,"line":"สายตะวันออกเฉียงเหนือ"},
    {"id":"T.1",  "name":"แม่น้ำท่าจีน ที่ นครปฐม",     "river":"ท่าจีน", "lat":13.8199,"lon":100.0597,"line":"สายใต้"},
    {"id":"G.1",  "name":"แม่น้ำแม่กลอง ที่ ราชบุรี",   "river":"แม่กลอง","lat":13.5361,"lon":99.8163,"line":"สายใต้"},
    {"id":"B.5",  "name":"แม่น้ำบางปะกง ที่ ฉะเชิงเทรา","river":"บางปะกง","lat":13.6903,"lon":101.0768,"line":"สายตะวันออก"},
]


# ══════════════════════════════════════════════════════════════
#  API HELPERS — MULTI-SOURCE
# ══════════════════════════════════════════════════════════════

# ── 1. TMD (กรมอุตุนิยมวิทยา) ────────────────────────────
_TMD_BASES = [
    "[data.tmd.go.th](https://data.tmd.go.th/api)",
    "[data.tmd.go.th](http://data.tmd.go.th/api)",
]

def _tmd_fetch(endpoint: str, uid: str, ukey: str, extra: dict | None = None) -> dict | None:
    if not uid or not ukey:
        st.session_state["_tmd_last_error"] = "Token ไม่ถูกต้อง"
        return None
    params = {"uid": uid, "ukey": ukey, "format": "json"}
    if extra:
        params.update(extra)
    errors = []
    for base in _TMD_BASES:
        url = f"{base}/{endpoint}"
        for attempt in range(2):
            try:
                r = requests.get(url, params=params, timeout=12,
                                 allow_redirects=True,
                                 headers={"Accept": "application/json"})
                if r.status_code == 200:
                    try:
                        data = r.json()
                    except Exception:
                        errors.append(f"{base}: ไม่ใช่ JSON")
                        break
                    if isinstance(data, dict):
                        api_err = (data.get("error") or data.get("Error") or
                                   data.get("STATUS") or data.get("status") or "")
                        if api_err and str(api_err).lower() not in ("0","ok","success","none","","null"):
                            errors.append(f"{base}: API error={api_err}")
                            break
                    st.session_state["_tmd_last_error"] = ""
                    return data
                elif r.status_code in (401, 403):
                    errors.append(f"HTTP {r.status_code} — Token ไม่ถูกต้อง")
                    break
                else:
                    errors.append(f"HTTP {r.status_code}")
            except requests.exceptions.Timeout:
                errors.append(f"Timeout (attempt {attempt+1})")
                if attempt < 1: time.sleep(0.5)
            except requests.exceptions.ConnectionError as ce:
                errors.append(f"ConnectionError: {str(ce)[:60]}")
                break
            except Exception as e:
                errors.append(f"{type(e).__name__}: {str(e)[:60]}")
                break
    st.session_state["_tmd_last_error"] = " | ".join(errors)
    return None


# ── 2. Water Resources (สทนช. / กรมทรัพยากรน้ำ) ──────────
# คลังข้อมูลน้ำแห่งชาติ: [app.thaiwater.net](https://app.thaiwater.net/api)
_THAIWATER_BASE = "[app.thaiwater.net](https://app.thaiwater.net/api/v1/thaiwater)"
_WRM_BASE       = "[api-v3.thaiwater.net](https://api-v3.thaiwater.net/api/v1)"  # Water Resource Management

def _thaiwater_fetch(endpoint: str, params: dict | None = None) -> dict | None:
    """คลังข้อมูลน้ำแห่งชาติ — ไม่ต้องการ API key สำหรับบางจุด"""
    url = f"{_THAIWATER_BASE}/{endpoint}"
    try:
        r = requests.get(url, params=params or {}, timeout=15,
                         headers={"Accept": "application/json",
                                  "User-Agent": "SRT-Weather-Alert/3.0"})
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        st.session_state["_water_last_error"] = str(e)[:80]
    return None

def _wrm_fetch(endpoint: str, params: dict | None = None) -> dict | None:
    """Water Resource Management API"""
    url = f"{_WRM_BASE}/{endpoint}"
    try:
        r = requests.get(url, params=params or {}, timeout=15,
                         headers={"Accept": "application/json"})
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        pass
    return None

def _dwr_fetch(endpoint: str, params: dict | None = None) -> dict | None:
    """กรมทรัพยากรน้ำ (DWR) — Open Data"""
    base = "[water.dwr.go.th](https://water.dwr.go.th/api)"
    try:
        r = requests.get(f"{base}/{endpoint}", params=params or {}, timeout=12,
                         headers={"Accept": "application/json"})
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


# ── Cached wrappers ───────────────────────────────────────
@st.cache_data(ttl=900, show_spinner=False)
def get_weather_today(uid: str, ukey: str) -> dict | None:
    return _tmd_fetch("WeatherToday/V2/", uid, ukey)

@st.cache_data(ttl=900, show_spinner=False)
def get_weather_3h(uid: str, ukey: str) -> dict | None:
    return _tmd_fetch("Weather3Hours/V2/", uid, ukey)

@st.cache_data(ttl=1800, show_spinner=False)
def get_warning(uid: str, ukey: str) -> dict | None:
    return _tmd_fetch("WeatherWarningNews/V1/", uid, ukey)

@st.cache_data(ttl=3600, show_spinner=False)
def get_forecast_region(uid: str, ukey: str) -> dict | None:
    return _tmd_fetch("WeatherForecast7DaysByRegion/V1/", uid, ukey)

@st.cache_data(ttl=3600, show_spinner=False)
def get_seismic(uid: str, ukey: str) -> dict | None:
    return _tmd_fetch("DailySeismicEvent/V1/", uid, ukey)

# Water APIs
@st.cache_data(ttl=600, show_spinner=False)
def get_water_level() -> dict | None:
    """ระดับน้ำแม่น้ำสายหลัก — คลังข้อมูลน้ำแห่งชาติ"""
    result = _thaiwater_fetch("waterlevel", {"limit": 100})
    if not result:
        result = _wrm_fetch("waterlevel/latest", {"count": 50})
    return result

@st.cache_data(ttl=600, show_spinner=False)
def get_water_situation() -> dict | None:
    """สถานการณ์น้ำ — สรุปภาพรวม"""
    return _thaiwater_fetch("water_situation")

@st.cache_data(ttl=1800, show_spinner=False)
def get_flood_forecast() -> dict | None:
    """พยากรณ์น้ำท่วม"""
    return _thaiwater_fetch("flood_forecast")

@st.cache_data(ttl=1800, show_spinner=False)
def get_dam_storage() -> dict | None:
    """ข้อมูลเขื่อน — ปริมาณน้ำในอ่างเก็บน้ำ"""
    result = _thaiwater_fetch("dam/daily", {"limit": 20})
    if not result:
        result = _wrm_fetch("dam/storage")
    return result

@st.cache_data(ttl=600, show_spinner=False)
def get_rainfall_station() -> dict | None:
    """ปริมาณฝนจากสถานีกรมทรัพยากรน้ำ"""
    result = _dwr_fetch("rainfall/today")
    if not result:
        result = _thaiwater_fetch("rainfall/today")
    return result


# ── Utility helpers ───────────────────────────────────────
def haversine(lat1, lon1, lat2, lon2) -> float:
    R = 6371.0
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    dφ = math.radians(lat2 - lat1)
    dλ = math.radians(lon2 - lon1)
    a = math.sin(dφ/2)**2 + math.cos(φ1)*math.cos(φ2)*math.sin(dλ/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def extract_stations_list(data: dict | None) -> list:
    if not data:
        return []
    for k in ["Stations","stations","Data","data","Items","items","results","result"]:
        if k in data and isinstance(data[k], list):
            return data[k]
    return []

def _fnum(d: dict, *keys) -> float | None:
    for k in keys:
        v = d.get(k)
        if v is not None and v != "" and v != "-":
            try:
                f = float(v)
                if not math.isnan(f):
                    return f
            except (TypeError, ValueError):
                pass
    return None

def nearest_obs(rail_stn: dict, tmd_list: list, radius_km: float = 80) -> dict | None:
    best, best_d = None, 9999.0
    for ts in tmd_list:
        slat = _fnum(ts, "Lat","lat","StationLatitude","Latitude")
        slon = _fnum(ts, "Lon","lon","StationLongitude","Longitude")
        if slat is None or slon is None:
            continue
        d = haversine(rail_stn["lat"], rail_stn["lon"], slat, slon)
        if d < best_d and d <= radius_km:
            best_d = d
            best = {**ts, "_km": round(d, 1)}
    return best

def get_rain(obs: dict | None) -> float | None:
    if not obs: return None
    return _fnum(obs, "Rain","rain","Rainfall","rainfall","RainfallToday",
                 "Rain24h","Precip","precip","TotalRain","RainAcc")

def get_temp(obs: dict | None) -> float | None:
    if not obs: return None
    return _fnum(obs, "Temp","temp","Temperature","temperature","AirTemp","MaxTemp")

def get_wind(obs: dict | None) -> float | None:
    if not obs: return None
    return _fnum(obs, "WindSpeed","windspeed","Wind","wind","WindSpd","MaxWindSpeed")

def get_rh(obs: dict | None) -> float | None:
    if not obs: return None
    return _fnum(obs, "Humidity","humidity","RH","rh","RelativeHumidity")

# ── Water level parsing ───────────────────────────────────
def parse_water_level_data(raw: dict | None) -> list[dict]:
    """Parse water level from any API format → list of normalized dicts"""
    if not raw:
        return []
    items = []
    # Try various response formats
    for k in ["data","Data","items","Items","result","results","waterlevel","WaterLevel"]:
        if k in raw and isinstance(raw[k], list):
            items = raw[k]; break
    if not items and isinstance(raw, list):
        items = raw

    result = []
    for it in items:
        station_id   = (it.get("station_id") or it.get("StationCode") or
                        it.get("id") or it.get("ID") or "")
        station_name = (it.get("station_name") or it.get("StationName") or
                        it.get("name") or it.get("Name") or str(station_id))
        water_level  = _fnum(it, "water_level","WaterLevel","level","Level","value","Value","wl")
        bank_level   = _fnum(it, "bank_level","BankLevel","bank","Bank","warning_level")
        lat          = _fnum(it, "lat","Lat","latitude","Latitude")
        lon          = _fnum(it, "lon","Lon","longitude","Longitude")
        river        = (it.get("river_name") or it.get("RiverName") or
                        it.get("river") or it.get("River") or "")
        datetime_str = (it.get("datetime") or it.get("DateTime") or
                        it.get("date") or it.get("Date") or "")

        if station_id or station_name:
            result.append({
                "id":           str(station_id),
                "name":         str(station_name),
                "river":        str(river),
                "water_level":  water_level,
                "bank_level":   bank_level,
                "lat":          lat,
                "lon":          lon,
                "datetime":     datetime_str,
                "overflow":     (water_level or 0) > (bank_level or 9999),
                "fill_pct":     min(((water_level or 0) / (bank_level or 1)) * 100, 100)
                               if bank_level else None,
            })
    return result

def parse_dam_data(raw: dict | None) -> list[dict]:
    if not raw: return []
    items = []
    for k in ["data","Data","dams","Dams","result","Dam"]:
        if k in raw and isinstance(raw[k], list):
            items = raw[k]; break
    result = []
    for it in items:
        result.append({
            "name":         it.get("dam_name") or it.get("name") or it.get("Name") or "",
            "storage_pct":  _fnum(it, "percent_storage","storage_percent","pct","Percent","%","percent"),
            "inflow":       _fnum(it, "inflow","Inflow","in_flow"),
            "outflow":      _fnum(it, "outflow","Outflow","out_flow","release"),
            "storage_mcm":  _fnum(it, "storage","Storage","storage_mcm"),
            "capacity_mcm": _fnum(it, "capacity","Capacity","max_storage"),
            "lat":          _fnum(it, "lat","Lat","latitude"),
            "lon":          _fnum(it, "lon","Lon","longitude"),
        })
    return [d for d in result if d["name"]]

# ── Risk classification ───────────────────────────────────
def risk_class(rain_mm: float | None) -> tuple[str, str, str, str]:
    if rain_mm is None: return "ไม่มีข้อมูล","⚪","badge-na","alert-info"
    if rain_mm == 0:    return "ปกติ","☀️","badge-low","alert-ok"
    if rain_mm < 10:    return "ฝนเล็กน้อย","🌦️","badge-low","alert-ok"
    if rain_mm < 35:    return "ฝนปานกลาง","🌧️","badge-medium","alert-info"
    if rain_mm < 90:    return "ฝนหนัก ⚠️","⛈️","badge-high","alert-warning"
    return "ฝนหนักมาก 🚨","🌊","badge-critical","alert-critical"

def risk_color_hex(rain_mm: float | None) -> str:
    if rain_mm is None: return "#2a4060"
    if rain_mm < 10:    return "#10b981"
    if rain_mm < 35:    return "#3b82f6"
    if rain_mm < 90:    return "#f59e0b"
    return "#ef4444"

def water_risk_class(fill_pct: float | None, overflow: bool = False) -> tuple[str,str,str]:
    """Returns (label, css_class, color)"""
    if overflow:             return "น้ำล้นตลิ่ง 🚨","flood-risk critical","#ef4444"
    if fill_pct is None:     return "ไม่มีข้อมูล","flood-risk","#4a6070"
    if fill_pct < 60:        return "ปกติ","flood-risk normal","#10b981"
    if fill_pct < 80:        return "เฝ้าระวัง","flood-risk watch","#3b82f6"
    if fill_pct < 95:        return "เตือนภัย","flood-risk warning","#f59e0b"
    return "อันตราย","flood-risk critical","#ef4444"

def dam_status_color(pct: float | None) -> str:
    if pct is None: return "#4a6070"
    if pct < 30:    return "#f59e0b"  # น้อย
    if pct < 70:    return "#10b981"  # ปกติ
    if pct < 90:    return "#3b82f6"  # มาก
    return "#ef4444"                   # เต็ม/วิกฤต


# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:18px 0 22px;'>
        <div style='font-size:2.8rem;line-height:1;margin-bottom:6px;'>🚆</div>
        <div style='color:#5bc8ff;font-size:1rem;font-weight:800;letter-spacing:0.5px;'>
            SRT Weather & Water
        </div>
        <div style='color:#2a4060;font-size:0.72rem;margin-top:2px;'>
            ระบบแจ้งเตือนสภาพอากาศและน้ำท่วม<br>โครงข่ายรถไฟแห่งประเทศไทย
        </div>
        <div style='display:flex;justify-content:center;gap:5px;margin-top:8px;flex-wrap:wrap;'>
            <span style='background:rgba(91,200,255,0.08);border:1px solid rgba(91,200,255,0.15);
                border-radius:20px;padding:1px 8px;color:#5bc8ff;font-size:0.65rem;'>TMD</span>
            <span style='background:rgba(6,182,212,0.08);border:1px solid rgba(6,182,212,0.2);
                border-radius:20px;padding:1px 8px;color:#06b6d4;font-size:0.65rem;'>สทนช.</span>
            <span style='background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);
                border-radius:20px;padding:1px 8px;color:#10b981;font-size:0.65rem;'>DWR</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # API Token
    _cur_uid   = _uid()
    _cur_token = _ukey()
    _cur_jwt   = _jwt()

    if _cur_token:
        exp_ts    = _cur_jwt.get("exp", 0)
        exp_dt    = datetime.fromtimestamp(exp_ts, tz=TZ_TH) if exp_ts else None
        days_left = (exp_dt - datetime.now(TZ_TH)).days if exp_dt else 0
        st_color  = "#10b981" if days_left > 30 else "#f59e0b" if days_left > 0 else "#ef4444"
        st.markdown(f"""
        <div style='background:rgba(4,10,19,0.9);border:1px solid rgba(91,200,255,0.12);
            border-radius:10px;padding:10px 14px;margin-bottom:10px;'>
            <div style='color:#2a5070;font-size:0.68rem;font-weight:700;text-transform:uppercase;
                letter-spacing:0.8px;margin-bottom:4px;'>🔑 TMD API Token</div>
            <div style='color:#5bc8ff;font-size:0.8rem;font-weight:600;'>
                uid: <b style="color:#e0f4ff;">{_cur_uid[:20]}</b>
            </div>
            <div style='color:{st_color};font-size:0.73rem;margin-top:3px;'>
                {"✅ ใช้งานได้" if days_left > 0 else "❌ หมดอายุแล้ว"}
                {" · " + str(days_left) + " วัน" if days_left > 0 else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:rgba(127,29,29,0.15);border:1px solid rgba(239,68,68,0.2);
            border-radius:8px;padding:8px 12px;margin-bottom:8px;'>
            <div style='color:#fca5a5;font-size:0.75rem;font-weight:600;'>
                ⚠️ ยังไม่ได้ใส่ TMD Token
            </div>
            <div style='color:#7a3030;font-size:0.7rem;margin-top:2px;'>
                ข้อมูลอุตุฯ จะไม่แสดง
            </div>
        </div>
        """, unsafe_allow_html=True)
        token_in = st.text_input(
            "TMD API Token", type="password",
            placeholder="eyJ0eXAiOiJKV1Qi...",
            help="รับ token ที่ data.tmd.go.th/api/index1.php",
            label_visibility="collapsed",
        )
        if st.button("✅ ยืนยัน Token", use_container_width=True):
            if token_in.strip():
                _set_token(token_in.strip())
                st.cache_data.clear()
                st.rerun()
            else:
                st.error("กรุณาใส่ Token ก่อน")

    st.markdown("---")

    # Filters
    st.markdown("""<div style='color:#5bc8ff;font-size:0.74rem;font-weight:700;
        text-transform:uppercase;letter-spacing:0.8px;margin-bottom:5px;'>
        🛤️ เส้นทาง</div>""", unsafe_allow_html=True)
    line_opts = ["ทุกสาย"] + list(SRT_LINES.keys())
    sel_line = st.selectbox("เส้นทาง", line_opts, label_visibility="collapsed")

    st.markdown("""<div style='color:#5bc8ff;font-size:0.74rem;font-weight:700;
        text-transform:uppercase;letter-spacing:0.8px;margin-bottom:5px;margin-top:8px;'>
        ⚠️ เกณฑ์แจ้งเตือน</div>""", unsafe_allow_html=True)
    alert_thresh = st.select_slider(
        "เกณฑ์", ["ทั้งหมด","ฝนเล็กน้อย","ฝนปานกลาง","ฝนหนัก","ฝนหนักมาก"],
        value="ทั้งหมด", label_visibility="collapsed"
    )

    st.markdown("---")

    now_th = datetime.now(TZ_TH)
    st.markdown(f"""
    <div style='color:#3a5570;font-size:0.73rem;line-height:2;'>
        🕐 เวลาประเทศไทย<br>
        <span style='color:#5bc8ff;font-size:0.92rem;font-weight:700;'>
            {now_th.strftime('%d %b %Y  %H:%M')} น.
        </span><br>
        <span style='font-size:0.68rem;color:#2a4060;'>อัพเดตอัตโนมัติ 10–30 นาที</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 รีเฟรชข้อมูล", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    # Line legend
    for ln, ld in SRT_LINES.items():
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:8px;margin:4px 0;'>
            <div style='width:24px;height:3px;border-radius:2px;background:{ld["color"]};
                box-shadow:0 0 6px {ld["color"]}50;'></div>
            <span style='color:#4a6070;font-size:0.74rem;'>{ld["icon"]} {ln[:12]}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style='color:#1a3040;font-size:0.66rem;margin-top:14px;line-height:1.8;
        border-top:1px solid rgba(91,200,255,0.06);padding-top:10px;'>
        <b style='color:#2a4a60;'>แหล่งข้อมูล:</b><br>
        📡 กรมอุตุนิยมวิทยา (TMD)<br>
        💧 คลังข้อมูลน้ำแห่งชาติ (สทนช.)<br>
        🌊 กรมทรัพยากรน้ำ (DWR)<br>
        🚆 การรถไฟแห่งประเทศไทย (SRT)<br>
        <br>v3.0 · June 2026
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  LOAD ALL DATA
# ══════════════════════════════════════════════════════════════
_cur_uid   = _uid()
_cur_ukey  = _ukey()

with st.spinner("⏳ กำลังโหลดข้อมูลจากทุกแหล่ง..."):
    # TMD
    _obs_today  = get_weather_today(_cur_uid, _cur_ukey)
    _obs_3h     = get_weather_3h(_cur_uid, _cur_ukey)
    _warning    = get_warning(_cur_uid, _cur_ukey)
    _forecast   = get_forecast_region(_cur_uid, _cur_ukey)
    _seismic    = get_seismic(_cur_uid, _cur_ukey)
    # Water
    _water_raw    = get_water_level()
    _dam_raw      = get_dam_storage()
    _flood_raw    = get_flood_forecast()
    _situation    = get_water_situation()
    _dwr_rain_raw = get_rainfall_station()

_obs_list    = extract_stations_list(_obs_today) or extract_stations_list(_obs_3h)
_api_ok      = bool(_obs_list)
_water_list  = parse_water_level_data(_water_raw)
_dam_list    = parse_dam_data(_dam_raw)
_water_ok    = bool(_water_list)
_dam_ok      = bool(_dam_list)

# Supplemental rainfall from DWR
_dwr_rain_list = extract_stations_list(_dwr_rain_raw) if _dwr_rain_raw else []

# ── Enrich stations ───────────────────────────────────────
_station_weather: list[dict] = []
for _s in ALL_STATIONS:
    if sel_line != "ทุกสาย" and _s["line"] != sel_line:
        continue
    _obs  = nearest_obs(_s, _obs_list)
    _rain = get_rain(_obs)
    _temp = get_temp(_obs)
    _wind = get_wind(_obs)
    _rh   = get_rh(_obs)

    # Supplement rain from DWR if TMD missing
    if _rain is None and _dwr_rain_list:
        _dwr_obs = nearest_obs(_s, _dwr_rain_list, radius_km=60)
        if _dwr_obs:
            _rain = get_rain(_dwr_obs)

    # Nearest river station
    _near_river = None
    _river_dist = 9999.0
    for _rv in RIVER_STATIONS_NEAR_RAIL:
        _d = haversine(_s["lat"], _s["lon"], _rv["lat"], _rv["lon"])
        if _d < _river_dist and _d < 100:
            _river_dist = _d
            _near_river = _rv

    # Find water level for nearest river station
    _wl_data = None
    if _near_river and _water_list:
        _rv_id = _near_river["id"]
        for _wl in _water_list:
            if _wl["id"] == _rv_id or _rv_id in _wl["name"]:
                _wl_data = _wl; break
        if not _wl_data:
            # nearest by coord
            for _wl in _water_list:
                if _wl["lat"] and _wl["lon"]:
                    _d2 = haversine(_s["lat"], _s["lon"], _wl["lat"], _wl["lon"])
                    if _d2 < 80:
                        _wl_data = _wl; break

    _lbl, _em, _bc, _ac = risk_class(_rain)
    _station_weather.append({
        **_s,
        "obs":          _obs,
        "rain_mm":      _rain,
        "temp_c":       _temp,
        "wind_ms":      _wind,
        "rh_pct":       _rh,
        "risk_label":   _lbl,
        "risk_emoji":   _em,
        "badge_cls":    _bc,
        "alert_cls":    _ac,
        "tmd_name":     (_obs.get("StationNameTh") or _obs.get("StationName") or "") if _obs else "",
        "tmd_km":       _obs.get("_km","?") if _obs else "?",
        "river_data":   _wl_data,
        "near_river":   _near_river,
        "river_dist_km":round(_river_dist,1) if _near_river else None,
    })

# ── Aggregates ────────────────────────────────────────────
_THRESH_MM = {"ทั้งหมด":0,"ฝนเล็กน้อย":1,"ฝนปานกลาง":10,"ฝนหนัก":35,"ฝนหนักมาก":90}
_t_mm = _THRESH_MM.get(alert_thresh, 0)

_all_rain  = [s["rain_mm"] for s in _station_weather if s["rain_mm"] is not None]
_all_temp  = [s["temp_c"]  for s in _station_weather if s["temp_c"]  is not None]
_n_critical= sum(1 for s in _station_weather if (s["rain_mm"] or 0) >= 90)
_n_heavy   = sum(1 for s in _station_weather if 35 <= (s["rain_mm"] or 0) < 90)
_n_medium  = sum(1 for s in _station_weather if 10 <= (s["rain_mm"] or 0) < 35)
_n_ok      = sum(1 for s in _station_weather if (s["rain_mm"] or 0) < 10)
_max_rain  = max(_all_rain) if _all_rain else None
_avg_temp  = round(sum(_all_temp)/len(_all_temp), 1) if _all_temp else None

# Water aggregates
_n_overflow= sum(1 for w in _water_list if w["overflow"])
_n_warning_water = sum(1 for w in _water_list
                       if w["fill_pct"] and 80 <= w["fill_pct"] < 100)
_avg_dam_pct = (
    round(sum(d["storage_pct"] for d in _dam_list if d["storage_pct"] is not None)
          / max(sum(1 for d in _dam_list if d["storage_pct"] is not None), 1), 1)
    if _dam_list else None
)


# ══════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class='rail-header'>
    <div class='glow-orb'></div>
    <h1>🚆 ระบบแจ้งเตือนสภาพอากาศและน้ำท่วมโครงข่ายรถไฟไทย</h1>
    <div style='color:#4a7090;font-size:0.83rem;margin:2px 0 8px;'>
        Thai Railway Network — Weather · Water · Disaster Alert System
    </div>
    <div class='sub-badges'>
        <span class='mini-badge gold'>🚆 SRT การรถไฟแห่งประเทศไทย</span>
        <span class='mini-badge'>📡 กรมอุตุนิยมวิทยา</span>
        <span class='mini-badge'>💧 สทนช. คลังข้อมูลน้ำแห่งชาติ</span>
        <span class='mini-badge'>🌊 กรมทรัพยากรน้ำ</span>
        <span class='mini-badge'>⏱️ {now_th.strftime('%d %b %Y %H:%M')} น.</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Source status bar
def _status_dot(ok): return "ok" if ok else "err"
def _status_text(ok, name, detail=""): 
    return f"✅ {name}" if ok else f"❌ {name} — ไม่ตอบสนอง"

st.markdown(f"""
<div class='source-bar'>
    <span style='color:#2a4060;font-size:0.74rem;font-weight:700;'>แหล่งข้อมูล:</span>
    <span class='source-pill {"ok" if _api_ok else "err"}'>
        <span class='source-dot {"ok" if _api_ok else "err"}'></span>
        <span style='color:{"#34d399" if _api_ok else "#f87171"};font-weight:600;font-size:0.74rem;'>
            TMD อุตุฯ {"· " + str(len(_obs_list)) + " สถานี" if _api_ok else ""}
        </span>
    </span>
    <span class='source-pill {"ok" if _water_ok else "warn"}'>
        <span class='source-dot {"ok" if _water_ok else "warn"}'></span>
        <span style='color:{"#67e8f9" if _water_ok else "#fbbf24"};font-weight:600;font-size:0.74rem;'>
            สทนช. น้ำท่วม {"· " + str(len(_water_list)) + " สถานี" if _water_ok else "· Mock"}
        </span>
    </span>
    <span class='source-pill {"ok" if _dam_ok else "warn"}'>
        <span class='source-dot {"ok" if _dam_ok else "warn"}'></span>
        <span style='color:{"#67e8f9" if _dam_ok else "#fbbf24"};font-weight:600;font-size:0.74rem;'>
            เขื่อน {"· " + str(len(_dam_list)) + " แห่ง" if _dam_ok else "· ไม่มีข้อมูล"}
        </span>
    </span>
    <span style='margin-left:auto;color:#2a4060;font-size:0.72rem;'>
        🛤️ {sel_line} · 📍 {len(_station_weather)} สถานี · ⚠️ เกณฑ์: {alert_thresh}
    </span>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  MAIN TABS
# ══════════════════════════════════════════════════════════════
tab_exec, tab_water, tab_map, tab_alert, tab_line, tab_forecast, tab_seismic = st.tabs([
    "📊 ภาพรวม",
    "💧 สถานการณ์น้ำ",
    "🗺️ แผนที่",
    "⚠️ แจ้งเตือน",
    "🛤️ รายสาย",
    "🌤️ พยากรณ์",
    "🌋 แผ่นดินไหว",
])


# ╔══════════════════════════════════════════════════════════╗
# ║  TAB 1 — EXECUTIVE DASHBOARD                            ║
# ╚══════════════════════════════════════════════════════════╝
with tab_exec:
    # ── KPI Row ──────────────────────────────────────────────
    kc = st.columns(8)
    kpi_data = [
        ("🚨","ฝนหนักมาก",str(_n_critical),"สถานี","kpi-red"),
        ("⛈️","ฝนหนัก",str(_n_heavy),"สถานี","kpi-orange"),
        ("🌧️","ฝนปานกลาง",str(_n_medium),"สถานี","kpi-blue"),
        ("☀️","สภาพปกติ",str(_n_ok),"สถานี","kpi-green"),
        ("💧","ฝนสูงสุด",f"{_max_rain:.1f}" if _max_rain is not None else "N/A","mm","kpi-gold"),
        ("🌡️","อุณหภูมิเฉลี่ย",f"{_avg_temp}" if _avg_temp is not None else "N/A","°C","kpi-purple"),
        ("🌊","น้ำล้นตลิ่ง",str(_n_overflow),"สถานี","kpi-teal"),
        ("🏗️","เขื่อนเฉลี่ย",f"{_avg_dam_pct}" if _avg_dam_pct else "N/A","%","kpi-water"),
    ]
    for col, (icon, label, val, unit, cls) in zip(kc, kpi_data):
        with col:
            st.markdown(f"""
            <div class='kpi-card {cls} anim'>
                <span class='kpi-icon'>{icon}</span>
                <div class='kpi-label'>{label}</div>
                <div class='kpi-value'>{val}
                    <span style='font-size:0.75rem;color:#4a7090;margin-left:2px;'>{unit}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    # ── Row 2 ─────────────────────────────────────────────────
    c1, c2, c3 = st.columns([1.3, 1.7, 1.8])

    with c1:
        st.markdown('<div class="dash-box"><h4>🎯 สรุปความเสี่ยง</h4>', unsafe_allow_html=True)
        total = max(len(_station_weather), 1)
        levels = [
            ("🚨 ฝนหนักมาก", _n_critical, "#ef4444"),
            ("⛈️ ฝนหนัก",    _n_heavy,    "#f59e0b"),
            ("🌧️ ฝนปานกลาง", _n_medium,   "#3b82f6"),
            ("☀️ ปกติ",       _n_ok,       "#10b981"),
        ]
        for lbl, cnt, col in levels:
            pct = cnt / total * 100
            st.markdown(f"""
            <div style='margin:8px 0;'>
                <div style='display:flex;justify-content:space-between;margin-bottom:4px;'>
                    <span style='color:#8ab8d4;font-size:0.78rem;'>{lbl}</span>
                    <span style='color:#fff;font-size:0.78rem;font-weight:800;'>{cnt}
                        <span style='color:#3a5570;font-size:0.68rem;'>/{total}</span>
                    </span>
                </div>
                <div class='prog-wrap'>
                    <div class='prog-fill' style='width:{pct:.1f}%;background:{col};
                        box-shadow: 0 0 6px {col}60;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if _n_critical > 0:
            ov_color, ov_label = "#ef4444", "🚨 วิกฤต"
        elif _n_heavy > 0:
            ov_color, ov_label = "#f59e0b", "⚠️ ต้องระวัง"
        elif _n_medium > 0:
            ov_color, ov_label = "#3b82f6", "ℹ️ เฝ้าระวัง"
        else:
            ov_color, ov_label = "#10b981", "✅ สภาวะปกติ"

        st.markdown(f"""
        <div style='margin-top:14px;background:rgba(0,0,0,0.4);
            border:1px solid {ov_color}40;border-radius:10px;
            padding:12px 16px;text-align:center;
            box-shadow:0 0 20px {ov_color}15;'>
            <div style='color:#3a5570;font-size:0.68rem;font-weight:700;
                text-transform:uppercase;letter-spacing:1px;'>ภาพรวมความเสี่ยง</div>
            <div style='color:{ov_color};font-size:1.25rem;font-weight:800;
                margin-top:4px;text-shadow:0 0 12px {ov_color}50;'>{ov_label}</div>
        </div>

        <!-- Water summary -->
        <div style='margin-top:10px;background:rgba(6,182,212,0.05);
            border:1px solid rgba(6,182,212,0.15);border-radius:10px;padding:10px 14px;'>
            <div style='color:#06b6d4;font-size:0.68rem;font-weight:700;
                text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;'>
                💧 สถานการณ์น้ำ
            </div>
            <div style='display:flex;justify-content:space-between;align-items:center;'>
                <span style='color:#67e8f9;font-size:0.78rem;'>น้ำล้นตลิ่ง</span>
                <span style='color:{"#ef4444" if _n_overflow>0 else "#10b981"};
                    font-weight:800;'>{_n_overflow} สถานี</span>
            </div>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-top:4px;'>
                <span style='color:#67e8f9;font-size:0.78rem;'>เตือนภัยน้ำ</span>
                <span style='color:{"#f59e0b" if _n_warning_water>0 else "#10b981"};
                    font-weight:800;'>{_n_warning_water} สถานี</span>
            </div>
            <div style='display:flex;justify-content:space-between;align-items:center;margin-top:4px;'>
                <span style='color:#67e8f9;font-size:0.78rem;'>เขื่อนเฉลี่ย</span>
                <span style='color:#a8cce0;font-weight:700;'>
                    {str(_avg_dam_pct)+"%" if _avg_dam_pct else "N/A"}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="dash-box"><h4>🌧️ ปริมาณฝนแยกตามสาย (mm)</h4>', unsafe_allow_html=True)
        _line_stats: dict = {}
        for _s in _station_weather:
            _ln = _s["line"]
            if _ln not in _line_stats:
                _line_stats[_ln] = {"vals": [], "color": _s["line_color"],
                                     "icon": _s["line_icon"], "short": _s["line_short"]}
            if _s["rain_mm"] is not None:
                _line_stats[_ln]["vals"].append(_s["rain_mm"])

        _max_bar = max(
            (max(v["vals"]) for v in _line_stats.values() if v["vals"]), default=50
        ) or 50
        _max_bar = max(_max_bar, 10)

        for _ln_name, _ld in _line_stats.items():
            _vals = _ld["vals"]
            _avg  = round(sum(_vals)/len(_vals), 1) if _vals else None
            _mx   = round(max(_vals), 1) if _vals else None
            _bar_w = (_mx / _max_bar * 100) if _mx else 0
            _bar_col = risk_color_hex(_mx)
            st.markdown(f"""
            <div style='margin:7px 0;'>
                <div style='display:flex;justify-content:space-between;align-items:center;
                    margin-bottom:4px;'>
                    <span style='color:#8ab8d4;font-size:0.77rem;'>
                        <span style='color:{_ld["color"]};font-size:0.85rem;'>●</span>
                        {_ld["icon"]} {_ln_name}
                    </span>
                    <span style='font-size:0.76rem;'>
                        <b style='color:{_bar_col};'>{_mx if _mx is not None else "N/A"}</b>
                        <span style='color:#2a4060;'> mm</span>
                        {" <span style='color:#3a5570;'>/เฉลี่ย "+str(_avg)+"</span>" if _avg else ""}
                    </span>
                </div>
                <div class='prog-wrap'>
                    <div class='prog-fill'
                        style='width:{_bar_w:.1f}%;background:linear-gradient(90deg,{_bar_col},{_bar_col}aa);
                        box-shadow: 0 0 5px {_bar_col}50;'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Mini river overview
        if _water_list[:3]:
            st.markdown("""<div style='margin-top:14px;padding-top:10px;
                border-top:1px solid rgba(6,182,212,0.1);'>
                <div style='color:#06b6d4;font-size:0.72rem;font-weight:700;
                    text-transform:uppercase;letter-spacing:0.8px;margin-bottom:8px;'>
                    💧 ระดับน้ำสำคัญ
                </div>""", unsafe_allow_html=True)
            for _wl in _water_list[:4]:
                _fill = _wl.get("fill_pct")
                _wlv  = _wl.get("water_level")
                _col  = "#ef4444" if _wl["overflow"] else ("#f59e0b" if _fill and _fill > 80 else "#06b6d4")
                st.markdown(f"""
                <div style='display:flex;justify-content:space-between;align-items:center;
                    margin:4px 0;padding:4px 0;border-bottom:1px solid rgba(255,255,255,0.03);'>
                    <span style='color:#5a8099;font-size:0.74rem;'>{_wl["name"][:22]}</span>
                    <span style='color:{_col};font-size:0.78rem;font-weight:700;'>
                        {f"{_wlv:.2f} ม." if _wlv else "N/A"}
                        {"🚨" if _wl["overflow"] else ""}
                    </span>
                </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="dash-box"><h4>🚨 สถานีเสี่ยงสูงสุด TOP 6</h4>', unsafe_allow_html=True)
        _sorted = sorted(_station_weather, key=lambda x: x["rain_mm"] or -1, reverse=True)[:6]
        if not _sorted or _sorted[0]["rain_mm"] is None:
            st.markdown("""<div style='color:#2a4060;font-size:0.82rem;padding:16px 0;text-align:center;'>
                <div style='font-size:2rem;margin-bottom:8px;'>🌤️</div>
                ไม่มีสถานีเสี่ยงในขณะนี้
            </div>""", unsafe_allow_html=True)
        else:
            for i, _s in enumerate(_sorted, 1):
                _rain = _s["rain_mm"]
                if _rain is None: continue
                _rc = risk_color_hex(_rain)
                _lbl, _em, _, _ = risk_class(_rain)
                _has_water = _s["river_data"] is not None
                _wl_overflow = _s["river_data"]["overflow"] if _has_water else False
                st.markdown(f"""
                <div style='display:flex;align-items:center;gap:8px;
                    padding:7px 8px;border-radius:8px;margin:2px 0;
                    background:{"rgba(239,68,68,0.06)" if _rain>=90 else "rgba(255,255,255,0.02)"};
                    border:1px solid {"rgba(239,68,68,0.15)" if _rain>=90 else "rgba(255,255,255,0.03)"};'>
                    <span style='color:#2a4060;font-size:0.78rem;font-weight:800;
                        width:14px;text-align:center;'>{i}</span>
                    <div style='flex:1;min-width:0;'>
                        <div style='color:#c8e4f8;font-size:0.8rem;font-weight:600;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>
                            {_em} {_s["name"]}
                        </div>
                        <div style='color:#2a5070;font-size:0.7rem;'>
                            {_s["province"]}
                            <span style='color:{_s["line_color"]};'>· {_s["line_short"]}</span>
                            {"🌊" if _wl_overflow else ""}
                        </div>
                    </div>
                    <div style='text-align:right;flex-shrink:0;'>
                        <div style='color:{_rc};font-size:1.05rem;font-weight:800;
                            text-shadow:0 0 8px {_rc}50;'>{_rain:.0f}</div>
                        <div style='color:#2a4060;font-size:0.65rem;'>mm</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")

    # ── Station Table ──────────────────────────────────────
    st.markdown('<div class="sec-title">📋 ตารางสถานีรถไฟทั้งหมด</div>', unsafe_allow_html=True)
    _tbl_rows = []
    for _s in sorted(_station_weather, key=lambda x: x["rain_mm"] or -1, reverse=True):
        _lbl, _em, _, _ = risk_class(_s["rain_mm"])
        _rv = _s.get("river_data")
        _tbl_rows.append({
            "สาย":             f"{_s['line_icon']} {_s['line_short']}",
            "สถานีรถไฟ":       _s["name"],
            "จังหวัด":         _s["province"],
            "ฝน (mm)":         round(_s["rain_mm"], 1) if _s["rain_mm"] is not None else None,
            "ระดับอุตุฯ":      f"{_em} {_lbl}",
            "อุณหภูมิ (°C)":   round(_s["temp_c"], 1) if _s["temp_c"] is not None else None,
            "ลม (m/s)":        round(_s["wind_ms"], 1) if _s["wind_ms"] is not None else None,
            "RH (%)":          round(_s["rh_pct"], 0) if _s["rh_pct"] is not None else None,
            "ระดับน้ำ (ม.)":   round(_rv["water_level"], 2) if _rv and _rv["water_level"] else None,
            "น้ำล้น":          "🚨 ล้น" if _rv and _rv["overflow"] else ("✅" if _rv else "—"),
            "แม่น้ำ":          _s["near_river"]["river"] if _s.get("near_river") else "—",
        })
    _df = pd.DataFrame(_tbl_rows)
    st.dataframe(
        _df, use_container_width=True, hide_index=True, height=360,
        column_config={
            "ฝน (mm)":       st.column_config.NumberColumn("🌧️ ฝน (mm)", format="%.1f"),
            "อุณหภูมิ (°C)": st.column_config.NumberColumn("🌡️ °C", format="%.1f"),
            "ลม (m/s)":      st.column_config.NumberColumn("💨 ลม", format="%.1f"),
            "RH (%)":        st.column_config.NumberColumn("💧 RH%", format="%.0f"),
            "ระดับน้ำ (ม.)": st.column_config.NumberColumn("🌊 น้ำ (ม.)", format="%.2f"),
        },
    )


# ╔══════════════════════════════════════════════════════════╗
# ║  TAB 2 — WATER SITUATION                                ║
# ╚══════════════════════════════════════════════════════════╝
with tab_water:
    st.markdown('<div class="sec-title-water">💧 สถานการณ์น้ำในโครงข่ายรถไฟ</div>',
                unsafe_allow_html=True)

    # ── KPI row ───────────────────────────────────────────
    wc = st.columns(5)
    wkpi = [
        ("🚨","สถานีน้ำล้นตลิ่ง",str(_n_overflow),"สถานี","kpi-red"),
        ("⚠️","เกณฑ์เฝ้าระวัง",str(_n_warning_water),"สถานี","kpi-orange"),
        ("🏗️","เขื่อนทั้งหมด",str(len(_dam_list)),"แห่ง","kpi-blue"),
        ("📊","ความจุเขื่อนเฉลี่ย",str(_avg_dam_pct) if _avg_dam_pct else "N/A","%","kpi-teal"),
        ("🌊","แม่น้ำที่ติดตาม",str(len(RIVER_STATIONS_NEAR_RAIL)),"สาย","kpi-water"),
    ]
    for col, (icon, label, val, unit, cls) in zip(wc, wkpi):
        with col:
            st.markdown(f"""
            <div class='kpi-card {cls}'>
                <span class='kpi-icon'>{icon}</span>
                <div class='kpi-label'>{label}</div>
                <div class='kpi-value'>{val}
                    <span style='font-size:0.75rem;color:#4a7090;margin-left:2px;'>{unit}</span>
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("")
    wa, wb = st.columns([1.8, 1.4])

    with wa:
        # ── River water levels near railway ────────────────
        st.markdown('<div class="sec-title-water">🌊 ระดับน้ำแม่น้ำใกล้แนวรถไฟ</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="dash-box water">', unsafe_allow_html=True)

        if _water_list:
            # Show actual data
            for _wl in _water_list[:12]:
                _lv = _wl["water_level"]
                _bk = _wl["bank_level"]
                _fp = _wl["fill_pct"]
                _ov = _wl["overflow"]
                _wlabel, _wcls, _wcol = water_risk_class(_fp, _ov)
                _bar_w = min(_fp or 0, 100)

                st.markdown(f"""
                <div class='river-row'>
                    <div style='flex:1.8;'>
                        <div class='river-name'>{_wl["name"][:26]}</div>
                        <div style='display:flex;align-items:center;gap:6px;margin-top:3px;'>
                            <span class='{_wcls}'>{_wlabel}</span>
                            <span style='color:#2a4060;font-size:0.68rem;'>{_wl["river"] or ""}</span>
                        </div>
                    </div>
                    <div class='river-bar'>
                        <div class='prog-wrap'>
                            <div class='prog-fill' style='width:{_bar_w:.0f}%;background:{_wcol};
                                box-shadow:0 0 5px {_wcol}50;'></div>
                        </div>
                        <div style='color:#2a4060;font-size:0.65rem;margin-top:2px;'>
                            {f"ตลิ่ง: {_bk:.1f} ม." if _bk else "ไม่มีข้อมูลตลิ่ง"}
                        </div>
                    </div>
                    <div class='river-val'>
                        {f"{_lv:.2f} ม." if _lv is not None else "N/A"}
                        {"<div style='font-size:0.68rem;color:#ef4444;'>🚨 ล้น</div>" if _ov else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Show reference river stations
            st.markdown("""
            <div style='color:#2a4060;font-size:0.8rem;padding:8px 0 12px;'>
                📡 กำลังรอข้อมูลจาก API คลังข้อมูลน้ำแห่งชาติ...
            </div>
            """, unsafe_allow_html=True)
            for _rv in RIVER_STATIONS_NEAR_RAIL:
                _line_col = SRT_LINES.get(_rv["line"],{}).get("color","#5bc8ff")
                st.markdown(f"""
                <div class='river-row'>
                    <div style='flex:1.8;'>
                        <div class='river-name'>{_rv["name"]}</div>
                        <div style='color:#2a4060;font-size:0.7rem;margin-top:2px;'>
                            <span style='color:{_line_col};'>●</span>
                            {_rv["line"]} · สถานี {_rv["id"]}
                        </div>
                    </div>
                    <div style='flex:1.2;'>
                        <span class='chip water'>{_rv["river"]}</span>
                    </div>
                    <div class='river-val' style='color:#2a4060;'>รอข้อมูล</div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with wb:
        # ── Dam storage ────────────────────────────────────
        st.markdown('<div class="sec-title-water">🏗️ ปริมาณน้ำในเขื่อน</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="dash-box water">', unsafe_allow_html=True)

        if _dam_list:
            for _dm in sorted(_dam_list, key=lambda x: x["storage_pct"] or 0, reverse=True)[:10]:
                _pct = _dm["storage_pct"]
                _dcol = dam_status_color(_pct)
                _dlab = ("น้อย" if _pct and _pct < 30 else
                         "เต็ม/วิกฤต" if _pct and _pct >= 90 else
                         "มาก" if _pct and _pct >= 70 else "ปกติ")
                st.markdown(f"""
                <div style='margin:8px 0;'>
                    <div style='display:flex;justify-content:space-between;margin-bottom:4px;'>
                        <span style='color:#a8cce0;font-size:0.78rem;font-weight:600;'>
                            🏗️ {_dm["name"][:20]}
                        </span>
                        <span style='color:{_dcol};font-size:0.78rem;font-weight:800;'>
                            {f"{_pct:.0f}%" if _pct else "N/A"} — {_dlab}
                        </span>
                    </div>
                    <div class='prog-wrap' style='height:8px;'>
                        <div class='prog-fill' style='width:{min(_pct or 0,100):.0f}%;
                            background:linear-gradient(90deg,{_dcol}aa,{_dcol});'></div>
                    </div>
                    {f"<div style='display:flex;justify-content:space-between;margin-top:3px;'><span style='color:#2a4060;font-size:0.67rem;'>↗ ไหลเข้า: {_dm['inflow']:.0f} ลบ.ม./วิ</span><span style='color:#2a4060;font-size:0.67rem;'>↘ ระบาย: {_dm['outflow']:.0f}</span></div>" if _dm.get("inflow") and _dm.get("outflow") else ""}
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='color:#2a4060;text-align:center;padding:24px 0;'>
                <div style='font-size:2rem;margin-bottom:8px;'>🏗️</div>
                <div style='font-size:0.82rem;'>รอข้อมูลจาก API เขื่อน...</div>
                <div style='font-size:0.72rem;margin-top:6px;color:#1a3040;'>
                    เชื่อมต่อ: app.thaiwater.net
                </div>
            </div>""", unsafe_allow_html=True)

        # ── Flood alert zones ──────────────────────────────
        st.markdown("""<div style='margin-top:14px;padding-top:12px;
            border-top:1px solid rgba(6,182,212,0.1);'>
            <div style='color:#06b6d4;font-size:0.72rem;font-weight:700;
                text-transform:uppercase;letter-spacing:0.8px;margin-bottom:8px;'>
                🚨 พื้นที่เสี่ยงน้ำท่วมใกล้รางรถไฟ
            </div>""", unsafe_allow_html=True)

        # Static known flood-prone railway zones
        _flood_zones = [
            {"area":"อยุธยา–ลพบุรี","line":"สายเหนือ","risk":"warning","note":"ที่ราบลุ่ม เจ้าพระยา"},
            {"area":"นครราชสีมา","line":"สายNE","risk":"watch","note":"ลุ่มน้ำมูล"},
            {"area":"อุบลราชธานี","line":"สายIS","risk":"warning","note":"ลุ่มน้ำมูล-ชี"},
            {"area":"ฉะเชิงเทรา","line":"สายตะวันออก","risk":"watch","note":"บางปะกง"},
            {"area":"นครศรีธรรมราช","line":"สายใต้","risk":"watch","note":"ฝั่งตะวันออก"},
        ]
        for _fz in _flood_zones:
            _rc_map = {"warning":"warning","watch":"watch","critical":"critical","normal":"normal"}
            st.markdown(f"""
            <div style='display:flex;align-items:center;justify-content:space-between;
                margin:5px 0;padding:5px 0;border-bottom:1px solid rgba(255,255,255,0.03);'>
                <div>
                    <div style='color:#8ab8d4;font-size:0.76rem;font-weight:600;'>
                        📍 {_fz["area"]}
                    </div>
                    <div style='color:#2a4060;font-size:0.68rem;'>{_fz["note"]}</div>
                </div>
                <span class='flood-risk {_rc_map.get(_fz["risk"],"normal")}'>
                    {{"warning":"⚠️ เฝ้าระวัง","watch":"👁 ติดตาม","critical":"🚨 อันตราย"}
                     .get(_fz["risk"],"✅ ปกติ")}
                </span>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Water Situation Summary ────────────────────────────
    if _situation:
        st.markdown('<div class="sec-title-water">📋 รายงานสถานการณ์น้ำ (สทนช.)</div>',
                    unsafe_allow_html=True)
        _sit_data = _situation.get("data") or _situation.get("Data") or {}
        if isinstance(_sit_data, dict) and _sit_data:
            _sc = st.columns(3)
            for i, (k, v) in enumerate(list(_sit_data.items())[:6]):
                with _sc[i % 3]:
                    st.markdown(f"""
                    <div class='alert-card alert-water'>
                        <div class='alert-card-title'>💧 {str(k)[:30]}</div>
                        <div class='alert-card-body'>{str(v)[:120]}</div>
                    </div>""", unsafe_allow_html=True)
        elif isinstance(_situation, dict):
            with st.expander("ดูข้อมูลดิบจาก API"):
                st.json(_situation)

    # ── Rainfall comparison TMD vs DWR ────────────────────
    if _dwr_rain_list and _obs_list:
        st.markdown('<div class="sec-title-water">🔬 เปรียบเทียบฝน: TMD vs กรมทรัพยากรน้ำ</div>',
                    unsafe_allow_html=True)
        _cmp_rows = []
        for _s in _station_weather[:8]:
            _tmd_rain = _s["rain_mm"]
            _dwr_obs  = nearest_obs(_s, _dwr_rain_list, 60)
            _dwr_rain = get_rain(_dwr_obs) if _dwr_obs else None
            if _tmd_rain or _dwr_rain:
                _cmp_rows.append({
                    "สถานีรถไฟ":     _s["name"],
                    "TMD (mm)":      round(_tmd_rain,1) if _tmd_rain else None,
                    "กรมทรัพยากรน้ำ (mm)": round(_dwr_rain,1) if _dwr_rain else None,
                    "ต่าง (mm)":     round(abs((_tmd_rain or 0)-(_dwr_rain or 0)),1)
                                     if _tmd_rain and _dwr_rain else None,
                })
        if _cmp_rows:
            st.dataframe(pd.DataFrame(_cmp_rows), use_container_width=True,
                         hide_index=True, height=220)


# ╔══════════════════════════════════════════════════════════╗
# ║  TAB 3 — MAP                                            ║
# ╚══════════════════════════════════════════════════════════╝
with tab_map:
    st.markdown('<div class="sec-title">🗺️ แผนที่โครงข่ายรถไฟ สภาพอากาศ และระดับน้ำ</div>',
                unsafe_allow_html=True)
    try:
        import folium
        from streamlit_folium import st_folium

        _m = folium.Map(location=[13.5, 101.5], zoom_start=6, tiles=None)
        folium.TileLayer(
            tiles="[{s}.basemaps.cartocdn.com](https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png)",
            attr="© OpenStreetMap © CARTO", name="Dark", max_zoom=19,
        ).add_to(_m)

        # Draw rail lines
        for _ln, _ld in SRT_LINES.items():
            if sel_line != "ทุกสาย" and _ln != sel_line:
                continue
            _coords = [[s["lat"], s["lon"]] for s in _ld["stations"]]
            folium.PolyLine(_coords, color=_ld["color"], weight=3.5,
                            opacity=0.85, tooltip=f"{_ln} — {_ld['desc']}").add_to(_m)

        # Station markers
        for _sw in _station_weather:
            _rc = risk_color_hex(_sw["rain_mm"])
            _lbl, _em, _, _ = risk_class(_sw["rain_mm"])
            _ic_color = {
                "#ef4444":"red","#f59e0b":"orange",
                "#3b82f6":"blue","#10b981":"green","#2a4060":"gray"
            }.get(_rc, "blue")
            _rv = _sw.get("river_data")
            _popup_html = f"""
            <div style='font-family:Sarabun,sans-serif;min-width:200px;max-width:260px;'>
                <b style='font-size:1rem;'>{_sw['name']}</b>
                <br><span style='color:#555;font-size:0.8rem;'>
                    {_sw['province']} · {_sw['line']}</span>
                <hr style='margin:6px 0;'>
                <table style='font-size:0.8rem;width:100%;'>
                    <tr><td>🌧️ ฝน</td>
                        <td><b>{f"{_sw['rain_mm']:.1f} mm" if _sw['rain_mm'] is not None else 'N/A'}</b></td></tr>
                    <tr><td>⚠️ ระดับ</td><td>{_em} {_lbl}</td></tr>
                    <tr><td>🌡️ อุณหภูมิ</td>
                        <td>{f"{_sw['temp_c']:.1f}°C" if _sw['temp_c'] is not None else 'N/A'}</td></tr>
                    <tr><td>💨 ลม</td>
                        <td>{f"{_sw['wind_ms']:.1f} m/s" if _sw['wind_ms'] is not None else 'N/A'}</td></tr>
                    {f'<tr><td>🌊 ระดับน้ำ</td><td><b>{_rv["water_level"]:.2f} ม.</b>{"&nbsp;🚨" if _rv["overflow"] else ""}</td></tr>' if _rv and _rv.get("water_level") else ''}
                    {f'<tr><td>🏞️ แม่น้ำ</td><td>{_sw["near_river"]["river"] if _sw.get("near_river") else ""}</td></tr>' if _sw.get("near_river") else ''}
                </table>
            </div>"""
            folium.Marker(
                location=[_sw["lat"], _sw["lon"]],
                popup=folium.Popup(_popup_html, max_width=280),
                tooltip=f"{_sw['name']} {_em} "
                        f"{_sw['rain_mm']:.0f}mm" if _sw['rain_mm'] else _sw['name'],
                icon=folium.Icon(color=_ic_color, icon="train", prefix="fa"),
            ).add_to(_m)

        # River station markers (water level)
        for _rv_stn in RIVER_STATIONS_NEAR_RAIL:
            if sel_line != "ทุกสาย" and _rv_stn["line"] != sel_line:
                continue
            # Find matching water data
            _wl_match = next((w for w in _water_list
                              if _rv_stn["id"] in w["id"] or _rv_stn["id"] in w["name"]),None)
            _wl_val = _wl_match["water_level"] if _wl_match else None
            _wl_ov  = _wl_match["overflow"] if _wl_match else False
            _dot_col = "#ef4444" if _wl_ov else "#06b6d4"
            folium.CircleMarker(
                location=[_rv_stn["lat"], _rv_stn["lon"]],
                radius=7 if _wl_ov else 5,
                color=_dot_col,
                fill=True, fill_opacity=0.7,
                tooltip=(f"💧 {_rv_stn['name']} "
                         f"{'🚨 น้ำล้น!' if _wl_ov else ''} "
                         f"{f'· {_wl_val:.2f}ม.' if _wl_val else ''}"),
            ).add_to(_m)

        st.caption("🚆 ไอคอนรถไฟ = สถานีรถไฟ (คลิกเพื่อดูรายละเอียด) · "
                   "🔵 วงกลม = สถานีวัดน้ำ · 🔴 = น้ำเกินตลิ่ง")
        st_folium(_m, width="100%", height=600, returned_objects=[])

    except ImportError:
        st.warning("⚠️ ติดตั้ง `folium` และ `streamlit-folium` เพื่อแสดงแผนที่")
        _map_df = pd.DataFrame([{
            "lat":_sw["lat"],"lon":_sw["lon"],
            "ฝน mm":_sw["rain_mm"],
        } for _sw in _station_weather])
        st.map(_map_df, latitude="lat", longitude="lon", use_container_width=True)

    # Legend
    st.markdown("""
    <div style='display:flex;gap:14px;flex-wrap:wrap;margin-top:10px;align-items:center;'>
        <span style='color:#3a5570;font-size:0.76rem;font-weight:700;'>เส้นทาง:</span>
    """ + "".join([
        f"<span style='display:flex;align-items:center;gap:4px;'>"
        f"<span style='width:18px;height:3px;background:{ld['color']};border-radius:2px;display:inline-block;'></span>"
        f"<span style='color:#5a8099;font-size:0.74rem;'>{ld['icon']}{ln}</span></span>"
        for ln, ld in SRT_LINES.items()
    ]) + """
        <span style='color:#3a5570;font-size:0.76rem;font-weight:700;margin-left:6px;'>ระดับน้ำ:</span>
        <span style='color:#67e8f9;font-size:0.74rem;'>● ปกติ</span>
        <span style='color:#ef4444;font-size:0.74rem;'>● เกินตลิ่ง</span>
    </div>
    """, unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════╗
# ║  TAB 4 — ALERTS                                         ║
# ╚══════════════════════════════════════════════════════════╝
with tab_alert:
    _ca, _cb = st.columns([1.6, 1.1])

    with _ca:
        st.markdown('<div class="sec-title">🌧️ แจ้งเตือนสถานีเสี่ยงฝน</div>',
                    unsafe_allow_html=True)
        _alert_stations = [
            s for s in sorted(_station_weather, key=lambda x: x["rain_mm"] or -1, reverse=True)
            if (s["rain_mm"] or 0) >= _t_mm
        ]
        if _alert_stations:
            for _s in _alert_stations:
                _lbl, _em, _, _ac = risk_class(_s["rain_mm"])
                _rv = _s.get("river_data")
                _combined_risk = (_ac == "alert-critical" or
                                  (_rv and _rv.get("overflow")))
                _card_cls = "alert-critical" if _combined_risk else _ac
                st.markdown(f"""
                <div class='alert-card {_card_cls}'>
                    <div style='display:flex;justify-content:space-between;'>
                        <div style='flex:1;'>
                            <div class='alert-card-title'>
                                {_em} {_s['name']}
                                <span style='color:{_s["line_color"]};font-size:0.72rem;
                                    font-weight:600;margin-left:8px;'>
                                    [{_s["line_short"]}] {_s["line"]}
                                </span>
                                {"<span style='margin-left:6px;font-size:0.75rem;'>🌊 น้ำล้น</span>" if _rv and _rv.get("overflow") else ""}
                            </div>
                            <div class='alert-card-body'>
                                📍 {_s['province']}
                                {f"· 🌧️ <b>{_s['rain_mm']:.1f} mm</b>" if _s["rain_mm"] else ""}
                                {f"· 🌡️ {_s['temp_c']:.1f}°C" if _s["temp_c"] else ""}
                                {f"· 💨 {_s['wind_ms']:.1f} m/s" if _s["wind_ms"] else ""}
                                {f"<br>🌊 แม่น้ำ: {_s['near_river']['name']} · ระดับ: {_rv['water_level']:.2f} ม." if _rv and _rv.get("water_level") else ""}
                                {f"<br>📡 อุตุฯ: {_s['tmd_name']} ({_s['tmd_km']} km)" if _s["tmd_name"] else ""}
                            </div>
                        </div>
                        <div style='text-align:right;min-width:64px;margin-left:10px;'>
                            <div style='color:#fff;font-size:1.25rem;font-weight:800;'>
                                {f"{_s['rain_mm']:.0f}" if _s["rain_mm"] is not None else "—"}
                            </div>
                            <div style='color:#3a5570;font-size:0.68rem;'>mm/วัน</div>
                            {f"<div style='color:#06b6d4;font-size:0.72rem;font-weight:700;margin-top:4px;'>{_rv['water_level']:.2f}ม.</div>" if _rv and _rv.get("water_level") else ""}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='alert-card alert-ok'>
                <div class='alert-card-title'>✅ ไม่มีสถานีเกินเกณฑ์ ({alert_thresh})</div>
                <div class='alert-card-body'>
                    สภาพอากาศทุกสถานีในเส้นทางที่เลือกปกติ
                    {"· ข้อมูลอาจยังไม่ครบถ้วน" if not _obs_list else ""}
                </div>
            </div>""", unsafe_allow_html=True)

        # Water overflow alerts
        _overflow_stns = [s for s in _station_weather
                          if s.get("river_data") and s["river_data"].get("overflow")]
        if _overflow_stns:
            st.markdown('<div class="sec-title-water">🚨 น้ำล้นตลิ่งใกล้แนวรถไฟ</div>',
                        unsafe_allow_html=True)
            for _s in _overflow_stns:
                _rv = _s["river_data"]
                st.markdown(f"""
                <div class='alert-card alert-critical'>
                    <div class='alert-card-title'>
                        🌊 น้ำล้นตลิ่ง — {_s["name"]}
                    </div>
                    <div class='alert-card-body'>
                        📍 {_s["province"]} · สาย {_s["line"]}<br>
                        แม่น้ำ: {_rv.get("river","") or _s.get("near_river",{}).get("river","")}
                        · ระดับน้ำ: <b>{_rv["water_level"]:.2f} ม.</b>
                        (ตลิ่ง {_rv["bank_level"]:.2f} ม.)
                    </div>
                    <div class='alert-card-meta'>
                        ⚠️ อาจมีผลกระทบต่อเส้นทางรถไฟ — ติดต่อ SRT กรณีฉุกเฉิน 1690
                    </div>
                </div>""", unsafe_allow_html=True)

    with _cb:
        st.markdown('<div class="sec-title">📰 ข่าวเตือนภัย TMD</div>', unsafe_allow_html=True)
        _wlist = []
        if _warning:
            for k in ["WeatherWarnings","warnings","items","Items","NewsItems","data"]:
                if k in _warning and isinstance(_warning[k], list):
                    _wlist = _warning[k]; break
        if _wlist:
            for wi in _wlist[:5]:
                _t = str(wi.get("Title") or wi.get("Subject") or "ข่าวเตือนภัย")[:55]
                _b = str(wi.get("Detail") or wi.get("Body") or wi.get("content") or "")
                _d = str(wi.get("Date") or wi.get("IssueDate") or "")
                st.markdown(f"""
                <div class='alert-card alert-warning'>
                    <div class='alert-card-title'>⚠️ {_t}</div>
                    <div class='alert-card-body'>{_b[:100]}{"…" if len(_b)>100 else ""}</div>
                    {"<div class='alert-card-meta'>📅 "+_d[:16]+"</div>" if _d else ""}
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='alert-card alert-ok'>
                <div class='alert-card-title'>✅ ไม่มีข่าวเตือนภัย</div>
                <div class='alert-card-body'>หรือยังไม่ได้รับข้อมูลจาก TMD</div>
            </div>""", unsafe_allow_html=True)

        # Flood forecast
        st.markdown('<div class="sec-title-water">🌊 พยากรณ์น้ำท่วม (สทนช.)</div>',
                    unsafe_allow_html=True)
        if _flood_raw:
            _fl_items = []
            for k in ["data","Data","forecasts","items"]:
                if k in _flood_raw and isinstance(_flood_raw[k], list):
                    _fl_items = _flood_raw[k]; break
            for _fi in _fl_items[:4]:
                _fa = str(_fi.get("area") or _fi.get("Area") or _fi.get("province") or "")
                _fd = str(_fi.get("description") or _fi.get("detail") or _fi.get("forecast") or "")
                _fr = str(_fi.get("risk") or _fi.get("level") or "")
                _fac = "alert-critical" if "สูง" in _fr else "alert-warning" if "ปาน" in _fr else "alert-water"
                st.markdown(f"""
                <div class='alert-card {_fac}'>
                    <div class='alert-card-title'>🌊 {_fa[:40] or "พยากรณ์น้ำท่วม"}</div>
                    <div class='alert-card-body'>{_fd[:100]}</div>
                    {"<div class='alert-card-meta'>ความเสี่ยง: "+_fr+"</div>" if _fr else ""}
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='alert-card alert-water'>
                <div class='alert-card-title'>💧 ระบบพยากรณ์น้ำท่วม</div>
                <div class='alert-card-body'>รอข้อมูลจาก สทนช. API</div>
            </div>""", unsafe_allow_html=True)

        # Criteria reference
        st.markdown('<div class="sec-title" style="margin-top:16px;">📋 เกณฑ์มาตรฐาน</div>',
                    unsafe_allow_html=True)
        for _em2, _lv, _mm, _cls in [
            ("🌦️","ฝนเล็กน้อย","< 10 mm/วัน","alert-ok"),
            ("🌧️","ฝนปานกลาง","10–35 mm/วัน","alert-info"),
            ("⛈️","ฝนหนัก","35–90 mm/วัน","alert-warning"),
            ("🌊","ฝนหนักมาก","> 90 mm/วัน","alert-critical"),
        ]:
            st.markdown(f"""
            <div class='alert-card {_cls}' style='padding:6px 12px;'>
                <div class='alert-card-body'>{_em2} <b>{_lv}</b> — {_mm}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style='margin-top:10px;background:rgba(6,182,212,0.05);
            border:1px solid rgba(6,182,212,0.15);border-radius:10px;padding:10px 14px;'>
            <div style='color:#06b6d4;font-size:0.7rem;font-weight:700;
                text-transform:uppercase;letter-spacing:0.8px;margin-bottom:5px;'>เกณฑ์น้ำท่วม</div>
            <div style='color:#3a6070;font-size:0.73rem;line-height:1.8;'>
                ☑️ ตลิ่ง &lt;80% — ปกติ<br>
                ⚠️ 80–95% — เฝ้าระวัง<br>
                🚨 &gt;95% หรือล้น — อันตราย
            </div>
        </div>
        <div style='margin-top:8px;background:rgba(255,255,255,0.02);
            border:1px solid rgba(91,200,255,0.08);border-radius:8px;padding:8px 12px;'>
            <div style='color:#2a4060;font-size:0.7rem;'>
                📞 ศูนย์ปฏิบัติการน้ำ: 1460<br>
                🚆 SRT ฉุกเฉิน: 1690
            </div>
        </div>
        """, unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════╗
# ║  TAB 5 — PER LINE                                       ║
# ╚══════════════════════════════════════════════════════════╝
with tab_line:
    _lines_show = [sel_line] if sel_line != "ทุกสาย" else list(SRT_LINES.keys())
    for _ln in _lines_show:
        _ld = SRT_LINES[_ln]
        _ln_stns     = [s for s in _station_weather if s["line"] == _ln]
        _ln_rains    = [s["rain_mm"] for s in _ln_stns if s["rain_mm"] is not None]
        _ln_max      = max(_ln_rains) if _ln_rains else None
        _ln_avg      = round(sum(_ln_rains)/len(_ln_rains), 1) if _ln_rains else None
        _ln_heavy_n  = sum(1 for r in _ln_rains if r >= 35)
        _ln_overflow = sum(1 for s in _ln_stns
                           if s.get("river_data") and s["river_data"].get("overflow"))

        with st.expander(
            f"{_ld['icon']} {_ln} — {_ld['desc']}  |  "
            + (f"🚨 {_ln_heavy_n} สถานีฝนหนัก" if _ln_heavy_n else "✅ ฝนปกติ")
            + (f"  🌊 {_ln_overflow} จุดน้ำล้น" if _ln_overflow else ""),
            expanded=(sel_line != "ทุกสาย")
        ):
            _mc = st.columns(5)
            with _mc[0]: st.metric("🌧️ ฝนสูงสุด",
                                   f"{_ln_max:.1f} mm" if _ln_max is not None else "N/A")
            with _mc[1]: st.metric("📊 ฝนเฉลี่ย",
                                   f"{_ln_avg} mm" if _ln_avg else "N/A")
            with _mc[2]: st.metric("⛈️ สถานีเสี่ยงฝน", f"{_ln_heavy_n} สถานี")
            with _mc[3]: st.metric("🌊 จุดน้ำล้น",
                                   f"{_ln_overflow} จุด",
                                   delta=f"วิกฤต" if _ln_overflow > 0 else None,
                                   delta_color="inverse")
            with _mc[4]: st.metric("📍 สถานีทั้งหมด", f"{len(_ln_stns)} สถานี")

            # Header
            st.markdown(f"""
            <div class='stn-row' style='background:rgba(91,200,255,0.05);'>
                <span style='color:#5bc8ff;font-size:0.72rem;font-weight:700;'>สถานี</span>
                <span style='color:#5bc8ff;font-size:0.72rem;font-weight:700;'>จังหวัด</span>
                <span style='color:#5bc8ff;font-size:0.72rem;font-weight:700;text-align:right;'>ฝน mm</span>
                <span style='color:#5bc8ff;font-size:0.72rem;font-weight:700;text-align:right;'>°C</span>
                <span style='color:#67e8f9;font-size:0.72rem;font-weight:700;text-align:right;'>ระดับน้ำ</span>
                <span style='color:#5bc8ff;font-size:0.72rem;font-weight:700;text-align:right;'>ระดับอุตุฯ</span>
            </div>""", unsafe_allow_html=True)

            for _s in _ln_stns:
                _lbl, _em, _, _ = risk_class(_s["rain_mm"])
                _rc = risk_color_hex(_s["rain_mm"])
                _rv = _s.get("river_data")
                _wl_val = _rv["water_level"] if _rv else None
                _wl_ov  = _rv["overflow"] if _rv else False
                _wl_col = "#ef4444" if _wl_ov else ("#f59e0b" if _rv and (_rv.get("fill_pct") or 0) > 80 else "#06b6d4")
                _bdg_cls = (
                    "critical" if _s["rain_mm"] and _s["rain_mm"] >= 90 else
                    "high"     if _s["rain_mm"] and _s["rain_mm"] >= 35 else
                    "medium"   if _s["rain_mm"] and _s["rain_mm"] >= 10 else
                    "low"      if _s["rain_mm"] is not None else "na"
                )
                st.markdown(f"""
                <div class='stn-row'
                    style='{"border-left:3px solid #ef4444;" if _wl_ov else ""}'>
                    <div>
                        <div class='stn-name'>🚉 {_s['name']}</div>
                        <div class='stn-prov'>km {_s.get("km","")}</div>
                    </div>
                    <div class='stn-prov'>{_s['province']}</div>
                    <div class='stn-val' style='color:{_rc};font-weight:800;'>
                        {f"{_s['rain_mm']:.1f}" if _s["rain_mm"] is not None else "—"}
                    </div>
                    <div class='stn-val'>
                        {f"{_s['temp_c']:.1f}" if _s["temp_c"] is not None else "—"}
                    </div>
                    <div class='stn-val' style='color:{_wl_col};font-weight:700;'>
                        {f"{_wl_val:.2f}ม." if _wl_val else "—"}
                        {"🚨" if _wl_ov else ""}
                    </div>
                    <div class='stn-val'>
                        <span class='badge badge-{_bdg_cls}'>{_em} {_lbl}</span>
                    </div>
                </div>""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════╗
# ║  TAB 6 — FORECAST                                       ║
# ╚══════════════════════════════════════════════════════════╝
with tab_forecast:
    st.markdown('<div class="sec-title">🌤️ พยากรณ์อากาศล่วงหน้า 7 วัน (รายภาค)</div>',
                unsafe_allow_html=True)

    _REGION_LINES = {
        "ภาคเหนือ":                 ["สายเหนือ"],
        "ภาคตะวันออกเฉียงเหนือ":   ["สายตะวันออกเฉียงเหนือ","สายอีสานใต้"],
        "ภาคกลาง":                  ["สายเหนือ","สายตะวันออกเฉียงเหนือ"],
        "ภาคตะวันออก":             ["สายตะวันออก"],
        "ภาคใต้ฝั่งตะวันออก":     ["สายใต้"],
        "ภาคใต้ฝั่งตะวันตก":      ["สายใต้"],
    }

    if _forecast:
        _regions = None
        for k in ["WeatherForecasts","forecasts","data","Regions","regions"]:
            if k in _forecast and isinstance(_forecast[k], list):
                _regions = _forecast[k]; break

        if _regions:
            for _rg in _regions[:6]:
                _rname = (_rg.get("RegionNameTh") or _rg.get("region") or
                          _rg.get("Name") or "ภาค")
                _rel_lines = _REGION_LINES.get(_rname, [])
                _rel_txt = " · ".join([
                    f"{SRT_LINES[l]['icon']} {l}" for l in _rel_lines if l in SRT_LINES
                ]) if _rel_lines else ""

                with st.expander(
                    f"🌏 {_rname}" + (f"  →  {_rel_txt}" if _rel_txt else ""),
                    expanded=False
                ):
                    _fdays = (_rg.get("Forecasts") or _rg.get("days") or
                              _rg.get("DailyForecasts") or [])
                    if _fdays:
                        _fd_rows = [{
                            "วันที่":            d.get("ForecastDate") or d.get("date",""),
                            "สภาพอากาศ":         d.get("Condition") or d.get("Weather") or "",
                            "โอกาสฝน (%)":       d.get("RainPercent") or d.get("rain",""),
                            "สูงสุด (°C)":       d.get("MaxTemp") or d.get("max_temp",""),
                            "ต่ำสุด (°C)":       d.get("MinTemp") or d.get("min_temp",""),
                            "ความชื้น (%)":       d.get("Humidity") or d.get("rh",""),
                        } for d in _fdays[:7]]
                        _fdf = pd.DataFrame(_fd_rows)
                        st.dataframe(_fdf, use_container_width=True,
                                     hide_index=True,
                                     column_config={
                                         "โอกาสฝน (%)": st.column_config.ProgressColumn(
                                             "🌧️ โอกาสฝน", min_value=0, max_value=100, format="%d%%"
                                         ) if all(_fd_rows[i].get("โอกาสฝน (%)") for i in range(len(_fd_rows))) else st.column_config.TextColumn(),
                                     })
                    else:
                        with st.expander("ข้อมูลดิบ"):
                            st.json({k:v for k,v in _rg.items()
                                     if k not in ("Forecasts","days","DailyForecasts")})
        else:
            st.info("ไม่พบข้อมูลพยากรณ์รายภาค — ตรวจสอบ TMD API Token")
    else:
        st.markdown("""
        <div class='alert-card alert-info'>
            <div class='alert-card-title'>ℹ️ ยังไม่ได้รับข้อมูลพยากรณ์อากาศ</div>
            <div class='alert-card-body'>
                ต้องการ TMD API Token ที่ถูกต้องเพื่อแสดงพยากรณ์ 7 วัน<br>
                รับ Token ได้ที่: data.tmd.go.th/api/index1.php
            </div>
        </div>""", unsafe_allow_html=True)

    # ── 7-day water forecast (คาดการณ์น้ำ) ────────────────
    st.markdown('<div class="sec-title-water">💧 แนวโน้มระดับน้ำ 7 วัน (ประมาณการ)</div>',
                unsafe_allow_html=True)

    # Generate indicative trends based on forecast + current water data
    _trend_rivers = ["เจ้าพระยา","ปิง","วัง","น่าน","มูล","ชี","บางปะกง"]
    _trend_cols = st.columns(min(len(_trend_rivers), 4))
    for _i, _rv_name in enumerate(_trend_rivers[:4]):
        _rv_stn = next((r for r in RIVER_STATIONS_NEAR_RAIL if r["river"] == _rv_name), None)
        _cur_wl = None
        if _rv_stn:
            _cur_wl = next(
                (w["water_level"] for w in _water_list
                 if _rv_stn["id"] in w["id"] or _rv_name in w["name"]), None
            )
        with _trend_cols[_i % 4]:
            st.markdown(f"""
            <div class='dash-box water' style='padding:14px 16px;'>
                <div style='color:#06b6d4;font-size:0.74rem;font-weight:700;
                    text-transform:uppercase;letter-spacing:0.8px;margin-bottom:8px;'>
                    🌊 แม่น้ำ{_rv_name}
                </div>
                <div style='color:{"#e0f4ff" if _cur_wl else "#2a4060"};
                    font-size:{"1.2rem" if _cur_wl else "0.8rem"};font-weight:700;'>
                    {f"{_cur_wl:.2f} ม." if _cur_wl else "รอข้อมูล"}
                </div>
                <div style='color:#2a4060;font-size:0.7rem;margin-top:6px;'>
                    สาย: {_rv_stn["line"] if _rv_stn else "—"}
                </div>
            </div>""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════╗
# ║  TAB 7 — SEISMIC                                        ║
# ╚══════════════════════════════════════════════════════════╝
with tab_seismic:
    st.markdown('<div class="sec-title">🌋 เหตุการณ์แผ่นดินไหว</div>', unsafe_allow_html=True)

    _sa, _sb = st.columns([1.6, 1])

    with _sa:
        _eqlist = []
        if _seismic:
            for k in ["SeismicEvents","events","data","Earthquakes","items","EQInfo"]:
                if k in _seismic and isinstance(_seismic[k], list):
                    _eqlist = _seismic[k]; break

        if _eqlist:
            for eq in _eqlist[:10]:
                _mag  = _fnum(eq, "Magnitude","mag","M","Richter")
                _loc  = str(eq.get("Location") or eq.get("location") or eq.get("Area") or "ไม่ระบุ")
                _dep  = _fnum(eq, "Depth","depth","FocalDepth")
                _edt  = str(eq.get("OriginTime") or eq.get("Date") or eq.get("datetime") or "")
                _lat  = _fnum(eq, "Lat","lat","Latitude")
                _lon  = _fnum(eq, "Lon","lon","Longitude")
                _mf   = _mag or 0

                # Nearest rail line
                _near_line = None
                if _lat and _lon:
                    _min_d = 9999.0
                    for _s in ALL_STATIONS:
                        _d = haversine(_lat, _lon, _s["lat"], _s["lon"])
                        if _d < _min_d:
                            _min_d = _d
                            _near_line = {"station": _s["name"], "line": _s["line"],
                                          "dist": round(_d,1)}

                _ec = ("alert-critical" if _mf >= 5.0 else
                       "alert-warning"  if _mf >= 3.5 else "alert-info")
                _mcolor = ("#ef4444" if _mf >= 5.0 else
                           "#f59e0b" if _mf >= 3.5 else "#3b82f6")
                _impact = ("⚠️ อาจมีผลต่อโครงสร้าง" if _mf >= 5.0 else
                           "ติดตามอย่างใกล้ชิด"     if _mf >= 3.5 else "ผลกระทบน้อย")

                st.markdown(f"""
                <div class='alert-card {_ec}'>
                    <div style='display:flex;justify-content:space-between;align-items:start;'>
                        <div style='flex:1;'>
                            <div class='alert-card-title'>
                                🌋 M {_mag:.1f if _mag else "?"} — {_loc[:50]}
                            </div>
                            <div class='alert-card-body'>
                                {f"🕐 {_edt[:19]}" if _edt else ""}
                                {f" · 🔽 ความลึก {_dep:.0f} กม." if _dep else ""}
                                {f"<br>🚆 ใกล้: {_near_line['station']} ({_near_line['dist']} km) · {_near_line['line']}" if _near_line and _near_line['dist'] < 200 else ""}
                            </div>
                            <div class='alert-card-meta'>{_impact}</div>
                        </div>
                        <div style='text-align:right;min-width:55px;'>
                            <div style='color:{_mcolor};font-size:1.5rem;font-weight:900;
                                text-shadow:0 0 12px {_mcolor}50;'>
                                {f"{_mag:.1f}" if _mag else "?"}
                            </div>
                            <div style='color:#2a4060;font-size:0.68rem;'>ริกเตอร์</div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='alert-card alert-ok'>
                <div class='alert-card-title'>✅ ไม่มีเหตุการณ์แผ่นดินไหวที่รายงาน</div>
                <div class='alert-card-body'>
                    ไม่พบข้อมูลจาก TMD DailySeismicEvent API<br>
                    หรืออยู่ในช่วงที่ไม่มีกิจกรรมแผ่นดินไหว
                </div>
            </div>""", unsafe_allow_html=True)

    with _sb:
        st.markdown("""
        <div class='dash-box'>
            <h4>📋 มาตรฐานความเสี่ยงรางรถไฟ</h4>
        """, unsafe_allow_html=True)
        for _ms, _ml, _mi, _cc in [
            ("< 3.5","ผลกระทบน้อย","✅","#10b981"),
            ("3.5 – 4.9","ติดตามอย่างใกล้ชิด","⚠️","#f59e0b"),
            ("5.0 – 5.9","ตรวจสอบโครงสร้าง","🚨","#ef4444"),
            ("≥ 6.0","หยุดการเดินรถทันที","🛑","#ef4444"),
        ]:
            st.markdown(f"""
            <div style='display:flex;align-items:center;gap:10px;
                padding:8px 10px;margin:4px 0;
                background:rgba(255,255,255,0.02);border-radius:8px;
                border:1px solid rgba(255,255,255,0.04);'>
                <span style='font-size:1.1rem;'>{_mi}</span>
                <div style='flex:1;'>
                    <div style='color:{_cc};font-size:0.78rem;font-weight:700;'>M {_ms}</div>
                    <div style='color:#3a5570;font-size:0.72rem;'>{_ml}</div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style='margin-top:16px;padding-top:12px;
            border-top:1px solid rgba(91,200,255,0.08);'>
            <div style='color:#2a4060;font-size:0.72rem;line-height:1.9;'>
                <b style='color:#3a5570;'>พื้นที่เสี่ยงแผ่นดินไหวใกล้รางรถไฟ:</b><br>
                🔴 ภาคเหนือ (เชียงราย–เชียงใหม่)<br>
                🟡 ภาคตะวันตก (กาญจนบุรี)<br>
                🟢 ภาคใต้ตอนบน (สุราษฎร์ธานี)
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style='margin-top:14px;background:rgba(239,68,68,0.05);
            border:1px solid rgba(239,68,68,0.15);border-radius:10px;padding:12px 14px;'>
            <div style='color:#fca5a5;font-size:0.76rem;font-weight:700;margin-bottom:6px;'>
                🚨 ขั้นตอนฉุกเฉินแผ่นดินไหว
            </div>
            <div style='color:#7a3030;font-size:0.72rem;line-height:1.8;'>
                1. หยุดขบวนรถทันที<br>
                2. ตรวจสอบโครงสร้างราง<br>
                3. รายงาน SRT ศูนย์ควบคุม<br>
                4. รอผลประเมินจากวิศวกร
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
