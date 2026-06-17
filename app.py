"""
🚆 ระบบแจ้งเตือนสภาพอากาศโครงข่ายรถไฟไทย
Thai Railway Network Weather & Disaster Alert System
การรถไฟแห่งประเทศไทย × กรมอุตุนิยมวิทยา
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
#  PAGE CONFIG  (ต้องเรียกก่อน st อื่น ๆ ทุกกรณี)
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="SRT Weather Alert · ระบบแจ้งเตือนรถไฟ",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://data.tmd.go.th/api/index1.php",
        "About": "ระบบแจ้งเตือนสภาพอากาศโครงข่ายรถไฟไทย v2.0 — ข้อมูลจาก TMD & SRT",
    },
)

TZ_TH = pytz.timezone("Asia/Bangkok")

# ══════════════════════════════════════════════════════════════
#  THEME & CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:ital,wght@0,300;0,400;0,600;0,700;0,800;1,400&display=swap');

/* ── Global ── */
html, body, [class*="css"], * {
    font-family: 'Sarabun', 'Segoe UI', sans-serif !important;
}
.stApp {
    background: #0b1622;
    background-image:
        repeating-linear-gradient(90deg, transparent, transparent 59px, rgba(255,255,255,0.015) 59px, rgba(255,255,255,0.015) 60px),
        linear-gradient(180deg, #0b1622 0%, #0d1f33 60%, #0b1622 100%);
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060e18 0%, #0a1825 100%) !important;
    border-right: 2px solid #1a3a5c !important;
}
[data-testid="stSidebar"] * { color: #a8cce0 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #5bc8ff !important; }

/* ── Rail track decoration (sidebar bottom) ── */
[data-testid="stSidebar"]::after {
    content: '';
    position: fixed; bottom: 0; left: 0; width: 280px; height: 8px;
    background: repeating-linear-gradient(90deg, #c8a84b 0, #c8a84b 20px, transparent 20px, transparent 30px);
    opacity: 0.4;
}

/* ── Header banner ── */
.rail-header {
    background: linear-gradient(135deg, #0d2137 0%, #0a3060 40%, #0d2137 100%);
    border: 1px solid #1a4a7a;
    border-left: 6px solid #c8a84b;
    border-radius: 0 12px 12px 0;
    padding: 20px 28px;
    margin-bottom: 20px;
    position: relative;
    overflow: hidden;
}
.rail-header::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 3px;
    background: repeating-linear-gradient(90deg, #c8a84b 0, #c8a84b 24px, transparent 24px, transparent 32px);
}
.rail-header::after {
    content: '';
    position: absolute; bottom: 0; left: 0; right: 0; height: 3px;
    background: repeating-linear-gradient(90deg, #c8a84b 0, #c8a84b 24px, transparent 24px, transparent 32px);
}
.rail-header h1 {
    color: #fff !important;
    font-size: 1.8rem !important;
    font-weight: 800 !important;
    margin: 0 0 4px 0 !important;
    text-shadow: 0 2px 12px rgba(91,200,255,0.3);
}
.rail-header p {
    color: #7ec8e3 !important;
    font-size: 0.88rem !important;
    margin: 0 !important;
}
.rail-header .stamp {
    position: absolute; right: 24px; top: 50%; transform: translateY(-50%);
    color: rgba(200,168,75,0.15);
    font-size: 6rem;
    font-weight: 900;
    line-height: 1;
    user-select: none;
}

/* ── KPI Cards ── */
.kpi-grid { display: flex; gap: 12px; flex-wrap: wrap; margin-bottom: 16px; }
.kpi-card {
    flex: 1; min-width: 140px;
    background: linear-gradient(135deg, rgba(13,33,55,0.95), rgba(8,24,44,0.95));
    border: 1px solid #1a3a5c;
    border-top: 3px solid var(--accent, #5bc8ff);
    border-radius: 10px;
    padding: 16px 18px;
    position: relative;
    transition: box-shadow 0.2s;
}
.kpi-card:hover { box-shadow: 0 4px 20px rgba(91,200,255,0.15); }
.kpi-card .kpi-icon { font-size: 1.5rem; margin-bottom: 6px; display: block; }
.kpi-card .kpi-label { color: #6899b8; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 4px; }
.kpi-card .kpi-value { color: #fff; font-size: 1.7rem; font-weight: 800; line-height: 1; }
.kpi-card .kpi-sub   { color: #7ec8e3; font-size: 0.75rem; margin-top: 4px; }
.kpi-red    { --accent: #ef4444; }
.kpi-orange { --accent: #f59e0b; }
.kpi-blue   { --accent: #3b82f6; }
.kpi-green  { --accent: #10b981; }
.kpi-gold   { --accent: #c8a84b; }
.kpi-purple { --accent: #a78bfa; }

/* ── Alert cards ── */
.alert-card {
    border-radius: 10px; padding: 14px 18px; margin: 6px 0;
    border-left: 4px solid;
    position: relative;
}
.alert-critical { background: rgba(220,38,38,0.12); border-color: #ef4444; border: 1px solid rgba(220,38,38,0.35); border-left: 4px solid #ef4444; }
.alert-warning  { background: rgba(245,158,11,0.10); border-color: #f59e0b; border: 1px solid rgba(245,158,11,0.35); border-left: 4px solid #f59e0b; }
.alert-info     { background: rgba(59,130,246,0.10); border-color: #3b82f6; border: 1px solid rgba(59,130,246,0.30); border-left: 4px solid #3b82f6; }
.alert-ok       { background: rgba(16,185,129,0.08); border-color: #10b981; border: 1px solid rgba(16,185,129,0.25); border-left: 4px solid #10b981; }
.alert-card-title { color: #fff; font-weight: 700; font-size: 0.95rem; margin: 0 0 4px 0; }
.alert-card-body  { color: #a8cce0; font-size: 0.84rem; margin: 0; line-height: 1.5; }
.alert-card-meta  { color: #5a8099; font-size: 0.75rem; margin-top: 6px; }

/* ── Section title ── */
.sec-title {
    color: #5bc8ff;
    font-size: 1.0rem; font-weight: 700;
    border-bottom: 1px solid rgba(91,200,255,0.2);
    padding-bottom: 7px;
    margin: 18px 0 10px 0;
    display: flex; align-items: center; gap: 8px;
}

/* ── Risk badge ── */
.badge { display: inline-block; padding: 2px 9px; border-radius: 12px; font-size: 0.72rem; font-weight: 700; }
.badge-critical { background: #7f1d1d; color: #fca5a5; border: 1px solid #ef4444; }
.badge-high     { background: #78350f; color: #fde68a; border: 1px solid #f59e0b; }
.badge-medium   { background: #1e3a5f; color: #93c5fd; border: 1px solid #3b82f6; }
.badge-low      { background: #064e3b; color: #6ee7b7; border: 1px solid #10b981; }
.badge-na       { background: #1e2a35; color: #6899b8;  border: 1px solid #2a4a62; }

/* ── Station row ── */
.stn-row {
    display: grid; grid-template-columns: 2fr 1.2fr 1fr 1fr 1fr;
    align-items: center; gap: 8px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(91,200,255,0.08);
    border-radius: 8px; padding: 9px 14px; margin: 3px 0;
    transition: background 0.15s;
}
.stn-row:hover { background: rgba(91,200,255,0.06); }
.stn-name { color: #d0e8f8; font-weight: 600; font-size: 0.88rem; }
.stn-prov { color: #5a8099; font-size: 0.76rem; }
.stn-val  { color: #e0f4ff; font-size: 0.88rem; text-align: right; }

/* ── Progress bar ── */
.prog-wrap { background: rgba(255,255,255,0.06); border-radius: 6px; height: 7px; overflow: hidden; margin-top: 3px; }
.prog-fill  { height: 100%; border-radius: 6px; transition: width 0.4s; }

/* ── Metric override ── */
div[data-testid="stMetric"] {
    background: rgba(13,33,55,0.8) !important;
    border: 1px solid rgba(91,200,255,0.15) !important;
    border-radius: 10px !important;
    padding: 14px 16px !important;
}
div[data-testid="stMetric"] label { color: #6899b8 !important; font-size: 0.77rem !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #fff !important; font-weight: 700 !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(13,33,55,0.6) !important;
    border-radius: 10px !important;
    gap: 4px !important;
    padding: 4px !important;
    border: 1px solid rgba(91,200,255,0.1) !important;
}
.stTabs [data-baseweb="tab"] { color: #6899b8 !important; border-radius: 7px !important; padding: 6px 18px !important; }
.stTabs [aria-selected="true"] { background: rgba(91,200,255,0.15) !important; color: #5bc8ff !important; }

/* ── Expander ── */
div[data-testid="stExpander"] {
    background: rgba(13,33,55,0.5) !important;
    border: 1px solid rgba(91,200,255,0.12) !important;
    border-radius: 10px !important;
}
div[data-testid="stExpander"] summary { color: #7ec8e3 !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #0a3060, #0d4080) !important;
    color: #d0e8f8 !important;
    border: 1px solid rgba(91,200,255,0.3) !important;
    border-radius: 8px !important; font-weight: 600 !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #0d4080, #1055a0) !important;
    box-shadow: 0 0 14px rgba(91,200,255,0.25) !important;
}

/* ── Selectbox / Input ── */
div[data-baseweb="select"] > div { background: rgba(10,25,45,0.8) !important; border-color: rgba(91,200,255,0.2) !important; }
div[data-baseweb="select"] * { color: #a8cce0 !important; }

/* ── Dataframe / Table ── */
.stDataFrame { border-radius: 8px !important; overflow: hidden !important; }
iframe[title="st.dataframe"] { background: transparent !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #060e18; }
::-webkit-scrollbar-thumb { background: #1a3a5c; border-radius: 3px; }

/* ── Status dot ── */
.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.dot-green  { background: #10b981; box-shadow: 0 0 6px #10b981; }
.dot-red    { background: #ef4444; box-shadow: 0 0 6px #ef4444; }
.dot-yellow { background: #f59e0b; box-shadow: 0 0 6px #f59e0b; }
.dot-grey   { background: #4a6070; }

/* ── Dashboard summary box ── */
.dash-box {
    background: linear-gradient(135deg, rgba(13,33,55,0.9), rgba(8,20,38,0.95));
    border: 1px solid rgba(91,200,255,0.15);
    border-radius: 12px;
    padding: 18px 22px;
    height: 100%;
}
.dash-box h4 { color: #5bc8ff; font-size: 0.82rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; margin: 0 0 12px 0; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  CONSTANTS & TOKEN SETUP
# ══════════════════════════════════════════════════════════════
TMD_BASE = "http://data.tmd.go.th/api"

def _decode_jwt_payload(token: str) -> dict:
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload))
    except Exception:
        return {}

# Load token
try:
    _raw_token = st.secrets.get("TMD_TOKEN", "") or st.secrets.get("tmd_token", "")
except Exception:
    _raw_token = ""

if not _raw_token:
    import os
    _raw_token = os.environ.get("TMD_TOKEN", "")

TMD_TOKEN: str = _raw_token
_jwt_data = _decode_jwt_payload(TMD_TOKEN)
TMD_UID   = str(_jwt_data.get("sub", ""))
TMD_UKEY  = TMD_TOKEN

# ══════════════════════════════════════════════════════════════
#  SRT RAILWAY NETWORK DATA  (การรถไฟแห่งประเทศไทย)
#  Source: datagov.mot.go.th/en/dataset/after16  (2026)
# ══════════════════════════════════════════════════════════════
SRT_LINES = {
    "สายเหนือ": {
        "color": "#ef4444", "short": "N", "icon": "🔴",
        "desc": "กรุงเทพ → เชียงใหม่ | 751 กม.",
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

# Flatten all unique stations (dedup by name)
_seen: set = set()
ALL_STATIONS: list = []
for _line, _ldata in SRT_LINES.items():
    for _s in _ldata["stations"]:
        _key = _s["name"]
        if _key not in _seen:
            _seen.add(_key)
            ALL_STATIONS.append({**_s, "line": _line, "line_color": _ldata["color"],
                                  "line_short": _ldata["short"], "line_icon": _ldata["icon"]})

# ══════════════════════════════════════════════════════════════
#  API HELPERS — robust fetch with retry & timeout
# ══════════════════════════════════════════════════════════════
_SESSION = requests.Session()
_SESSION.headers.update({"Accept": "application/json", "Connection": "close"})

def _tmd_fetch(endpoint: str, extra: dict | None = None, retries: int = 2) -> dict | None:
    """GET a TMD API endpoint; return parsed JSON or None."""
    if not TMD_UID or not TMD_UKEY:
        return None
    params = {"uid": TMD_UID, "ukey": TMD_UKEY, "format": "json"}
    if extra:
        params.update(extra)
    url = f"{TMD_BASE}/{endpoint}"
    for attempt in range(retries):
        try:
            r = _SESSION.get(url, params=params, timeout=12, allow_redirects=True)
            if r.status_code == 200:
                data = r.json()
                # TMD wraps some errors as 200
                if isinstance(data, dict):
                    err = data.get("error") or data.get("Error") or data.get("STATUS")
                    if err and str(err).lower() not in ("0", "ok", "success", ""):
                        return None
                return data
        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                time.sleep(1)
        except Exception:
            break
    return None


@st.cache_data(ttl=900, show_spinner=False)
def get_weather_today() -> dict | None:
    return _tmd_fetch("WeatherToday/V2/")

@st.cache_data(ttl=900, show_spinner=False)
def get_weather_3h() -> dict | None:
    return _tmd_fetch("Weather3Hours/V2/")

@st.cache_data(ttl=1800, show_spinner=False)
def get_warning() -> dict | None:
    return _tmd_fetch("WeatherWarningNews/V1/")

@st.cache_data(ttl=3600, show_spinner=False)
def get_forecast_region() -> dict | None:
    return _tmd_fetch("WeatherForecast7DaysByRegion/V1/")

@st.cache_data(ttl=3600, show_spinner=False)
def get_seismic() -> dict | None:
    return _tmd_fetch("DailySeismicEvent/V1/")

# ── Utility: find nearest TMD station ────────────────────────
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
    for k in ["Stations", "stations", "Data", "data", "Items", "items"]:
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
    if not obs:
        return None
    return _fnum(obs, "Rain","rain","Rainfall","rainfall","RainfallToday",
                 "Rain24h","Precip","precip","TotalRain","RainAcc")

def get_temp(obs: dict | None) -> float | None:
    if not obs:
        return None
    return _fnum(obs, "Temp","temp","Temperature","temperature","AirTemp","MaxTemp")

def get_wind(obs: dict | None) -> float | None:
    if not obs:
        return None
    return _fnum(obs, "WindSpeed","windspeed","Wind","wind","WindSpd","MaxWindSpeed")

def get_rh(obs: dict | None) -> float | None:
    if not obs:
        return None
    return _fnum(obs, "Humidity","humidity","RH","rh","RelativeHumidity")

# ── Risk classification ───────────────────────────────────────
def risk_class(rain_mm: float | None) -> tuple[str, str, str, str]:
    """Returns (label_th, emoji, badge_class, alert_class)"""
    if rain_mm is None:
        return "ไม่มีข้อมูล", "⚪", "badge-na", "alert-info"
    if rain_mm == 0:
        return "ปกติ", "☀️", "badge-low", "alert-ok"
    if rain_mm < 10:
        return "ฝนเล็กน้อย", "🌦️", "badge-low", "alert-ok"
    if rain_mm < 35:
        return "ฝนปานกลาง", "🌧️", "badge-medium", "alert-info"
    if rain_mm < 90:
        return "ฝนหนัก ⚠️", "⛈️", "badge-high", "alert-warning"
    return "ฝนหนักมาก 🚨", "🌊", "badge-critical", "alert-critical"

def risk_color_hex(rain_mm: float | None) -> str:
    if rain_mm is None: return "#4a6070"
    if rain_mm < 10:    return "#10b981"
    if rain_mm < 35:    return "#3b82f6"
    if rain_mm < 90:    return "#f59e0b"
    return "#ef4444"

# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:16px 0 20px;'>
        <div style='font-size:3rem;'>🚆</div>
        <div style='color:#5bc8ff;font-size:1.05rem;font-weight:800;letter-spacing:0.5px;'>SRT Weather Alert</div>
        <div style='color:#4a7090;font-size:0.74rem;margin-top:2px;'>ระบบแจ้งเตือนสภาพอากาศ</div>
        <div style='color:#4a7090;font-size:0.74rem;'>โครงข่ายรถไฟแห่งประเทศไทย</div>
    </div>
    """, unsafe_allow_html=True)

    # API Token status
    if TMD_TOKEN:
        exp_ts = _jwt_data.get("exp", 0)
        exp_dt = datetime.fromtimestamp(exp_ts, tz=TZ_TH) if exp_ts else None
        days_left = (exp_dt - datetime.now(TZ_TH)).days if exp_dt else 0
        status_color = "#10b981" if days_left > 30 else "#f59e0b" if days_left > 0 else "#ef4444"
        st.markdown(f"""
        <div style='background:rgba(10,20,35,0.8);border:1px solid rgba(91,200,255,0.15);border-radius:8px;padding:10px 14px;margin-bottom:12px;'>
            <div style='color:#4a7090;font-size:0.72rem;'>🔑 API Token</div>
            <div style='color:#5bc8ff;font-size:0.82rem;font-weight:600;'>uid: <b style="color:#fff;">{TMD_UID}</b></div>
            <div style='color:{status_color};font-size:0.75rem;margin-top:2px;'>
                {'✅ ใช้งานได้' if days_left > 0 else '❌ หมดอายุแล้ว'} · {'หมดใน ' + str(days_left) + ' วัน' if days_left > 0 else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        token_in = st.text_input("🔑 TMD API Token", type="password",
                                  placeholder="eyJ0eXAiOiJKV1Qi...",
                                  help="ใส่ JWT token จาก data.tmd.go.th")
        if token_in:
            TMD_TOKEN = TMD_UKEY = token_in
            _d = _decode_jwt_payload(token_in)
            TMD_UID = str(_d.get("sub", ""))
            st.success(f"✅ uid={TMD_UID}")

    st.markdown("---")

    # Line filter
    st.markdown("<div style='color:#5bc8ff;font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;'>🛤️ เส้นทาง</div>", unsafe_allow_html=True)
    line_opts = ["ทุกสาย"] + list(SRT_LINES.keys())
    sel_line = st.selectbox("เลือกสาย", line_opts, label_visibility="collapsed")

    st.markdown("<div style='color:#5bc8ff;font-size:0.78rem;font-weight:700;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:6px;margin-top:10px;'>⚠️ แสดงตั้งแต่ระดับ</div>", unsafe_allow_html=True)
    alert_thresh = st.select_slider("ระดับ", ["ทั้งหมด","ฝนเล็กน้อย","ฝนปานกลาง","ฝนหนัก","ฝนหนักมาก"],
                                    value="ทั้งหมด", label_visibility="collapsed")

    st.markdown("---")
    now_th = datetime.now(TZ_TH)
    st.markdown(f"""
    <div style='color:#4a7090;font-size:0.75rem;line-height:1.8;'>
        🕐 เวลาไทย<br>
        <span style='color:#5bc8ff;font-size:0.95rem;font-weight:700;'>
            {now_th.strftime('%d %b %Y %H:%M')} น.
        </span><br>
        <span style='color:#2a5070;'>อัพเดตทุก 15–30 นาที</span>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🔄 รีเฟรชข้อมูล", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    # Line legend
    for ln, ld in SRT_LINES.items():
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:8px;margin:3px 0;'>
            <div style='width:28px;height:4px;border-radius:2px;background:{ld["color"]};'></div>
            <span style='color:#6899b8;font-size:0.76rem;'>{ld["short"]} {ln}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style='color:#2a4060;font-size:0.69rem;margin-top:16px;line-height:1.7;'>
        ข้อมูลอุตุฯ: กรมอุตุนิยมวิทยา<br>
        โครงข่าย: การรถไฟแห่งประเทศไทย<br>
        แหล่งข้อมูล: datagov.mot.go.th<br>
        v2.0 · June 2026
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  LOAD DATA
# ══════════════════════════════════════════════════════════════
with st.spinner("⏳ กำลังโหลดข้อมูลสภาพอากาศ..."):
    _obs_today  = get_weather_today()
    _obs_3h     = get_weather_3h()
    _warning    = get_warning()
    _forecast   = get_forecast_region()
    _seismic    = get_seismic()

_obs_list = extract_stations_list(_obs_today) or extract_stations_list(_obs_3h)
_api_ok   = bool(_obs_list)

# ── Enrich each station with nearest weather obs ─────────────
_station_weather: list[dict] = []
for _s in ALL_STATIONS:
    if sel_line != "ทุกสาย" and _s["line"] != sel_line:
        continue
    _obs = nearest_obs(_s, _obs_list)
    _rain = get_rain(_obs)
    _temp = get_temp(_obs)
    _wind = get_wind(_obs)
    _rh   = get_rh(_obs)
    _lbl, _em, _bc, _ac = risk_class(_rain)
    _station_weather.append({
        **_s,
        "obs": _obs,
        "rain_mm": _rain,
        "temp_c":  _temp,
        "wind_ms": _wind,
        "rh_pct":  _rh,
        "risk_label": _lbl,
        "risk_emoji": _em,
        "badge_cls": _bc,
        "alert_cls": _ac,
        "tmd_name": (_obs.get("StationNameTh") or _obs.get("StationName") or "") if _obs else "",
        "tmd_km": _obs.get("_km","?") if _obs else "?",
    })

_THRESH_MM = {"ทั้งหมด":0,"ฝนเล็กน้อย":1,"ฝนปานกลาง":10,"ฝนหนัก":35,"ฝนหนักมาก":90}
_t_mm = _THRESH_MM.get(alert_thresh, 0)

# Aggregates
_all_rain  = [s["rain_mm"] for s in _station_weather if s["rain_mm"] is not None]
_all_temp  = [s["temp_c"]  for s in _station_weather if s["temp_c"]  is not None]
_n_critical= sum(1 for s in _station_weather if (s["rain_mm"] or 0) >= 90)
_n_heavy   = sum(1 for s in _station_weather if 35 <= (s["rain_mm"] or 0) < 90)
_n_medium  = sum(1 for s in _station_weather if 10 <= (s["rain_mm"] or 0) < 35)
_n_ok      = sum(1 for s in _station_weather if (s["rain_mm"] or 0) < 10)
_max_rain  = max(_all_rain) if _all_rain else None
_avg_temp  = round(sum(_all_temp)/len(_all_temp), 1) if _all_temp else None

# ══════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class='rail-header'>
    <div class='stamp'>🚂</div>
    <h1>🚆 ระบบแจ้งเตือนสภาพอากาศโครงข่ายรถไฟไทย</h1>
    <p>Thai Railway Network Weather & Disaster Alert System
    · การรถไฟแห่งประเทศไทย (SRT) × กรมอุตุนิยมวิทยา (TMD)
    · อัพเดต {now_th.strftime('%d %b %Y %H:%M')} น.</p>
</div>
""", unsafe_allow_html=True)

# API status bar
dot = '<span class="dot dot-green"></span>' if _api_ok else '<span class="dot dot-red"></span>'
st.markdown(f"""
<div style='display:flex;align-items:center;gap:20px;background:rgba(10,20,35,0.7);
    border:1px solid rgba(91,200,255,0.1);border-radius:8px;padding:8px 18px;margin-bottom:16px;flex-wrap:wrap;'>
    <span style='font-size:0.8rem;color:#6899b8;'>{dot}
        <b style='color:{"#10b981" if _api_ok else "#ef4444"};'>
        {"✅ API เชื่อมต่อสำเร็จ" if _api_ok else "❌ API ไม่ตอบสนอง"}</b>
        {" · สถานีอุตุฯ " + str(len(_obs_list)) + " สถานี" if _api_ok else " — ตรวจสอบ Token และการเชื่อมต่อ"}
    </span>
    <span style='font-size:0.8rem;color:#6899b8;'>🛤️ สาย: <b style='color:#a8cce0;'>{sel_line}</b></span>
    <span style='font-size:0.8rem;color:#6899b8;'>📍 สถานีรถไฟ: <b style='color:#a8cce0;'>{len(_station_weather)}</b> สถานี</span>
    <span style='font-size:0.8rem;color:#6899b8;'>⚠️ เกณฑ์: <b style='color:#a8cce0;'>{alert_thresh}</b></span>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  MAIN TABS
# ══════════════════════════════════════════════════════════════
tab_exec, tab_map, tab_alert, tab_line, tab_forecast = st.tabs([
    "📊 Executive Dashboard",
    "🗺️ แผนที่",
    "⚠️ แจ้งเตือนภัย",
    "🛤️ รายสาย",
    "🌤️ พยากรณ์",
])

# ╔══════════════════════════════════════════════════════════╗
# ║  TAB 1 — EXECUTIVE DASHBOARD                            ║
# ╚══════════════════════════════════════════════════════════╝
with tab_exec:
    # ── KPI Row ──────────────────────────────────────────────
    kc = st.columns(6)
    kpi_data = [
        ("🚨","ฝนหนักมาก",str(_n_critical),"สถานี","kpi-red"),
        ("⛈️","ฝนหนัก",str(_n_heavy),"สถานี","kpi-orange"),
        ("🌧️","ฝนปานกลาง",str(_n_medium),"สถานี","kpi-blue"),
        ("☀️","ปกติ/เล็กน้อย",str(_n_ok),"สถานี","kpi-green"),
        ("💧","ฝนสูงสุด",f"{_max_rain:.1f}" if _max_rain is not None else "N/A","mm","kpi-gold"),
        ("🌡️","อุณหภูมิเฉลี่ย",f"{_avg_temp}" if _avg_temp is not None else "N/A","°C","kpi-purple"),
    ]
    for col, (icon, label, val, unit, cls) in zip(kc, kpi_data):
        with col:
            st.markdown(f"""
            <div class='kpi-card {cls}'>
                <span class='kpi-icon'>{icon}</span>
                <div class='kpi-label'>{label}</div>
                <div class='kpi-value'>{val}<span style='font-size:0.85rem;color:#7ec8e3;margin-left:3px;'>{unit}</span></div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("")

    # ── Row 2: Risk Summary + Bar Chart + Top Risk ────────────
    c1, c2, c3 = st.columns([1.2, 1.8, 1.8])

    with c1:
        st.markdown('<div class="dash-box"><h4>🎯 สรุปความเสี่ยงเส้นทาง</h4>', unsafe_allow_html=True)
        total = max(len(_station_weather), 1)
        levels = [
            ("🚨 ฝนหนักมาก", _n_critical, "#ef4444"),
            ("⛈️ ฝนหนัก",   _n_heavy,    "#f59e0b"),
            ("🌧️ ฝนปานกลาง",_n_medium,   "#3b82f6"),
            ("☀️ ปกติ",      _n_ok,       "#10b981"),
        ]
        for lbl, cnt, col in levels:
            pct = cnt / total * 100
            st.markdown(f"""
            <div style='margin:7px 0;'>
                <div style='display:flex;justify-content:space-between;margin-bottom:3px;'>
                    <span style='color:#a8cce0;font-size:0.8rem;'>{lbl}</span>
                    <span style='color:#fff;font-size:0.8rem;font-weight:700;'>{cnt}</span>
                </div>
                <div class='prog-wrap'>
                    <div class='prog-fill' style='width:{pct:.1f}%;background:{col};'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Overall risk indicator
        if _n_critical > 0:
            ov_color, ov_label = "#ef4444", "🚨 วิกฤต"
        elif _n_heavy > 0:
            ov_color, ov_label = "#f59e0b", "⚠️ ต้องระวัง"
        elif _n_medium > 0:
            ov_color, ov_label = "#3b82f6", "ℹ️ เฝ้าระวัง"
        else:
            ov_color, ov_label = "#10b981", "✅ ปกติ"

        st.markdown(f"""
        <div style='margin-top:14px;background:rgba(0,0,0,0.3);border:1px solid {ov_color};border-radius:8px;padding:10px 14px;text-align:center;'>
            <div style='color:#6899b8;font-size:0.72rem;font-weight:600;text-transform:uppercase;'>ภาพรวมความเสี่ยง</div>
            <div style='color:{ov_color};font-size:1.3rem;font-weight:800;margin-top:3px;'>{ov_label}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown('<div class="dash-box"><h4>🌧️ ปริมาณฝนแยกตามสาย (mm)</h4>', unsafe_allow_html=True)
        # Bar chart per line using HTML/CSS
        _line_stats: dict[str, dict] = {}
        for _s in _station_weather:
            _ln = _s["line"]
            if _ln not in _line_stats:
                _line_stats[_ln] = {"vals": [], "color": _s["line_color"], "icon": _s["line_icon"]}
            if _s["rain_mm"] is not None:
                _line_stats[_ln]["vals"].append(_s["rain_mm"])

        _max_bar = max(
            (max(v["vals"]) for v in _line_stats.values() if v["vals"]),
            default=100
        ) or 100
        _max_bar = max(_max_bar, 10)

        for _ln_name, _ld in _line_stats.items():
            _vals = _ld["vals"]
            _avg  = round(sum(_vals)/len(_vals), 1) if _vals else None
            _mx   = round(max(_vals), 1) if _vals else None
            _bar_w = (_mx / _max_bar * 100) if _mx else 0
            _bar_col = risk_color_hex(_mx)
            st.markdown(f"""
            <div style='margin:6px 0;'>
                <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;'>
                    <span style='color:#a8cce0;font-size:0.78rem;'>
                        <span style='color:{_ld["color"]};'>●</span> {_ln_name}
                    </span>
                    <span style='color:#fff;font-size:0.78rem;'>
                        สูงสุด <b>{_mx if _mx is not None else "N/A"}</b> mm
                        {" · เฉลี่ย " + str(_avg) if _avg is not None else ""}
                    </span>
                </div>
                <div class='prog-wrap'>
                    <div class='prog-fill' style='width:{_bar_w:.1f}%;background:{_bar_col};'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with c3:
        st.markdown('<div class="dash-box"><h4>🚨 สถานีเสี่ยงสูงสุด TOP 5</h4>', unsafe_allow_html=True)
        _sorted = sorted(_station_weather, key=lambda x: x["rain_mm"] or -1, reverse=True)[:5]
        if not _sorted or _sorted[0]["rain_mm"] is None:
            st.markdown("<p style='color:#4a6070;font-size:0.82rem;'>ไม่มีข้อมูลฝนในขณะนี้</p>", unsafe_allow_html=True)
        else:
            for i, _s in enumerate(_sorted, 1):
                _rain = _s["rain_mm"]
                if _rain is None:
                    continue
                _bc = risk_color_hex(_rain)
                _lbl, _em, _, _ = risk_class(_rain)
                st.markdown(f"""
                <div style='display:flex;align-items:center;gap:10px;padding:7px 0;
                    border-bottom:1px solid rgba(91,200,255,0.07);'>
                    <span style='color:#4a6070;font-size:0.82rem;font-weight:700;width:16px;'>{i}</span>
                    <div style='flex:1;'>
                        <div style='color:#d0e8f8;font-size:0.82rem;font-weight:600;'>{_em} {_s["name"]}</div>
                        <div style='color:#4a7090;font-size:0.72rem;'>{_s["province"]} · {_s["line"]}</div>
                    </div>
                    <div style='text-align:right;'>
                        <div style='color:{_bc};font-size:1rem;font-weight:800;'>{_rain:.1f}</div>
                        <div style='color:#4a7090;font-size:0.68rem;'>mm</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")

    # ── Row 3: Station Summary Table ─────────────────────────
    st.markdown('<div class="sec-title">📋 ตารางสรุปสภาพอากาศทุกสถานีรถไฟ</div>', unsafe_allow_html=True)

    _tbl_rows = []
    for _s in sorted(_station_weather, key=lambda x: x["rain_mm"] or -1, reverse=True):
        _lbl, _em, _, _ = risk_class(_s["rain_mm"])
        _tbl_rows.append({
            "สาย": f"{_s['line_icon']} {_s['line_short']}",
            "สถานี": _s["name"],
            "จังหวัด": _s["province"],
            "ฝน (mm)": round(_s["rain_mm"], 1) if _s["rain_mm"] is not None else None,
            "ระดับ": f"{_em} {_lbl}",
            "อุณหภูมิ (°C)": round(_s["temp_c"], 1) if _s["temp_c"] is not None else None,
            "ลม (m/s)": round(_s["wind_ms"], 1) if _s["wind_ms"] is not None else None,
            "RH (%)": round(_s["rh_pct"], 0) if _s["rh_pct"] is not None else None,
            "สถานีอุตุ": _s["tmd_name"][:18] if _s["tmd_name"] else "—",
        })

    _df = pd.DataFrame(_tbl_rows)
    st.dataframe(
        _df,
        use_container_width=True,
        hide_index=True,
        height=340,
        column_config={
            "ฝน (mm)": st.column_config.NumberColumn("🌧️ ฝน (mm)", format="%.1f"),
            "อุณหภูมิ (°C)": st.column_config.NumberColumn("🌡️ °C", format="%.1f"),
            "ลม (m/s)": st.column_config.NumberColumn("💨 ลม", format="%.1f"),
            "RH (%)": st.column_config.NumberColumn("💧 RH%", format="%.0f"),
        },
    )

    # ── Row 4: Warning news summary ──────────────────────────
    if _warning:
        st.markdown('<div class="sec-title">📰 ข่าวเตือนภัยล่าสุด (TMD)</div>', unsafe_allow_html=True)
        _warn_items = extract_stations_list(_warning) or []
        if not _warn_items:
            for k in ["WeatherWarnings","warnings","items","Items","NewsItems"]:
                if k in _warning and isinstance(_warning[k], list):
                    _warn_items = _warning[k]
                    break
        _wc = st.columns(min(len(_warn_items[:3]) or 1, 3))
        for i, wi in enumerate(_warn_items[:3]):
            _title = wi.get("Title") or wi.get("title") or wi.get("Subject") or "ข่าวเตือนภัย"
            _body  = wi.get("Detail") or wi.get("detail") or wi.get("Body") or wi.get("content") or ""
            with _wc[i % 3]:
                st.markdown(f"""
                <div class='alert-card alert-warning'>
                    <div class='alert-card-title'>⚠️ {str(_title)[:60]}</div>
                    <div class='alert-card-body'>{str(_body)[:120]}{"..." if len(str(_body)) > 120 else ""}</div>
                </div>
                """, unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════╗
# ║  TAB 2 — MAP                                            ║
# ╚══════════════════════════════════════════════════════════╝
with tab_map:
    st.markdown('<div class="sec-title">🗺️ แผนที่โครงข่ายรถไฟและสภาพอากาศ</div>', unsafe_allow_html=True)
    try:
        import folium
        from streamlit_folium import st_folium

        _m = folium.Map(location=[13.5, 101.5], zoom_start=6, tiles=None)
        folium.TileLayer(
            tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
            attr="© OpenStreetMap © CARTO", name="Dark", max_zoom=19,
        ).add_to(_m)

        # Draw lines
        for _ln, _ld in SRT_LINES.items():
            if sel_line != "ทุกสาย" and _ln != sel_line:
                continue
            _coords = [[s["lat"], s["lon"]] for s in _ld["stations"]]
            folium.PolyLine(_coords, color=_ld["color"], weight=3, opacity=0.85,
                            tooltip=f"{_ln} — {_ld['desc']}").add_to(_m)

        # Station markers
        for _sw in _station_weather:
            _rc = risk_color_hex(_sw["rain_mm"])
            _lbl, _em, _, _ = risk_class(_sw["rain_mm"])
            _ic_color = {
                "#ef4444":"red","#f59e0b":"orange","#3b82f6":"blue","#10b981":"green","#4a6070":"gray"
            }.get(_rc, "blue")
            _popup_html = f"""
            <div style='font-family:Sarabun,sans-serif;min-width:180px;max-width:240px;'>
                <b style='font-size:1rem;color:#111;'>{_sw['name']}</b>
                <br><span style='color:#555;font-size:0.82rem;'>{_sw['province']} · {_sw['line']}</span>
                <hr style='margin:6px 0;border-color:#ddd;'>
                <table style='font-size:0.82rem;width:100%;'>
                    <tr><td>🌧️ ฝน</td><td><b>{f"{_sw['rain_mm']:.1f} mm" if _sw['rain_mm'] is not None else 'N/A'}</b></td></tr>
                    <tr><td>⚠️ ระดับ</td><td>{_em} {_lbl}</td></tr>
                    <tr><td>🌡️ อุณหภูมิ</td><td>{f"{_sw['temp_c']:.1f}°C" if _sw['temp_c'] is not None else 'N/A'}</td></tr>
                    <tr><td>💨 ลม</td><td>{f"{_sw['wind_ms']:.1f} m/s" if _sw['wind_ms'] is not None else 'N/A'}</td></tr>
                    <tr><td>📡 อุตุ</td><td>{_sw['tmd_name'][:20] or 'N/A'} ({_sw['tmd_km']} km)</td></tr>
                </table>
            </div>"""
            folium.Marker(
                location=[_sw["lat"], _sw["lon"]],
                popup=folium.Popup(_popup_html, max_width=260),
                tooltip="{} {} {}".format(_sw['name'], _em, "{:.1f}mm".format(_sw['rain_mm']) if _sw['rain_mm'] is not None else ""),
                icon=folium.Icon(color=_ic_color, icon="train", prefix="fa"),
            ).add_to(_m)

        st.caption("🖱️ คลิกไอคอนสถานีเพื่อดูข้อมูล · 🔴 ฝนหนักมาก · 🟠 ฝนหนัก · 🔵 ฝนปานกลาง · 🟢 ปกติ")
        st_folium(_m, width="100%", height=580, returned_objects=[])

    except ImportError:
        st.warning("⚠️ ติดตั้ง `folium` และ `streamlit-folium` เพื่อแสดงแผนที่")
        _map_df = pd.DataFrame([{
            "สถานี":_sw["name"],"จังหวัด":_sw["province"],"สาย":_sw["line"],
            "lat":_sw["lat"],"lon":_sw["lon"],
            "ฝน mm": _sw["rain_mm"],
        } for _sw in _station_weather])
        st.map(_map_df, latitude="lat", longitude="lon", use_container_width=True)

    # Map legend
    st.markdown("""
    <div style='display:flex;gap:16px;flex-wrap:wrap;margin-top:8px;'>
        <span style='color:#6899b8;font-size:0.8rem;'>เส้นทาง:</span>
    """ + "".join([
        f"<span style='display:flex;align-items:center;gap:5px;'><span style='width:20px;height:3px;border-radius:2px;background:{ld['color']};display:inline-block;'></span><span style='color:#7ec8e3;font-size:0.78rem;'>{ln}</span></span>"
        for ln, ld in SRT_LINES.items()
    ]) + "</div>", unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════╗
# ║  TAB 3 — ALERTS                                         ║
# ╚══════════════════════════════════════════════════════════╝
with tab_alert:
    _ca, _cb = st.columns([1.6, 1])

    with _ca:
        st.markdown('<div class="sec-title">🚨 แจ้งเตือนสถานีเสี่ยง</div>', unsafe_allow_html=True)
        _alert_stations = [
            s for s in sorted(_station_weather, key=lambda x: x["rain_mm"] or -1, reverse=True)
            if (s["rain_mm"] or 0) >= _t_mm
        ]
        if _alert_stations:
            for _s in _alert_stations:
                _lbl, _em, _, _ac = risk_class(_s["rain_mm"])
                st.markdown(f"""
                <div class='alert-card {_ac}'>
                    <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
                        <div>
                            <div class='alert-card-title'>{_em} {_s['name']}
                                <span style='color:{_s["line_color"]};font-size:0.75rem;font-weight:600;margin-left:8px;'>
                                    [{_s["line_short"]}] {_s["line"]}
                                </span>
                            </div>
                            <div class='alert-card-body'>
                                📍 {_s['province']}
                                {f" · 🌧️ <b>{_s['rain_mm']:.1f} mm</b>" if _s["rain_mm"] is not None else ""}
                                {f" · 🌡️ {_s['temp_c']:.1f}°C" if _s["temp_c"] is not None else ""}
                                {f" · 💨 {_s['wind_ms']:.1f} m/s" if _s["wind_ms"] is not None else ""}
                                {f"<br>📡 อุตุฯ: {_s['tmd_name']} ({_s['tmd_km']} km)" if _s["tmd_name"] else ""}
                            </div>
                        </div>
                        <div style='text-align:right;min-width:70px;'>
                            <div style='color:#fff;font-size:1.3rem;font-weight:800;'>
                                {f"{_s['rain_mm']:.0f}" if _s["rain_mm"] is not None else "—"}
                            </div>
                            <div style='color:#6899b8;font-size:0.72rem;'>mm</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='alert-card alert-ok'>
                <div class='alert-card-title'>✅ ไม่มีสถานีเกินเกณฑ์ ({alert_thresh})</div>
                <div class='alert-card-body'>ทุกสถานีในเส้นทางที่เลือกสภาพอากาศปกติ
                {" · หรือยังไม่ได้รับข้อมูลจาก TMD" if not _obs_list else ""}</div>
            </div>
            """, unsafe_allow_html=True)

    with _cb:
        st.markdown('<div class="sec-title">📰 ข่าวเตือนภัย (TMD)</div>', unsafe_allow_html=True)
        _wlist = []
        if _warning:
            for k in ["WeatherWarnings","warnings","items","Items","NewsItems","data"]:
                if k in _warning and isinstance(_warning[k], list):
                    _wlist = _warning[k]; break
        if _wlist:
            for wi in _wlist[:6]:
                _t = wi.get("Title") or wi.get("Subject") or "ข่าวเตือนภัย"
                _b = wi.get("Detail") or wi.get("Body") or wi.get("content") or ""
                _d = wi.get("Date") or wi.get("IssueDate") or ""
                st.markdown(f"""
                <div class='alert-card alert-warning'>
                    <div class='alert-card-title'>⚠️ {str(_t)[:55]}</div>
                    <div class='alert-card-body'>{str(_b)[:100]}{"..." if len(str(_b))>100 else ""}</div>
                    {"<div class='alert-card-meta'>📅 "+str(_d)[:16]+"</div>" if _d else ""}
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='alert-card alert-ok'>
                <div class='alert-card-title'>✅ ไม่มีข่าวเตือนภัยในขณะนี้</div>
                <div class='alert-card-body'>หรือยังไม่ได้รับข้อมูลจาก TMD API</div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sec-title">🌋 แผ่นดินไหว</div>', unsafe_allow_html=True)
        _eqlist = []
        if _seismic:
            for k in ["SeismicEvents","events","data","Earthquakes","items"]:
                if k in _seismic and isinstance(_seismic[k], list):
                    _eqlist = _seismic[k]; break
        if _eqlist:
            for eq in _eqlist[:5]:
                _mag = _fnum(eq, "Magnitude","mag","M","Richter") or "?"
                _loc = eq.get("Location") or eq.get("location") or eq.get("Area") or "ไม่ระบุ"
                _edt = eq.get("OriginTime") or eq.get("Date") or ""
                try:
                    _mf = float(_mag)
                    _ec = "alert-critical" if _mf >= 5.0 else "alert-warning" if _mf >= 3.5 else "alert-info"
                except Exception:
                    _ec = "alert-info"
                st.markdown(f"""
                <div class='alert-card {_ec}'>
                    <div class='alert-card-title'>🌋 M {_mag} — {str(_loc)[:40]}</div>
                    {"<div class='alert-card-meta'>📅 "+str(_edt)[:16]+"</div>" if _edt else ""}
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='alert-card alert-info'>
                <div class='alert-card-title'>ℹ️ ไม่มีข้อมูลแผ่นดินไหว</div>
            </div>""", unsafe_allow_html=True)

        # Rainfall criteria reference
        st.markdown('<div class="sec-title">📋 เกณฑ์ฝน (กรมอุตุฯ)</div>', unsafe_allow_html=True)
        for _em, _lv, _mm, _cls in [
            ("🌦️","ฝนเล็กน้อย","< 10 mm/วัน","alert-ok"),
            ("🌧️","ฝนปานกลาง","10–35 mm/วัน","alert-info"),
            ("⛈️","ฝนหนัก","35–90 mm/วัน","alert-warning"),
            ("🌊","ฝนหนักมาก","> 90 mm/วัน","alert-critical"),
        ]:
            st.markdown(f"""
            <div class='alert-card {_cls}' style='padding:7px 14px;'>
                <div class='alert-card-body'>{_em} <b>{_lv}</b> — {_mm}</div>
            </div>""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════╗
# ║  TAB 4 — PER LINE                                       ║
# ╚══════════════════════════════════════════════════════════╝
with tab_line:
    _lines_show = [sel_line] if sel_line != "ทุกสาย" else list(SRT_LINES.keys())
    for _ln in _lines_show:
        _ld = SRT_LINES[_ln]
        _ln_stns = [s for s in _station_weather if s["line"] == _ln]
        _ln_rains = [s["rain_mm"] for s in _ln_stns if s["rain_mm"] is not None]
        _ln_max  = max(_ln_rains) if _ln_rains else None
        _ln_avg  = round(sum(_ln_rains)/len(_ln_rains), 1) if _ln_rains else None
        _ln_heavy_cnt = sum(1 for r in _ln_rains if r >= 35)

        with st.expander(
            f"{_ld['icon']} {_ln} — {_ld['desc']}  |  "
            f"{'🚨 ' + str(_ln_heavy_cnt) + ' สถานีเสี่ยง' if _ln_heavy_cnt else '✅ ปกติ'}",
            expanded=(sel_line != "ทุกสาย")
        ):
            # Summary row
            _mc = st.columns(4)
            with _mc[0]: st.metric("🌧️ ฝนสูงสุด", f"{_ln_max:.1f} mm" if _ln_max is not None else "N/A")
            with _mc[1]: st.metric("📊 ฝนเฉลี่ย", f"{_ln_avg} mm" if _ln_avg is not None else "N/A")
            with _mc[2]: st.metric("⛈️ สถานีเสี่ยง", f"{_ln_heavy_cnt} สถานี")
            with _mc[3]: st.metric("📍 สถานีทั้งหมด", f"{len(_ln_stns)} สถานี")

            # Station rows
            st.markdown(f"""
            <div class='stn-row' style='background:rgba(91,200,255,0.06);'>
                <span style='color:#5bc8ff;font-size:0.74rem;font-weight:700;'>สถานี</span>
                <span style='color:#5bc8ff;font-size:0.74rem;font-weight:700;'>จังหวัด</span>
                <span style='color:#5bc8ff;font-size:0.74rem;font-weight:700;text-align:right;'>ฝน (mm)</span>
                <span style='color:#5bc8ff;font-size:0.74rem;font-weight:700;text-align:right;'>อุณหภูมิ</span>
                <span style='color:#5bc8ff;font-size:0.74rem;font-weight:700;text-align:right;'>ระดับ</span>
            </div>""", unsafe_allow_html=True)

            for _s in _ln_stns:
                _lbl, _em, _, _ = risk_class(_s["rain_mm"])
                _rc = risk_color_hex(_s["rain_mm"])
                st.markdown(f"""
                <div class='stn-row'>
                    <div>
                        <div class='stn-name'>🚉 {_s['name']}</div>
                        {"<div class='stn-prov'>km " + str(_s.get('km','')) + "</div>" if _s.get('km') is not None else ""}
                    </div>
                    <div class='stn-prov'>{_s['province']}</div>
                    <div class='stn-val' style='color:{_rc};font-weight:700;'>
                        {f"{_s['rain_mm']:.1f}" if _s["rain_mm"] is not None else "—"}
                    </div>
                    <div class='stn-val'>
                        {f"{_s['temp_c']:.1f}°C" if _s["temp_c"] is not None else "—"}
                    </div>
                    <div class='stn-val'>
                        <span class='badge badge-{"critical" if _s["rain_mm"] and _s["rain_mm"]>=90 else "high" if _s["rain_mm"] and _s["rain_mm"]>=35 else "medium" if _s["rain_mm"] and _s["rain_mm"]>=10 else "low" if _s["rain_mm"] is not None else "na"}'>
                            {_em} {_lbl}
                        </span>
                    </div>
                </div>""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════╗
# ║  TAB 5 — FORECAST                                       ║
# ╚══════════════════════════════════════════════════════════╝
with tab_forecast:
    st.markdown('<div class="sec-title">🌤️ พยากรณ์อากาศล่วงหน้า 7 วัน (รายภาค)</div>', unsafe_allow_html=True)

    _REGION_LINES = {
        "ภาคเหนือ":                  ["สายเหนือ"],
        "ภาคตะวันออกเฉียงเหนือ":     ["สายตะวันออกเฉียงเหนือ","สายอีสานใต้"],
        "ภาคกลาง":                   ["สายเหนือ","สายตะวันออกเฉียงเหนือ"],
        "ภาคตะวันออก":               ["สายตะวันออก"],
        "ภาคใต้ฝั่งตะวันออก":        ["สายใต้"],
        "ภาคใต้ฝั่งตะวันตก":         ["สายใต้"],
    }

    if _forecast:
        _regions = None
        for k in ["WeatherForecasts","forecasts","data","Regions","regions"]:
            if k in _forecast and isinstance(_forecast[k], list):
                _regions = _forecast[k]; break

        if _regions:
            for _rg in _regions[:6]:
                _rname = _rg.get("RegionNameTh") or _rg.get("region") or _rg.get("Name") or "ภาค"
                _rel_lines = _REGION_LINES.get(_rname, [])
                _rel_txt = " · ".join([l.split(" ")[0] for l in _rel_lines]) if _rel_lines else ""
                with st.expander(f"🌏 {_rname}" + (f" → เส้นทาง: {_rel_txt}" if _rel_txt else ""), expanded=False):
                    _fdays = _rg.get("Forecasts") or _rg.get("days") or _rg.get("DailyForecasts") or []
                    if _fdays:
                        _fd_rows = [{
                            "วันที่": d.get("ForecastDate") or d.get("date",""),
                            "สภาพอากาศ": d.get("Condition") or d.get("Weather") or d.get("cond",""),
                            "ฝน (%)": d.get("RainPercent") or d.get("rain",""),
                            "อุณหภูมิสูงสุด": d.get("MaxTemp") or d.get("max_temp",""),
                            "อุณหภูมิต่ำสุด": d.get("MinTemp") or d.get("min_temp",""),
                        } for d in _fdays[:7]]
                        st.dataframe(pd.DataFrame(_fd_rows), use_container_width=True, hide_index=True)
                    else:
                        st.json({k:v for k,v in _rg.items() if k not in ("Forecasts","days")})
        e
