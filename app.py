import streamlit as st
import requests
import json
import math
import pandas as pd
from datetime import datetime
import pytz

# ─────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ระบบแจ้งเตือนสภาพอากาศโครงข่ายรถไฟไทย",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700&display=swap');

* { font-family: 'Sarabun', sans-serif !important; }

/* ── App background ── */
.stApp {
    background: linear-gradient(135deg, #0a1628 0%, #0d2137 40%, #0a1f35 100%);
    min-height: 100vh;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #071220 0%, #0c1e30 100%) !important;
    border-right: 1px solid rgba(0,180,255,0.2) !important;
}
[data-testid="stSidebar"] * { color: #c8dff0 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label { color: #7ec8e3 !important; font-size: 0.82rem !important; }

/* ── Metric cards ── */
.metric-card {
    background: linear-gradient(135deg, rgba(0,120,200,0.15), rgba(0,60,120,0.25));
    border: 1px solid rgba(0,180,255,0.25);
    border-radius: 12px;
    padding: 16px 20px;
    margin: 6px 0;
    backdrop-filter: blur(4px);
}
.metric-card h3 { color: #5bc8ff; margin:0 0 4px 0; font-size:0.82rem; font-weight:600; text-transform:uppercase; letter-spacing:0.5px; }
.metric-card .value { color: #fff; font-size: 1.6rem; font-weight: 700; line-height:1; }
.metric-card .unit  { color: #7ec8e3; font-size: 0.75rem; margin-left:4px; }

/* ── Alert cards ── */
.alert-critical {
    background: linear-gradient(135deg, rgba(220,38,38,0.2), rgba(180,0,0,0.3));
    border: 1px solid rgba(220,38,38,0.6);
    border-left: 4px solid #ef4444;
    border-radius: 10px; padding: 14px 18px; margin: 8px 0;
}
.alert-warning {
    background: linear-gradient(135deg, rgba(245,158,11,0.15), rgba(180,100,0,0.2));
    border: 1px solid rgba(245,158,11,0.5);
    border-left: 4px solid #f59e0b;
    border-radius: 10px; padding: 14px 18px; margin: 8px 0;
}
.alert-info {
    background: linear-gradient(135deg, rgba(59,130,246,0.12), rgba(0,80,200,0.18));
    border: 1px solid rgba(59,130,246,0.4);
    border-left: 4px solid #3b82f6;
    border-radius: 10px; padding: 14px 18px; margin: 8px 0;
}
.alert-ok {
    background: linear-gradient(135deg, rgba(16,185,129,0.12), rgba(0,120,80,0.18));
    border: 1px solid rgba(16,185,129,0.4);
    border-left: 4px solid #10b981;
    border-radius: 10px; padding: 14px 18px; margin: 8px 0;
}
.alert-card-title { color: #fff; font-weight:700; font-size:1rem; margin:0 0 4px 0; }
.alert-card-body  { color: #c8dff0; font-size:0.87rem; margin:0; }

/* ── Section headers ── */
.section-header {
    color: #5bc8ff;
    font-size: 1.1rem;
    font-weight: 700;
    border-bottom: 1px solid rgba(0,180,255,0.3);
    padding-bottom: 6px;
    margin: 16px 0 10px 0;
}

/* ── Station table ── */
.station-row {
    display: flex; align-items:center; gap:12px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(0,180,255,0.12);
    border-radius: 8px; padding: 10px 14px; margin: 4px 0;
}
.station-name { color: #e0f0ff; font-weight:600; font-size:0.9rem; flex:1; }
.station-detail { color: #7ec8e3; font-size: 0.8rem; }
.badge-rain   { background:#3b82f6; color:#fff; padding:2px 8px; border-radius:12px; font-size:0.72rem; font-weight:700; }
.badge-alert  { background:#ef4444; color:#fff; padding:2px 8px; border-radius:12px; font-size:0.72rem; font-weight:700; }
.badge-ok     { background:#10b981; color:#fff; padding:2px 8px; border-radius:12px; font-size:0.72rem; font-weight:700; }
.badge-warn   { background:#f59e0b; color:#fff; padding:2px 8px; border-radius:12px; font-size:0.72rem; font-weight:700; }

/* ── Main title ── */
.main-title {
    background: linear-gradient(90deg, #5bc8ff, #3b9eff, #5bc8ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    font-size: 1.9rem; font-weight: 800; margin: 0;
}
.sub-title { color: #7ec8e3; font-size: 0.9rem; margin-top: 2px; }

/* ── Override streamlit components ── */
div[data-testid="stMetric"] {
    background: rgba(0,100,180,0.12) !important;
    border: 1px solid rgba(0,180,255,0.2) !important;
    border-radius: 10px !important; padding: 14px !important;
}
div[data-testid="stMetric"] label { color: #7ec8e3 !important; font-size:0.8rem !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #fff !important; font-size: 1.5rem !important; }
div[data-testid="stMetric"] [data-testid="stMetricDelta"] { font-size: 0.78rem !important; }

.stTabs [data-baseweb="tab-list"] { background: rgba(0,60,120,0.3) !important; border-radius: 8px; }
.stTabs [data-baseweb="tab"] { color: #7ec8e3 !important; }
.stTabs [aria-selected="true"] { background: rgba(0,120,200,0.4) !important; color: #fff !important; }

.stSelectbox > div > div { background: rgba(0,40,80,0.6) !important; border-color: rgba(0,180,255,0.3) !important; color: #c8dff0 !important; }

div[data-testid="stExpander"] {
    background: rgba(0,40,80,0.25) !important;
    border: 1px solid rgba(0,180,255,0.2) !important;
    border-radius: 8px !important;
}

.stButton > button {
    background: linear-gradient(135deg, #0066cc, #0044aa) !important;
    color: white !important; border: 1px solid rgba(0,180,255,0.4) !important;
    border-radius: 8px !important; font-weight: 600 !important;
    transition: all 0.2s;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #0088ff, #0055cc) !important;
    box-shadow: 0 0 16px rgba(0,150,255,0.4) !important;
}

/* scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #071220; }
::-webkit-scrollbar-thumb { background: #1a4a7a; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
#  TMD API TOKEN  (set via Streamlit secrets or env)
# ─────────────────────────────────────────────────────────
try:
    TMD_TOKEN = st.secrets["TMD_TOKEN"]
except Exception:
    import os
    TMD_TOKEN = os.environ.get("TMD_TOKEN", "")

# TMD API base URL — must use http:// (TMD legacy API does not support HTTPS)
TMD_BASE = "http://data.tmd.go.th/api"

# Extract uid (sub) from JWT payload — TMD requires uid=<sub> & ukey=<full_jwt>
def _parse_uid(token: str) -> str:
    """Decode JWT sub field without a library (base64url decode payload section)."""
    import base64, json as _json
    try:
        parts = token.split(".")
        if len(parts) < 2:
            return ""
        payload = parts[1]
        # pad to multiple of 4
        payload += "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload)
        return str(_json.loads(decoded).get("sub", ""))
    except Exception:
        return ""

TMD_UID  = _parse_uid(TMD_TOKEN)   # e.g. "5439"
TMD_UKEY = TMD_TOKEN               # full JWT string

# ─────────────────────────────────────────────────────────
#  RAILWAY STATIONS ALONG NETWORK (mapped from KMZ centroids)
# ─────────────────────────────────────────────────────────
RAIL_LINES = {
    "สายเหนือ (กรุงเทพ–เชียงใหม่)": [
        {"name": "กรุงเทพ (หัวลำโพง)", "lat": 13.738, "lon": 100.517, "province": "กรุงเทพมหานคร"},
        {"name": "อยุธยา",             "lat": 14.355, "lon": 100.567, "province": "พระนครศรีอยุธยา"},
        {"name": "ลพบุรี",             "lat": 14.799, "lon": 100.614, "province": "ลพบุรี"},
        {"name": "นครสวรรค์",          "lat": 15.703, "lon": 100.136, "province": "นครสวรรค์"},
        {"name": "พิษณุโลก",           "lat": 16.820, "lon": 100.263, "province": "พิษณุโลก"},
        {"name": "ลำปาง",              "lat": 18.289, "lon": 99.490, "province": "ลำปาง"},
        {"name": "เชียงใหม่",          "lat": 18.789, "lon": 99.003, "province": "เชียงใหม่"},
    ],
    "สายตะวันออกเฉียงเหนือ (กรุงเทพ–หนองคาย)": [
        {"name": "กรุงเทพ (หัวลำโพง)", "lat": 13.738, "lon": 100.517, "province": "กรุงเทพมหานคร"},
        {"name": "สระบุรี",            "lat": 14.529, "lon": 100.910, "province": "สระบุรี"},
        {"name": "นครราชสีมา",         "lat": 14.973, "lon": 102.112, "province": "นครราชสีมา"},
        {"name": "ขอนแก่น",            "lat": 16.441, "lon": 102.834, "province": "ขอนแก่น"},
        {"name": "อุดรธานี",           "lat": 17.391, "lon": 102.793, "province": "อุดรธานี"},
        {"name": "หนองคาย",            "lat": 17.877, "lon": 102.743, "province": "หนองคาย"},
    ],
    "สายอีสานใต้ (ถนนจิระ–อุบลราชธานี)": [
        {"name": "ถนนจิระ",            "lat": 14.973, "lon": 102.112, "province": "นครราชสีมา"},
        {"name": "บุรีรัมย์",          "lat": 14.995, "lon": 103.103, "province": "บุรีรัมย์"},
        {"name": "สุรินทร์",           "lat": 14.883, "lon": 103.494, "province": "สุรินทร์"},
        {"name": "ศรีสะเกษ",           "lat": 15.117, "lon": 104.322, "province": "ศรีสะเกษ"},
        {"name": "อุบลราชธานี",        "lat": 15.224, "lon": 104.858, "province": "อุบลราชธานี"},
    ],
    "สายใต้ (กรุงเทพ–สุไหงโก-ลก)": [
        {"name": "กรุงเทพ (หัวลำโพง)", "lat": 13.738, "lon": 100.517, "province": "กรุงเทพมหานคร"},
        {"name": "ราชบุรี",            "lat": 13.536, "lon": 99.817, "province": "ราชบุรี"},
        {"name": "ชุมพร",              "lat": 10.494, "lon": 99.180, "province": "ชุมพร"},
        {"name": "สุราษฎร์ธานี",       "lat": 9.140,  "lon": 99.330, "province": "สุราษฎร์ธานี"},
        {"name": "นครศรีธรรมราช",      "lat": 8.433,  "lon": 99.963, "province": "นครศรีธรรมราช"},
        {"name": "หาดใหญ่",            "lat": 7.008,  "lon": 100.474, "province": "สงขลา"},
        {"name": "ปาดังเบซาร์",        "lat": 6.673,  "lon": 100.378, "province": "สงขลา"},
    ],
    "สายตะวันออก (กรุงเทพ–อรัญประเทศ)": [
        {"name": "มักกะสัน",           "lat": 13.752, "lon": 100.568, "province": "กรุงเทพมหานคร"},
        {"name": "ฉะเชิงเทรา",         "lat": 13.690, "lon": 101.077, "province": "ฉะเชิงเทรา"},
        {"name": "ชลบุรี",             "lat": 13.364, "lon": 100.990, "province": "ชลบุรี"},
        {"name": "อรัญประเทศ",         "lat": 13.694, "lon": 102.506, "province": "สระแก้ว"},
    ],
}

# Flatten all stations with line info
ALL_STATIONS = []
for line_name, stations in RAIL_LINES.items():
    for s in stations:
        s = dict(s)
        s["line"] = line_name
        ALL_STATIONS.append(s)

# Deduplicate by name
seen = set()
UNIQUE_STATIONS = []
for s in ALL_STATIONS:
    if s["name"] not in seen:
        UNIQUE_STATIONS.append(s)
        seen.add(s["name"])

# ─────────────────────────────────────────────────────────
#  TMD API HELPERS
#  Authentication: uid=<sub from JWT>  &  ukey=<full JWT token>
#  Base URL: http://data.tmd.go.th/api  (http, NOT https)
# ─────────────────────────────────────────────────────────

def _tmd_params(extra: dict = None) -> dict:
    """Build standard TMD query params (uid + ukey + format)."""
    p = {"uid": TMD_UID, "ukey": TMD_UKEY, "format": "json"}
    if extra:
        p.update(extra)
    return p


def _tmd_get(endpoint: str, extra_params: dict = None, timeout: int = 15):
    """GET a TMD endpoint; return parsed JSON or None."""
    url = f"{TMD_BASE}/{endpoint}"
    try:
        r = requests.get(url, params=_tmd_params(extra_params), timeout=timeout)
        if r.status_code == 200:
            data = r.json()
            # TMD sometimes wraps errors in a 200 response
            if isinstance(data, dict) and data.get("error"):
                return None
            return data
    except Exception:
        pass
    return None


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_weather_warning():
    """ดึงข่าวเตือนภัยสภาพอากาศ — WeatherWarningNews/V1"""
    return _tmd_get("WeatherWarningNews/V1/")


@st.cache_data(ttl=900, show_spinner=False)
def fetch_weather_today():
    """ดึงสภาพอากาศรายวัน 07:00 — WeatherToday/V2"""
    return _tmd_get("WeatherToday/V2/")


@st.cache_data(ttl=900, show_spinner=False)
def fetch_weather_3h():
    """ดึงสภาพอากาศราย 3 ชม. — Weather3Hours/V2"""
    return _tmd_get("Weather3Hours/V2/")


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_forecast_7days():
    """ดึงพยากรณ์ 7 วัน รายภาค — WeatherForecast7DaysByRegion/V1"""
    return _tmd_get("WeatherForecast7DaysByRegion/V1/")


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_seismic():
    """ดึงข้อมูลแผ่นดินไหว"""
    try:
        r = requests.get(
            f"{TMD_LEGACY}/DailySeismicEvent/V1/",
            params={"format": "json"},
            timeout=10,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def haversine(lat1, lon1, lat2, lon2):
    """คำนวณระยะทางระหว่างสองจุด (km)"""
    R = 6371
    φ1, φ2 = math.radians(lat1), math.radians(lat2)
    Δφ = math.radians(lat2 - lat1)
    Δλ = math.radians(lon2 - lon1)
    a = math.sin(Δφ/2)**2 + math.cos(φ1)*math.cos(φ2)*math.sin(Δλ/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def find_nearest_station_data(rail_station, obs_data, radius_km=80):
    """หาสถานีอุตุฯ ที่ใกล้สถานีรถไฟ"""
    if not obs_data:
        return None
    stations_list = None
    # Try different JSON structures
    for key in ["Stations", "stations", "data", "Data"]:
        if key in obs_data:
            stations_list = obs_data[key]
            break
    if not stations_list:
        return None
    best, best_dist = None, 9999
    for st in stations_list:
        try:
            slat = float(st.get("Lat") or st.get("lat") or st.get("StationLatitude") or 0)
            slon = float(st.get("Lon") or st.get("lon") or st.get("StationLongitude") or 0)
        except (TypeError, ValueError):
            continue
        if slat == 0 and slon == 0:
            continue
        d = haversine(rail_station["lat"], rail_station["lon"], slat, slon)
        if d < best_dist and d < radius_km:
            best_dist = d
            best = dict(st)
            best["_distance_km"] = round(d, 1)
    return best


def get_rain_mm(obs):
    """ดึงค่าฝน mm จาก observation dict"""
    if not obs:
        return None
    for key in ["Rain", "rain", "Rainfall", "rainfall", "RainfallToday",
                "Precip", "precip", "TotalRain", "Rain24h"]:
        v = obs.get(key)
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                pass
    return None


def get_temp(obs):
    for key in ["Temp", "temp", "Temperature", "temperature", "AirTemp"]:
        v = obs.get(key)
        if v is not None:
            try:
                return float(v)
            except Exception:
                pass
    return None


def get_wind_speed(obs):
    for key in ["WindSpeed", "windspeed", "Wind", "wind", "WindSpd"]:
        v = obs.get(key)
        if v is not None:
            try:
                return float(v)
            except Exception:
                pass
    return None


def rain_level(mm):
    if mm is None:
        return "unknown", "⚪", "badge-ok"
    if mm == 0:
        return "ไม่มีฝน", "🌤️", "badge-ok"
    elif mm < 10:
        return "ฝนเล็กน้อย", "🌦️", "badge-rain"
    elif mm < 35:
        return "ฝนปานกลาง", "🌧️", "badge-warn"
    elif mm < 90:
        return "ฝนหนัก", "⛈️", "badge-alert"
    else:
        return "ฝนหนักมาก", "🌊", "badge-alert"


def alert_level_color(mm):
    if mm is None:
        return "alert-info"
    if mm >= 90:
        return "alert-critical"
    elif mm >= 35:
        return "alert-warning"
    elif mm >= 10:
        return "alert-info"
    return "alert-ok"

# ─────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:10px 0 20px 0;'>
        <div style='font-size:2.8rem; margin-bottom:4px;'>🚆</div>
        <div style='color:#5bc8ff; font-size:1.05rem; font-weight:700;'>Railway Weather Alert</div>
        <div style='color:#7ec8e3; font-size:0.75rem;'>ระบบแจ้งเตือนสภาพอากาศเส้นทางรถไฟ</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Token input if not set
    if not TMD_TOKEN:
        st.markdown("**🔑 TMD API Token**")
        token_input = st.text_input("ใส่ Token", type="password", key="token_input",
                                    placeholder="eyJ0eXAiOiJKV1Qi...")
        if token_input:
            TMD_TOKEN = token_input
            TMD_UKEY  = token_input
            TMD_UID   = _parse_uid(token_input)
            st.success(f"✅ ตั้งค่า Token แล้ว (uid={TMD_UID})")
    else:
        uid_str = f"uid={TMD_UID}" if TMD_UID else "uid=?"
        st.markdown(f"**🔑 Token:** `{uid_str}` · `...{TMD_TOKEN[-8:]}`")

    st.markdown("---")

    # Line selector
    st.markdown("**🛤️ เลือกเส้นทางรถไฟ**")
    line_options = ["ทุกสาย"] + list(RAIL_LINES.keys())
    selected_line = st.selectbox("สาย", line_options, label_visibility="collapsed")

    st.markdown("**⚠️ ระดับการแจ้งเตือน**")
    alert_threshold = st.select_slider(
        "แสดงตั้งแต่ระดับ",
        options=["ทั้งหมด", "ฝนเล็กน้อย", "ฝนปานกลาง", "ฝนหนัก", "ฝนหนักมาก"],
        value="ทั้งหมด",
        label_visibility="collapsed"
    )

    st.markdown("---")
    tz_th = pytz.timezone("Asia/Bangkok")
    now_th = datetime.now(tz_th)
    st.markdown(f"""
    <div style='color:#7ec8e3; font-size:0.78rem;'>
        🕐 อัพเดตล่าสุด<br>
        <span style='color:#5bc8ff; font-size:1rem; font-weight:600;'>
            {now_th.strftime('%d %b %Y %H:%M')} น.
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🔄 รีเฟรชข้อมูล", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("""
    <div style='color:#3a5a7a; font-size:0.72rem; margin-top:16px; line-height:1.6;'>
        ข้อมูลจาก: กรมอุตุนิยมวิทยา<br>
        โครงข่าย: การรถไฟแห่งประเทศไทย<br>
        อัพเดตทุก: 15 - 30 นาที
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────────────────
col_title, col_status = st.columns([3, 1])
with col_title:
    st.markdown("""
    <p class='main-title'>🚆 ระบบแจ้งเตือนสภาพอากาศโครงข่ายรถไฟไทย</p>
    <p class='sub-title'>Thai Railway Network Weather & Disaster Alert System · ข้อมูลจากกรมอุตุนิยมวิทยา (TMD)</p>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
#  LOAD DATA
# ─────────────────────────────────────────────────────────
with st.spinner("กำลังโหลดข้อมูลสภาพอากาศ..."):
    obs_data      = fetch_weather_today()
    obs_3h        = fetch_weather_3h()
    warning_data  = fetch_weather_warning()
    forecast_data = fetch_forecast_7days()
    seismic_data  = _tmd_get("DailySeismicEvent/V1/")

api_ok = obs_data is not None or obs_3h is not None

# ─────────────────────────────────────────────────────────
#  STATUS BAR
# ─────────────────────────────────────────────────────────
status_cols = st.columns(5)
with status_cols[0]:
    if api_ok:
        st.metric("🌐 API Status", "✅ เชื่อมต่อ")
    elif TMD_TOKEN:
        st.metric("🌐 API Status", "⚠️ Token Error")
    else:
        st.metric("🌐 API Status", "❌ ไม่มี Token")
with status_cols[1]:
    st.metric("🔑 User ID", TMD_UID if TMD_UID else "ไม่พบ")
with status_cols[2]:
    n_stations = len(UNIQUE_STATIONS)
    st.metric("📍 สถานีรถไฟ", f"{n_stations} สถานี")
with status_cols[3]:
    n_lines = len(RAIL_LINES)
    st.metric("🛤️ สายรถไฟ", f"{n_lines} สาย")
with status_cols[4]:
    tz_th = pytz.timezone("Asia/Bangkok")
    st.metric("🕐 เวลา (ไทย)", datetime.now(tz_th).strftime("%H:%M น."))

# Show diagnostic if API failed
if not api_ok and TMD_TOKEN:
    with st.expander("🔍 ข้อมูล Debug (คลิกเพื่อดู)", expanded=False):
        st.code(f"""
URL ที่ใช้ : http://data.tmd.go.th/api/WeatherToday/V2/
uid        : {TMD_UID}
ukey       : ...{TMD_UKEY[-20:] if TMD_UKEY else '(ว่าง)'}
""")
        st.caption("ถ้า uid ว่าง = JWT decode ล้มเหลว, ถ้า uid ถูกแต่ยัง error = Token หมดอายุหรือ IP blocked")

st.markdown("")

# ─────────────────────────────────────────────────────────
#  MAIN TABS
# ─────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️ แผนที่สภาพอากาศ",
    "⚠️ แจ้งเตือนภัย",
    "📊 สถานีรายสาย",
    "🌐 พยากรณ์ 7 วัน"
])

# ╔══════════════════════════════════════════════════════╗
# ║  TAB 1 – MAP                                        ║
# ╚══════════════════════════════════════════════════════╝
with tab1:
    # Determine which stations to show
    if selected_line == "ทุกสาย":
        map_stations = UNIQUE_STATIONS
    else:
        map_stations = [s for s in ALL_STATIONS if s["line"] == selected_line]

    # Build folium map
    try:
        import folium
        from streamlit_folium import st_folium

        m = folium.Map(
            location=[13.5, 101.5],
            zoom_start=6,
            tiles=None,
        )

        # Dark tile layer
        folium.TileLayer(
            tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
            attr="© OpenStreetMap © CARTO",
            name="Dark Map",
            max_zoom=19,
        ).add_to(m)

        # Draw railway lines
        for line_name, stations in RAIL_LINES.items():
            if selected_line != "ทุกสาย" and line_name != selected_line:
                continue
            coords = [[s["lat"], s["lon"]] for s in stations]
            line_colors = {
                "สายเหนือ": "#ef4444",
                "สายตะวันออกเฉียงเหนือ": "#f59e0b",
                "สายอีสานใต้": "#a78bfa",
                "สายใต้": "#34d399",
                "สายตะวันออก": "#60a5fa",
            }
            color = "#5bc8ff"
            for k, v in line_colors.items():
                if k in line_name:
                    color = v
                    break
            folium.PolyLine(
                coords,
                color=color,
                weight=3,
                opacity=0.85,
                tooltip=line_name,
            ).add_to(m)

        # Plot stations
        for s in map_stations:
            obs = find_nearest_station_data(s, obs_data or obs_3h)
            rain = get_rain_mm(obs) if obs else None
            temp = get_temp(obs) if obs else None
            level_txt, emoji, badge = rain_level(rain)

            icon_color = "blue"
            if rain is not None:
                if rain >= 90:   icon_color = "red"
                elif rain >= 35: icon_color = "orange"
                elif rain >= 10: icon_color = "lightblue"
                else:            icon_color = "green"

            popup_html = f"""
            <div style='font-family:Sarabun,sans-serif; min-width:160px;'>
                <b style='font-size:1rem;'>{s['name']}</b><br>
                <span style='color:#555;'>{s['province']}</span><br>
                <hr style='margin:6px 0;'>
                {emoji} <b>{level_txt}</b>
                {f"<br>🌧️ ฝน: <b>{rain:.1f} mm</b>" if rain is not None else ""}
                {f"<br>🌡️ อุณหภูมิ: <b>{temp:.1f} °C</b>" if temp is not None else ""}
                {f"<br>📡 สถานีอุตุ: {obs.get('StationNameTh','') or obs.get('name','')} ({obs.get('_distance_km','?')} km)" if obs else "<br><i style='color:#999'>ไม่พบข้อมูลอุตุ</i>"}
            </div>
            """

            folium.Marker(
                location=[s["lat"], s["lon"]],
                popup=folium.Popup(popup_html, max_width=250),
                tooltip=f"{s['name']} {emoji}",
                icon=folium.Icon(color=icon_color, icon="train", prefix="fa"),
            ).add_to(m)

        st.markdown('<p class="section-header">🗺️ แผนที่โครงข่ายรถไฟและสภาพอากาศ</p>', unsafe_allow_html=True)
        st.caption("คลิกที่ไอคอนสถานีเพื่อดูข้อมูลสภาพอากาศ · สีแดง=ฝนหนักมาก · สีส้ม=ฝนหนัก · สีฟ้า=ฝนเล็กน้อย · สีเขียว=ปกติ")
        st_folium(m, width="100%", height=600, returned_objects=[])

    except ImportError:
        st.warning("⚠️ ติดตั้ง `folium` และ `streamlit-folium` เพื่อแสดงแผนที่")
        # Fallback: show coordinates table
        df_map = pd.DataFrame([
            {
                "สถานี": s["name"],
                "จังหวัด": s["province"],
                "สาย": s["line"].split("(")[0].strip(),
                "lat": s["lat"],
                "lon": s["lon"],
            }
            for s in map_stations
        ])
        st.dataframe(df_map, use_container_width=True)

    # Legend
    st.markdown("""
    <div style='display:flex; gap:16px; flex-wrap:wrap; margin-top:10px;'>
        <div style='display:flex;align-items:center;gap:6px;'>
            <div style='width:12px;height:12px;border-radius:50%;background:#ef4444;'></div>
            <span style='color:#c8dff0;font-size:0.8rem;'>สายเหนือ</span>
        </div>
        <div style='display:flex;align-items:center;gap:6px;'>
            <div style='width:12px;height:12px;border-radius:50%;background:#f59e0b;'></div>
            <span style='color:#c8dff0;font-size:0.8rem;'>สายตะวันออกเฉียงเหนือ</span>
        </div>
        <div style='display:flex;align-items:center;gap:6px;'>
            <div style='width:12px;height:12px;border-radius:50%;background:#a78bfa;'></div>
            <span style='color:#c8dff0;font-size:0.8rem;'>สายอีสานใต้</span>
        </div>
        <div style='display:flex;align-items:center;gap:6px;'>
            <div style='width:12px;height:12px;border-radius:50%;background:#34d399;'></div>
            <span style='color:#c8dff0;font-size:0.8rem;'>สายใต้</span>
        </div>
        <div style='display:flex;align-items:center;gap:6px;'>
            <div style='width:12px;height:12px;border-radius:50%;background:#60a5fa;'></div>
            <span style='color:#c8dff0;font-size:0.8rem;'>สายตะวันออก</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════╗
# ║  TAB 2 – ALERTS                                     ║
# ╚══════════════════════════════════════════════════════╝
with tab2:
    col_warn, col_seis = st.columns([2, 1])

    with col_warn:
        st.markdown('<p class="section-header">🚨 ข่าวเตือนภัยสภาพอากาศ (กรมอุตุนิยมวิทยา)</p>',
                    unsafe_allow_html=True)

        if warning_data:
            # Try to extract warning items
            warn_items = None
            for key in ["WeatherWarnings", "warnings", "data", "NewsItems", "Items"]:
                if key in warning_data:
                    warn_items = warning_data[key]
                    break
            if warn_items and isinstance(warn_items, list):
                for item in warn_items[:10]:
                    title = (item.get("Title") or item.get("title") or
                             item.get("Subject") or item.get("Header") or "ข่าวเตือนภัย")
                    body = (item.get("Detail") or item.get("detail") or
                            item.get("Body") or item.get("content") or "")
                    date = (item.get("Date") or item.get("date") or
                            item.get("IssueDate") or "")
                    st.markdown(f"""
                    <div class='alert-warning'>
                        <p class='alert-card-title'>⚠️ {title}</p>
                        <p class='alert-card-body'>{body[:200]}{"..." if len(str(body)) > 200 else ""}</p>
                        {"<small style='color:#a0b8c8;'>📅 "+str(date)+"</small>" if date else ""}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # Show raw summary
                st.markdown(f"""
                <div class='alert-info'>
                    <p class='alert-card-title'>📡 ข้อมูล API</p>
                    <p class='alert-card-body'>Keys: {list(warning_data.keys())[:6]}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='alert-ok'>
                <p class='alert-card-title'>✅ ไม่มีข่าวเตือนภัยในขณะนี้</p>
                <p class='alert-card-body'>สภาพอากาศในเส้นทางรถไฟทั่วประเทศอยู่ในเกณฑ์ปกติ หรือยังไม่ได้รับข้อมูลจาก API</p>
            </div>
            """, unsafe_allow_html=True)

        # Auto-generated alerts from rainfall data
        st.markdown('<p class="section-header">🌧️ การแจ้งเตือนฝนตกหนักตามเส้นทาง</p>',
                    unsafe_allow_html=True)

        threshold_map = {
            "ทั้งหมด": 0, "ฝนเล็กน้อย": 1,
            "ฝนปานกลาง": 10, "ฝนหนัก": 35, "ฝนหนักมาก": 90
        }
        min_rain = threshold_map.get(alert_threshold, 0)

        alert_stations = []
        for s in UNIQUE_STATIONS:
            if selected_line != "ทุกสาย" and s["line"] != selected_line:
                continue
            obs = find_nearest_station_data(s, obs_data or obs_3h)
            rain = get_rain_mm(obs) if obs else None
            if rain is not None and rain >= min_rain:
                alert_stations.append((s, obs, rain))

        if alert_stations:
            alert_stations.sort(key=lambda x: -(x[2] or 0))
            for s, obs, rain in alert_stations:
                level_txt, emoji, badge = rain_level(rain)
                temp = get_temp(obs) if obs else None
                wind = get_wind_speed(obs) if obs else None
                card_class = alert_level_color(rain)
                station_name_obs = (obs.get("StationNameTh") or obs.get("name") or "") if obs else ""
                dist_km = obs.get("_distance_km", "?") if obs else "?"
                st.markdown(f"""
                <div class='{card_class}'>
                    <p class='alert-card-title'>{emoji} {s['name']} ({s['province']})</p>
                    <p class='alert-card-body'>
                        🌧️ ปริมาณฝน: <b>{rain:.1f} mm</b> · ระดับ: <b>{level_txt}</b>
                        {f" · 🌡️ {temp:.1f}°C" if temp else ""}
                        {f" · 💨 {wind:.1f} m/s" if wind else ""}
                        {"<br>📡 อุตุฯ: " + station_name_obs + f" ({dist_km} km)" if station_name_obs else ""}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='alert-ok'>
                <p class='alert-card-title'>✅ ไม่มีการแจ้งเตือน (เกณฑ์: {alert_threshold})</p>
                <p class='alert-card-body'>ไม่พบฝนตกเกินเกณฑ์ที่กำหนดในเส้นทางที่เลือก
                {"หรือยังไม่ได้รับข้อมูลจาก TMD API" if not (obs_data or obs_3h) else ""}</p>
            </div>
            """, unsafe_allow_html=True)

    with col_seis:
        st.markdown('<p class="section-header">🌋 ข้อมูลแผ่นดินไหว</p>', unsafe_allow_html=True)

        if seismic_data:
            eq_list = None
            for k in ["SeismicEvents", "events", "data", "Earthquakes"]:
                if k in seismic_data:
                    eq_list = seismic_data[k]
                    break
            if eq_list and isinstance(eq_list, list):
                for eq in eq_list[:8]:
                    mag  = eq.get("Magnitude") or eq.get("mag") or eq.get("M") or "?"
                    loc  = eq.get("Location") or eq.get("location") or eq.get("Area") or "ไม่ระบุ"
                    date = eq.get("OriginTime") or eq.get("Date") or eq.get("date") or ""
                    try:
                        mag_f = float(mag)
                        c = "alert-critical" if mag_f >= 5.0 else "alert-warning" if mag_f >= 3.5 else "alert-info"
                    except:
                        c = "alert-info"
                    st.markdown(f"""
                    <div class='{c}'>
                        <p class='alert-card-title'>🌋 M {mag}</p>
                        <p class='alert-card-body'>📍 {loc}<br>
                        {"📅 " + str(date)[:16] if date else ""}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class='alert-ok'>
                    <p class='alert-card-title'>✅ ไม่มีเหตุการณ์แผ่นดินไหวใกล้เส้นทาง</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='alert-info'>
                <p class='alert-card-title'>ℹ️ ยังไม่ได้รับข้อมูลแผ่นดินไหว</p>
                <p class='alert-card-body'>ต้องการ API Token ที่ถูกต้องจาก TMD</p>
            </div>
            """, unsafe_allow_html=True)

        # Quick severity reference
        st.markdown('<p class="section-header">📋 เกณฑ์ปริมาณฝน (กรมอุตุฯ)</p>', unsafe_allow_html=True)
        criteria = [
            ("🌦️", "ฝนเล็กน้อย", "< 10 mm/วัน", "alert-info"),
            ("🌧️", "ฝนปานกลาง", "10–35 mm/วัน", "alert-info"),
            ("⛈️", "ฝนหนัก", "35–90 mm/วัน", "alert-warning"),
            ("🌊", "ฝนหนักมาก", "> 90 mm/วัน", "alert-critical"),
        ]
        for em, lv, mm, cls in criteria:
            st.markdown(f"""
            <div class='{cls}' style='padding:8px 14px;'>
                <p class='alert-card-body'>{em} <b>{lv}</b> — {mm}</p>
            </div>
            """, unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════╗
# ║  TAB 3 – STATION DETAIL                             ║
# ╚══════════════════════════════════════════════════════╝
with tab3:
    st.markdown('<p class="section-header">📊 สภาพอากาศแยกตามสายรถไฟ</p>', unsafe_allow_html=True)

    lines_to_show = [selected_line] if selected_line != "ทุกสาย" else list(RAIL_LINES.keys())

    for line_name in lines_to_show:
        stations = RAIL_LINES.get(line_name, [])
        # Determine line color
        line_colors_map = {
            "สายเหนือ": "#ef4444", "สายตะวันออกเฉียงเหนือ": "#f59e0b",
            "สายอีสานใต้": "#a78bfa", "สายใต้": "#34d399", "สายตะวันออก": "#60a5fa"
        }
        lc = "#5bc8ff"
        for k, v in line_colors_map.items():
            if k in line_name:
                lc = v
                break

        with st.expander(f"🛤️ {line_name} ({len(stations)} สถานี)", expanded=(selected_line != "ทุกสาย")):
            rows = []
            for s in stations:
                obs = find_nearest_station_data(s, obs_data or obs_3h)
                rain = get_rain_mm(obs) if obs else None
                temp = get_temp(obs) if obs else None
                wind = get_wind_speed(obs) if obs else None
                level_txt, emoji, badge = rain_level(rain)
                rows.append({
                    "สถานีรถไฟ": s["name"],
                    "จังหวัด": s["province"],
                    "ฝน (mm)": f"{rain:.1f}" if rain is not None else "N/A",
                    "ระดับ": f"{emoji} {level_txt}",
                    "อุณหภูมิ (°C)": f"{temp:.1f}" if temp is not None else "N/A",
                    "ลม (m/s)": f"{wind:.1f}" if wind is not None else "N/A",
                    "สถานีอุตุใกล้สุด": (obs.get("StationNameTh") or obs.get("name") or "N/A") if obs else "N/A",
                    "ระยะ (km)": obs.get("_distance_km", "N/A") if obs else "N/A",
                })

            if rows:
                df = pd.DataFrame(rows)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "ฝน (mm)": st.column_config.TextColumn("🌧️ ฝน (mm)"),
                        "ระดับ": st.column_config.TextColumn("⚠️ ระดับ"),
                        "อุณหภูมิ (°C)": st.column_config.TextColumn("🌡️ อุณหภูมิ"),
                        "ลม (m/s)": st.column_config.TextColumn("💨 ลม"),
                    }
                )

            # Summary metrics
            mc = st.columns(4)
            rain_vals = [float(r["ฝน (mm)"]) for r in rows if r["ฝน (mm)"] != "N/A"]
            temp_vals = [float(r["อุณหภูมิ (°C)"]) for r in rows if r["อุณหภูมิ (°C)"] != "N/A"]
            with mc[0]:
                st.metric("🌧️ ฝนสูงสุด", f"{max(rain_vals):.1f} mm" if rain_vals else "N/A")
            with mc[1]:
                st.metric("📊 ฝนเฉลี่ย", f"{sum(rain_vals)/len(rain_vals):.1f} mm" if rain_vals else "N/A")
            with mc[2]:
                st.metric("🌡️ อุณหภูมิเฉลี่ย", f"{sum(temp_vals)/len(temp_vals):.1f} °C" if temp_vals else "N/A")
            with mc[3]:
                heavy = sum(1 for v in rain_vals if v >= 35)
                st.metric("⛈️ ฝนหนัก", f"{heavy} สถานี")


# ╔══════════════════════════════════════════════════════╗
# ║  TAB 4 – 7-DAY FORECAST                             ║
# ╚══════════════════════════════════════════════════════╝
with tab4:
    st.markdown('<p class="section-header">🌐 พยากรณ์อากาศล่วงหน้า 7 วัน (รายภาค)</p>',
                unsafe_allow_html=True)

    REGION_MAP = {
        "ภาคเหนือ":                   ["สายเหนือ"],
        "ภาคตะวันออกเฉียงเหนือ":      ["สายตะวันออกเฉียงเหนือ", "สายอีสานใต้"],
        "ภาคกลาง":                    ["สายเหนือ", "สายตะวันออกเฉียงเหนือ"],
        "ภาคตะวันออก":                ["สายตะวันออก"],
        "ภาคใต้ฝั่งตะวันออก":         ["สายใต้"],
        "ภาคใต้ฝั่งตะวันตก":          ["สายใต้"],
    }

    if forecast_data:
        regions = None
        for k in ["WeatherForecasts", "forecasts", "data", "Regions"]:
            if k in forecast_data:
                regions = forecast_data[k]
                break
        if regions and isinstance(regions, list):
            for region in regions[:6]:
                region_name = (region.get("RegionNameTh") or region.get("region") or
                               region.get("Name") or "ภาค")
                related_lines = REGION_MAP.get(region_name, [])
                rel_txt = " · ".join([l.split("(")[0].strip() for l in related_lines]) if related_lines else ""

                with st.expander(f"🌏 {region_name}" + (f" → {rel_txt}" if rel_txt else ""), expanded=False):
                    forecasts = (region.get("Forecasts") or region.get("days") or
                                 region.get("DailyForecasts") or [])
                    if forecasts:
                        fc_rows = []
                        for day in forecasts[:7]:
                            fc_rows.append({
                                "วันที่": day.get("ForecastDate") or day.get("date") or "",
                                "สภาพอากาศ": day.get("Condition") or day.get("Weather") or day.get("cond") or "",
                                "ฝน": day.get("RainPercent") or day.get("rain") or day.get("RainfallPercent") or "",
                                "อุณหภูมิสูงสุด": day.get("MaxTemp") or day.get("max_temp") or "",
                                "อุณหภูมิต่ำสุด": day.get("MinTemp") or day.get("min_temp") or "",
                            })
                        if any(any(v for v in r.values()) for r in fc_rows):
                            st.dataframe(pd.DataFrame(fc_rows), use_container_width=True, hide_index=True)
                        else:
                            st.json(forecasts[:2])
                    else:
                        # Show raw keys
                        st.json({k: v for k, v in region.items() if k != "Forecasts"})
        else:
            # Try show raw
            st.json(str(forecast_data)[:500])
    else:
        # Show placeholder forecast UI
        st.info("ℹ️ กำลังรอข้อมูลพยากรณ์จาก TMD API · ตรวจสอบ Token หรือลองรีเฟรช")

        # Static example layout
        regions_demo = [
            ("ภาคเหนือ", "☁️ มีเมฆมาก", "สายเหนือ (กรุงเทพ–เชียงใหม่)"),
            ("ภาคตะวันออกเฉียงเหนือ", "⛈️ ฝนฟ้าคะนอง", "สายตะวันออกเฉียงเหนือ"),
            ("ภาคกลาง", "🌤️ มีเมฆบางส่วน", "ทุกสาย (กรุงเทพฯ)"),
            ("ภาคตะวันออก", "🌦️ ฝนเล็กน้อย", "สายตะวันออก"),
            ("ภาคใต้ฝั่งตะวันออก", "🌧️ ฝนตกต่อเนื่อง", "สายใต้"),
            ("ภาคใต้ฝั่งตะวันตก", "⛈️ ฝนหนักบางพื้นที่", "สายใต้"),
        ]
        cols_fc = st.columns(3)
        for i, (reg, cond, lines) in enumerate(regions_demo):
            with cols_fc[i % 3]:
                st.markdown(f"""
                <div class='metric-card'>
                    <h3>{reg}</h3>
                    <div class='value' style='font-size:1.1rem;'>{cond}</div>
                    <div class='unit' style='font-size:0.75rem; display:block; margin-top:4px;'>{lines}</div>
                </div>
                """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#3a5a7a; font-size:0.78rem; padding:8px 0;'>
    🚆 Thai Railway Network Weather Alert System &nbsp;|&nbsp;
    ข้อมูลสภาพอากาศจาก <a href='https://data.tmd.go.th' style='color:#5bc8ff;'>กรมอุตุนิยมวิทยา (TMD)</a> &nbsp;|&nbsp;
    โครงข่ายรถไฟจาก <a href='https://www.railway.co.th' style='color:#5bc8ff;'>การรถไฟแห่งประเทศไทย</a>
</div>
""", unsafe_allow_html=True)
