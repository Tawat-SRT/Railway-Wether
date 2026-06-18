"""
🚆 ระบบแจ้งเตือนสภาพอากาศโครงข่ายรถไฟไทย v3.0
Thai Railway Network Weather & Disaster Alert System
การรถไฟแห่งประเทศไทย × กรมอุตุนิยมวิทยา (TMD NWP API v1)
"""

import streamlit as st
import requests
import json
import math
import base64
import time
import pandas as pd
from datetime import datetime, timedelta
import pytz

# ══════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="SRT Weather Alert · ระบบแจ้งเตือนรถไฟ",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

TZ_TH = pytz.timezone("Asia/Bangkok")
NOW_TH = datetime.now(TZ_TH)

# ══════════════════════════════════════════════════════════════
#  THEME & CSS  (รถไฟ + ราง)
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;600;700;800&display=swap');

*, html, body, [class*="css"] { font-family: 'Sarabun', sans-serif !important; }

.stApp {
    background:
        repeating-linear-gradient(90deg, transparent 0 59px, rgba(255,255,255,0.012) 59px 60px),
        linear-gradient(180deg, #0b1622 0%, #0d1f33 60%, #0b1622 100%);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #060e18 0%, #0a1825 100%) !important;
    border-right: 2px solid #1a3a5c !important;
}
[data-testid="stSidebar"] * { color: #a8cce0 !important; }
[data-testid="stSidebar"]::after {
    content: '';
    position: fixed; bottom: 0; left: 0; width: 280px; height: 8px;
    background: repeating-linear-gradient(90deg, #c8a84b 0 20px, transparent 20px 30px);
    opacity: 0.4; z-index: 999;
}

/* Header */
.rail-header {
    background: linear-gradient(135deg, #0d2137 0%, #0a3060 40%, #0d2137 100%);
    border: 1px solid #1a4a7a;
    border-left: 6px solid #c8a84b;
    border-radius: 0 12px 12px 0;
    padding: 20px 28px;
    margin-bottom: 16px;
    position: relative; overflow: hidden;
}
.rail-header::before, .rail-header::after {
    content: ''; position: absolute; left: 0; right: 0; height: 3px;
    background: repeating-linear-gradient(90deg, #c8a84b 0 24px, transparent 24px 32px);
}
.rail-header::before { top: 0; }
.rail-header::after  { bottom: 0; }
.rail-header h1 {
    color: #fff !important; font-size: 1.75rem !important; font-weight: 800 !important;
    margin: 0 0 4px 0 !important; text-shadow: 0 2px 12px rgba(91,200,255,0.3);
}
.rail-header p { color: #7ec8e3 !important; font-size: 0.86rem !important; margin: 0 !important; }
.rail-header .stamp {
    position: absolute; right: 24px; top: 50%; transform: translateY(-50%);
    color: rgba(200,168,75,0.12); font-size: 6rem; font-weight: 900; line-height: 1;
    user-select: none;
}

/* KPI cards */
.kpi-grid { display: flex; gap: 10px; flex-wrap: wrap; }
.kpi-card {
    flex: 1; min-width: 140px;
    background: linear-gradient(135deg, rgba(13,33,55,0.95), rgba(8,24,44,0.95));
    border: 1px solid #1a3a5c;
    border-top: 3px solid var(--accent, #5bc8ff);
    border-radius: 10px; padding: 14px 16px;
    transition: box-shadow 0.2s, transform 0.1s;
}
.kpi-card:hover { box-shadow: 0 4px 20px rgba(91,200,255,0.15); transform: translateY(-1px); }
.kpi-card .kpi-icon { font-size: 1.4rem; margin-bottom: 4px; display: block; }
.kpi-card .kpi-label { color: #6899b8; font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 3px; }
.kpi-card .kpi-value { color: #fff; font-size: 1.6rem; font-weight: 800; line-height: 1; }
.kpi-card .kpi-sub   { color: #7ec8e3; font-size: 0.72rem; margin-top: 3px; }
.kpi-red    { --accent: #ef4444; }
.kpi-orange { --accent: #f59e0b; }
.kpi-blue   { --accent: #3b82f6; }
.kpi-green  { --accent: #10b981; }
.kpi-gold   { --accent: #c8a84b; }
.kpi-purple { --accent: #a78bfa; }

/* Alert cards */
.alert-card {
    border-radius: 9px; padding: 12px 16px; margin: 5px 0;
    border-left: 4px solid; border: 1px solid;
}
.alert-critical { background: rgba(220,38,38,0.12); border-color: rgba(220,38,38,0.35); border-left-color: #ef4444; }
.alert-warning  { background: rgba(245,158,11,0.10); border-color: rgba(245,158,11,0.35); border-left-color: #f59e0b; }
.alert-info     { background: rgba(59,130,246,0.10); border-color: rgba(59,130,246,0.30); border-left-color: #3b82f6; }
.alert-ok       { background: rgba(16,185,129,0.08); border-color: rgba(16,185,129,0.25); border-left-color: #10b981; }
.alert-card-title { color: #fff; font-weight: 700; font-size: 0.94rem; margin: 0 0 3px 0; }
.alert-card-body  { color: #a8cce0; font-size: 0.83rem; margin: 0; line-height: 1.5; }
.alert-card-meta  { color: #5a8099; font-size: 0.72rem; margin-top: 4px; }

/* Section title */
.sec-title {
    color: #5bc8ff; font-size: 1.0rem; font-weight: 700;
    border-bottom: 1px solid rgba(91,200,255,0.2);
    padding-bottom: 6px; margin: 16px 0 10px 0;
}

/* Badges */
.badge { display: inline-block; padding: 2px 9px; border-radius: 12px; font-size: 0.7rem; font-weight: 700; }
.badge-critical { background: #7f1d1d; color: #fca5a5; border: 1px solid #ef4444; }
.badge-high     { background: #78350f; color: #fde68a; border: 1px solid #f59e0b; }
.badge-medium   { background: #1e3a5f; color: #93c5fd; border: 1px solid #3b82f6; }
.badge-low      { background: #064e3b; color: #6ee7b7; border: 1px solid #10b981; }
.badge-na       { background: #1e2a35; color: #6899b8; border: 1px solid #2a4a62; }

/* Progress bar */
.prog-wrap { background: rgba(255,255,255,0.06); border-radius: 6px; height: 7px; overflow: hidden; margin-top: 3px; }
.prog-fill  { height: 100%; border-radius: 6px; transition: width 0.4s; }

/* Streamlit overrides */
div[data-testid="stMetric"] {
    background: rgba(13,33,55,0.8) !important;
    border: 1px solid rgba(91,200,255,0.15) !important;
    border-radius: 10px !important; padding: 12px 14px !important;
}
div[data-testid="stMetric"] label { color: #6899b8 !important; font-size: 0.76rem !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #fff !important; font-weight: 700 !important; }

.stTabs [data-baseweb="tab-list"] {
    background: rgba(13,33,55,0.6) !important;
    border-radius: 10px !important; gap: 4px !important; padding: 4px !important;
    border: 1px solid rgba(91,200,255,0.1) !important;
}
.stTabs [data-baseweb="tab"] { color: #6899b8 !important; border-radius: 7px !important; padding: 6px 16px !important; }
.stTabs [aria-selected="true"] { background: rgba(91,200,255,0.15) !important; color: #5bc8ff !important; }

div[data-testid="stExpander"] {
    background: rgba(13,33,55,0.5) !important;
    border: 1px solid rgba(91,200,255,0.12) !important;
    border-radius: 10px !important;
}
div[data-testid="stExpander"] summary { color: #7ec8e3 !important; }

.stButton > button {
    background: linear-gradient(135deg, #0a3060, #0d4080) !important;
    color: #d0e8f8 !important; border: 1px solid rgba(91,200,255,0.3) !important;
    border-radius: 8px !important; font-weight: 600 !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #0d4080, #1055a0) !important;
    box-shadow: 0 0 14px rgba(91,200,255,0.25) !important;
}

div[data-baseweb="select"] > div {
    background: rgba(10,25,45,0.8) !important;
    border-color: rgba(91,200,255,0.2) !important;
}
div[data-baseweb="select"] * { color: #a8cce0 !important; }

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: #060e18; }
::-webkit-scrollbar-thumb { background: #1a3a5c; border-radius: 3px; }

.dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 6px; }
.dot-green  { background: #10b981; box-shadow: 0 0 6px #10b981; }
.dot-red    { background: #ef4444; box-shadow: 0 0 6px #ef4444; }
.dot-yellow { background: #f59e0b; box-shadow: 0 0 6px #f59e0b; }
.dot-grey   { background: #4a6070; }

.dash-box {
    background: linear-gradient(135deg, rgba(13,33,55,0.9), rgba(8,20,38,0.95));
    border: 1px solid rgba(91,200,255,0.15);
    border-radius: 12px; padding: 16px 20px; height: 100%;
}
.dash-box h4 {
    color: #5bc8ff; font-size: 0.8rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.7px;
    margin: 0 0 10px 0;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  TOKEN MANAGEMENT  (session_state-backed)
# ══════════════════════════════════════════════════════════════
def _decode_jwt(token):
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload))
    except Exception:
        return {}

def _set_token(raw):
    raw = (raw or "").strip()
    st.session_state["_tk"]      = raw
    st.session_state["_tk_jwt"]  = _decode_jwt(raw)
    st.session_state["_tk_uid"]  = str(st.session_state["_tk_jwt"].get("sub", ""))

# Bootstrap from secrets or env
if "_tk" not in st.session_state:
    _boot = ""
    try:
        _boot = str(st.secrets.get("TMD_TOKEN", "") or st.secrets.get("tmd_token", ""))
    except Exception:
        pass
    if not _boot:
        import os
        _boot = os.environ.get("TMD_TOKEN", "")
    _set_token(_boot)

def _token():    return st.session_state.get("_tk", "")
def _uid():    return st.session_state.get("_tk_uid", "")
def _jwt():   return st.session_state.get("_tk_jwt", {})

# ══════════════════════════════════════════════════════════════
#  SRT RAILWAY NETWORK  (datagov.mot.go.th, updated 2026)
# ══════════════════════════════════════════════════════════════
SRT_LINES = {
    "สายเหนือ": {
        "color": "#ef4444", "short": "N", "icon": "🔴",
        "desc": "กรุงเทพ → เชียงใหม่ · 751 กม.",
        "stations": [
            {"name":"กรุงเทพ (หัวลำโพง)","lat":13.7401,"lon":100.5178,"province":"กรุงเทพมหานคร","km":0},
            {"name":"ดอนเมือง","lat":13.9186,"lon":100.5970,"province":"กรุงเทพมหานคร","km":22},
            {"name":"รังสิต","lat":14.0262,"lon":100.6162,"province":"ปทุมธานี","km":43},
            {"name":"อยุธยา","lat":14.3554,"lon":100.5679,"province":"พระนครศรีอยุธยา","km":71},
            {"name":"ลพบุรี","lat":14.7987,"lon":100.6141,"province":"ลพบุรี","km":133},
            {"name":"นครสวรรค์","lat":15.7028,"lon":100.1363,"province":"นครสวรรค์","km":246},
            {"name":"พิจิตร","lat":16.4365,"lon":100.3485,"province":"พิจิตร","km":347},
            {"name":"พิษณุโลก","lat":16.8204,"lon":100.2714,"province":"พิษณุโลก","km":389},
            {"name":"อุตรดิตถ์","lat":17.6236,"lon":100.0987,"province":"อุตรดิตถ์","km":485},
            {"name":"เด่นชัย","lat":17.9827,"lon":100.0569,"province":"แพร่","km":535},
            {"name":"ลำปาง","lat":18.2896,"lon":99.4905,"province":"ลำปาง","km":642},
            {"name":"ลำพูน","lat":18.5746,"lon":99.0094,"province":"ลำพูน","km":703},
            {"name":"เชียงใหม่","lat":18.7883,"lon":98.9933,"province":"เชียงใหม่","km":751},
        ],
    },
    "สายตะวันออกเฉียงเหนือ": {
        "color": "#f59e0b", "short": "NE", "icon": "🟡",
        "desc": "กรุงเทพ → หนองคาย · 624 กม.",
        "stations": [
            {"name":"กรุงเทพ (หัวลำโพง)","lat":13.7401,"lon":100.5178,"province":"กรุงเทพมหานคร","km":0},
            {"name":"สระบุรี (ชุมทาง)","lat":14.5291,"lon":100.9101,"province":"สระบุรี","km":107},
            {"name":"ปากช่อง","lat":14.7043,"lon":101.4180,"province":"นครราชสีมา","km":180},
            {"name":"นครราชสีมา","lat":14.9734,"lon":102.1112,"province":"นครราชสีมา","km":264},
            {"name":"บัวใหญ่","lat":15.5887,"lon":102.4242,"province":"นครราชสีมา","km":361},
            {"name":"ขอนแก่น","lat":16.4419,"lon":102.8330,"province":"ขอนแก่น","km":449},
            {"name":"อุดรธานี","lat":17.4043,"lon":102.7877,"province":"อุดรธานี","km":569},
            {"name":"หนองคาย","lat":17.8818,"lon":102.7433,"province":"หนองคาย","km":624},
        ],
    },
    "สายอีสานใต้": {
        "color": "#a78bfa", "short": "IS", "icon": "🟣",
        "desc": "นครราชสีมา → อุบลราชธานี · 305 กม.",
        "stations": [
            {"name":"นครราชสีมา (ถนนจิระ)","lat":14.9734,"lon":102.1112,"province":"นครราชสีมา","km":0},
            {"name":"บุรีรัมย์","lat":14.9950,"lon":103.1030,"province":"บุรีรัมย์","km":101},
            {"name":"สุรินทร์","lat":14.8835,"lon":103.4935,"province":"สุรินทร์","km":142},
            {"name":"ศีขรภูมิ","lat":14.9466,"lon":103.7889,"province":"สุรินทร์","km":175},
            {"name":"ศรีสะเกษ","lat":15.1174,"lon":104.3221,"province":"ศรีสะเกษ","km":237},
            {"name":"อุบลราชธานี","lat":15.2241,"lon":104.8579,"province":"อุบลราชธานี","km":305},
        ],
    },
    "สายใต้": {
        "color": "#34d399", "short": "S", "icon": "🟢",
        "desc": "กรุงเทพ → สุไหงโก-ลก · 1,144 กม.",
        "stations": [
            {"name":"กรุงเทพ (หัวลำโพง)","lat":13.7401,"lon":100.5178,"province":"กรุงเทพมหานคร","km":0},
            {"name":"นครปฐม","lat":13.8199,"lon":100.0597,"province":"นครปฐม","km":56},
            {"name":"ราชบุรี","lat":13.5361,"lon":99.8163,"province":"ราชบุรี","km":117},
            {"name":"เพชรบุรี","lat":13.1093,"lon":99.9494,"province":"เพชรบุรี","km":167},
            {"name":"หัวหิน","lat":12.5675,"lon":99.9576,"province":"ประจวบคีรีขันธ์","km":229},
            {"name":"ประจวบคีรีขันธ์","lat":11.8121,"lon":99.7962,"province":"ประจวบคีรีขันธ์","km":318},
            {"name":"ชุมพร","lat":10.4930,"lon":99.1800,"province":"ชุมพร","km":485},
            {"name":"สุราษฎร์ธานี","lat":9.1400,"lon":99.3300,"province":"สุราษฎร์ธานี","km":651},
            {"name":"นครศรีธรรมราช","lat":8.4330,"lon":99.9630,"province":"นครศรีธรรมราช","km":832},
            {"name":"หาดใหญ่","lat":7.0080,"lon":100.4740,"province":"สงขลา","km":945},
            {"name":"ปาดังเบซาร์","lat":6.6735,"lon":100.3781,"province":"สงขลา","km":991},
            {"name":"สุไหงโก-ลก","lat":6.0277,"lon":101.9784,"province":"นราธิวาส","km":1144},
        ],
    },
    "สายตะวันออก": {
        "color": "#60a5fa", "short": "E", "icon": "🔵",
        "desc": "กรุงเทพ → อรัญประเทศ · 255 กม.",
        "stations": [
            {"name":"กรุงเทพ (มักกะสัน)","lat":13.7524,"lon":100.5684,"province":"กรุงเทพมหานคร","km":0},
            {"name":"ฉะเชิงเทรา","lat":13.6903,"lon":101.0768,"province":"ฉะเชิงเทรา","km":61},
            {"name":"ชลบุรี","lat":13.3639,"lon":100.9905,"province":"ชลบุรี","km":120},
            {"name":"พัทยา","lat":12.9236,"lon":100.8825,"province":"ชลบุรี","km":154},
            {"name":"มาบตาพุด","lat":12.6793,"lon":101.1500,"province":"ระยอง","km":179},
            {"name":"อรัญประเทศ","lat":13.6942,"lon":102.5062,"province":"สระแก้ว","km":255},
        ],
    },
}

# Flatten unique stations
_seen = set()
ALL_STATIONS = []
for _ln, _ld in SRT_LINES.items():
    for _s in _ld["stations"]:
        if _s["name"] not in _seen:
            _seen.add(_s["name"])
            ALL_STATIONS.append({**_s, "line": _ln, "line_color": _ld["color"],
                                  "line_short": _ld["short"], "line_icon": _ld["icon"]})

# ══════════════════════════════════════════════════════════════
#  TMD NWP API v1  (Bearer token)
#  Docs: https://data.tmd.go.th/nwpapi/doc/main/getting_start.html
# ══════════════════════════════════════════════════════════════
TMD_NWP_BASE = "https://data.tmd.go.th/nwpapi/v1"

def _nwp_get(path, params, token):
    """Call NWP API endpoint. Returns (data, error_msg). data=None on error."""
    if not token:
        return None, "ไม่มี Token"
    url = f"{TMD_NWP_BASE}/{path.lstrip('/')}"
    headers = {
        "accept": "application/json",
        "authorization": f"Bearer {token}",
    }
    for attempt in range(2):
        try:
            r = requests.get(url, headers=headers, params=params,
                             timeout=15, allow_redirects=True)
            if r.status_code == 200:
                try:
                    return r.json(), ""
                except Exception:
                    return None, f"Response 200 but not JSON: {r.text[:80]}"
            elif r.status_code in (401, 403):
                return None, f"HTTP {r.status_code}: Token ไม่ถูกต้องหรือหมดอายุ"
            elif r.status_code == 404:
                return None, f"HTTP 404: ไม่พบ endpoint {path}"
            elif r.status_code == 429:
                return None, "HTTP 429: เรียก API บ่อยเกินไป (rate limit)"
            elif r.status_code >= 500:
                if attempt < 1:
                    time.sleep(1.0)
                    continue
                return None, f"HTTP {r.status_code}: เซิร์ฟเวอร์ TMD มีปัญหา"
            else:
                return None, f"HTTP {r.status_code}"
        except requests.exceptions.Timeout:
            if attempt < 1:
                continue
            return None, "Timeout (15s) — เซิร์ฟเวอร์ตอบช้า"
        except requests.exceptions.ConnectionError as e:
            return None, f"ConnectionError: {str(e)[:80]}"
        except Exception as e:
            return None, f"{type(e).__name__}: {str(e)[:80]}"
    return None, "Unknown error"


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_daily_at(lat, lon, token, days=3):
    """พยากรณ์รายวันที่ตำแหน่ง lat/lon"""
    today_str = NOW_TH.strftime("%Y-%m-%d")
    params = {
        "lat": lat, "lon": lon,
        "fields": "tc_max,tc_min,rh,rain,cond,wd,ws",
        "date": today_str,
        "duration": days,
    }
    data, _err = _nwp_get("forecast/location/daily/at", params, token)
    return data


@st.cache_data(ttl=900, show_spinner=False)
def fetch_hourly_at(lat, lon, token, hours=24):
    """พยากรณ์ราย ชม. ที่ตำแหน่ง lat/lon"""
    today_str = NOW_TH.strftime("%Y-%m-%d")
    params = {
        "lat": lat, "lon": lon,
        "fields": "tc,rh,rain,cond,ws",
        "date": today_str,
        "hour": 0,
        "duration": hours,
    }
    data, _err = _nwp_get("forecast/location/hourly/at", params, token)
    return data


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_token_test(token):
    """ทดสอบ token ว่าใช้งานได้หรือไม่"""
    if not token:
        return False, "ไม่มี Token"
    # ลองดึงข้อมูลกรุงเทพฯ
    params = {
        "lat": 13.7563, "lon": 100.5018,
        "fields": "tc",
        "date": NOW_TH.strftime("%Y-%m-%d"),
        "duration": 1,
    }
    data, err = _nwp_get("forecast/location/daily/at", params, token)
    if data and isinstance(data, dict):
        return True, "OK"
    return False, err


# ══════════════════════════════════════════════════════════════
#  HELPERS — parse NWP API response
# ══════════════════════════════════════════════════════════════
def parse_daily_forecast(data):
    """แปลง response เป็น list ของ forecasts รายวัน"""
    if not data or not isinstance(data, dict):
        return []
    wf = data.get("WeatherForecasts") or data.get("forecasts") or []
    if not wf:
        return []
    forecasts = wf[0].get("forecasts", []) if isinstance(wf, list) else []
    result = []
    for f in forecasts:
        d = f.get("data", {}) if isinstance(f, dict) else {}
        result.append({
            "time": f.get("time", "") if isinstance(f, dict) else "",
            "tc_max": d.get("tc_max"),
            "tc_min": d.get("tc_min"),
            "rh":     d.get("rh"),
            "rain":   d.get("rain"),
            "cond":   d.get("cond"),
            "wd":     d.get("wd"),
            "ws":     d.get("ws"),
        })
    return result


def parse_hourly_forecast(data):
    """แปลง response เป็น list ของ forecasts รายชั่วโมง"""
    if not data or not isinstance(data, dict):
        return []
    wf = data.get("WeatherForecasts") or []
    if not wf:
        return []
    forecasts = wf[0].get("forecasts", []) if isinstance(wf, list) else []
    result = []
    for f in forecasts:
        d = f.get("data", {}) if isinstance(f, dict) else {}
        result.append({
            "time": f.get("time", "") if isinstance(f, dict) else "",
            "tc":   d.get("tc"),
            "rh":   d.get("rh"),
            "rain": d.get("rain"),
            "cond": d.get("cond"),
            "ws":   d.get("ws"),
        })
    return result


# TMD weather condition codes
COND_MAP = {
    1:"ท้องฟ้าแจ่มใส ☀️", 2:"มีเมฆบางส่วน 🌤️", 3:"เมฆเป็นส่วนมาก ⛅",
    4:"มีเมฆมาก ☁️",     5:"ฝนตกเล็กน้อย 🌦️",  6:"ฝนปานกลาง 🌧️",
    7:"ฝนตกหนัก ⛈️",     8:"ฝนฟ้าคะนอง ⛈️",    9:"อากาศหนาวจัด ❄️",
    10:"อากาศหนาว 🥶",    11:"อากาศเย็น 😎",     12:"อากาศร้อนจัด 🥵",
}

def cond_text(cond_code):
    try:
        return COND_MAP.get(int(cond_code), f"รหัส {cond_code}")
    except Exception:
        return "—"


# ══════════════════════════════════════════════════════════════
#  RISK CLASSIFICATION
# ══════════════════════════════════════════════════════════════
def risk_class(rain_mm):
    """Returns (label_th, emoji, badge_class, alert_class)"""
    if rain_mm is None:
        return "ไม่มีข้อมูล", "⚪", "badge-na", "alert-info"
    try:
        rain_mm = float(rain_mm)
    except Exception:
        return "ไม่มีข้อมูล", "⚪", "badge-na", "alert-info"
    if rain_mm <= 0:    return "ปกติ",         "☀️", "badge-low",      "alert-ok"
    if rain_mm < 10:    return "ฝนเล็กน้อย",   "🌦️", "badge-low",      "alert-ok"
    if rain_mm < 35:    return "ฝนปานกลาง",    "🌧️", "badge-medium",   "alert-info"
    if rain_mm < 90:    return "ฝนหนัก ⚠️",    "⛈️", "badge-high",     "alert-warning"
    return                     "ฝนหนักมาก 🚨", "🌊", "badge-critical", "alert-critical"

def risk_color_hex(rain_mm):
    if rain_mm is None: return "#4a6070"
    try:    rain_mm = float(rain_mm)
    except: return "#4a6070"
    if rain_mm < 10:    return "#10b981"
    if rain_mm < 35:    return "#3b82f6"
    if rain_mm < 90:    return "#f59e0b"
    return "#ef4444"


# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:16px 0 18px;'>
        <div style='font-size:3rem;'>🚆</div>
        <div style='color:#5bc8ff;font-size:1.05rem;font-weight:800;letter-spacing:0.4px;'>SRT Weather Alert</div>
        <div style='color:#4a7090;font-size:0.74rem;'>ระบบแจ้งเตือนสภาพอากาศ</div>
        <div style='color:#4a7090;font-size:0.74rem;'>โครงข่ายรถไฟแห่งประเทศไทย</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Token panel ────────────────────────────────────────────
    if _token():
        _jwt_data = _jwt()
        _exp_ts = _jwt_data.get("exp", 0)
        _exp_dt = datetime.fromtimestamp(_exp_ts, tz=TZ_TH) if _exp_ts else None
        _days   = (_exp_dt - NOW_TH).days if _exp_dt else 0
        _color  = "#10b981" if _days > 30 else "#f59e0b" if _days > 0 else "#ef4444"
        st.markdown(f"""
        <div style='background:rgba(10,20,35,0.85);border:1px solid rgba(91,200,255,0.18);
            border-radius:8px;padding:10px 14px;margin-bottom:12px;'>
            <div style='color:#4a7090;font-size:0.71rem;'>🔑 TMD NWP API Token</div>
            <div style='color:#5bc8ff;font-size:0.82rem;font-weight:600;'>
                uid: <b style='color:#fff;'>{_uid()}</b>
            </div>
            <div style='color:{_color};font-size:0.74rem;margin-top:2px;'>
                {"✅ ใช้งานได้" if _days > 0 else "❌ หมดอายุแล้ว"}
                {f" · เหลือ {_days} วัน" if _days > 0 else ""}
            </div>
        </div>""", unsafe_allow_html=True)

        if st.button("🔄 เปลี่ยน Token", use_container_width=True, key="btn_change"):
            _set_token("")
            st.cache_data.clear()
            st.rerun()
    else:
        st.markdown("<div style='color:#ef4444;font-size:0.8rem;margin-bottom:6px;'>⚠️ ยังไม่ได้ใส่ Token</div>",
                    unsafe_allow_html=True)
        _t_in = st.text_input("Token", type="password",
            placeholder="eyJ0eXAiOiJKV1Qi...", label_visibility="collapsed",
            help="JWT token จาก https://data.tmd.go.th/nwpapi")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ ใช้งาน", use_container_width=True, key="btn_use_tk"):
                if _t_in.strip():
                    _set_token(_t_in.strip())
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("กรุณาใส่ Token")
        with c2:
            st.markdown("<a href='https://data.tmd.go.th/nwpapi/doc/main/getting_start.html' "
                        "target='_blank' style='font-size:0.74rem;color:#5bc8ff;text-decoration:none;'>"
                        "📖 คู่มือ</a>", unsafe_allow_html=True)

    st.markdown("---")

    # ── Line filter ────────────────────────────────────────────
    st.markdown("<div style='color:#5bc8ff;font-size:0.76rem;font-weight:700;"
                "text-transform:uppercase;letter-spacing:0.7px;margin-bottom:5px;'>"
                "🛤️ เส้นทาง</div>", unsafe_allow_html=True)
    sel_line = st.selectbox("เส้นทาง", ["ทุกสาย"] + list(SRT_LINES.keys()),
                             label_visibility="collapsed")

    st.markdown("<div style='color:#5bc8ff;font-size:0.76rem;font-weight:700;"
                "text-transform:uppercase;letter-spacing:0.7px;margin:10px 0 5px;'>"
                "⚠️ ระดับการแจ้งเตือน</div>", unsafe_allow_html=True)
    sel_thresh = st.select_slider("ระดับ",
        ["ทั้งหมด","ฝนเล็กน้อย","ฝนปานกลาง","ฝนหนัก","ฝนหนักมาก"],
        value="ทั้งหมด", label_visibility="collapsed")

    st.markdown("<div style='color:#5bc8ff;font-size:0.76rem;font-weight:700;"
                "text-transform:uppercase;letter-spacing:0.7px;margin:10px 0 5px;'>"
                "📅 ช่วงเวลา</div>", unsafe_allow_html=True)
    sel_horizon = st.radio("วัน", ["วันนี้","พรุ่งนี้","มะรืน"],
                            horizontal=True, label_visibility="collapsed")

    st.markdown("---")
    st.markdown(f"""
    <div style='color:#4a7090;font-size:0.74rem;line-height:1.8;'>
        🕐 เวลาไทย<br>
        <span style='color:#5bc8ff;font-size:0.94rem;font-weight:700;'>
            {NOW_TH.strftime('%d %b %Y · %H:%M')} น.
        </span><br>
        <span style='color:#2a5070;'>อัพเดตทุก 15–30 นาที</span>
    </div>""", unsafe_allow_html=True)

    if st.button("🔄 รีเฟรชข้อมูล", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")
    for _ln, _ld in SRT_LINES.items():
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:8px;margin:3px 0;'>
            <div style='width:26px;height:4px;border-radius:2px;background:{_ld["color"]};'></div>
            <span style='color:#6899b8;font-size:0.74rem;'>{_ld["short"]} {_ln}</span>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style='color:#2a4060;font-size:0.68rem;margin-top:14px;line-height:1.7;'>
        ข้อมูลอุตุฯ: <b>TMD NWP API v1</b><br>
        โครงข่าย: รฟท. (datagov.mot.go.th)<br>
        v3.0 · มิถุนายน 2569
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  TEST TOKEN + LOAD STATION DATA
# ══════════════════════════════════════════════════════════════
_horizon_index = {"วันนี้":0, "พรุ่งนี้":1, "มะรืน":2}[sel_horizon]
_api_ok, _api_err = (False, "ไม่มี Token")
if _token():
    _api_ok, _api_err = fetch_token_test(_token())

# ── Build filtered + deduplicated station list ────────────────
_filtered_stations = []
_seen_names = set()
for _ln, _ld in SRT_LINES.items():
    if sel_line != "ทุกสาย" and _ln != sel_line:
        continue
    for _s in _ld["stations"]:
        if _s["name"] in _seen_names:
            continue
        _seen_names.add(_s["name"])
        _filtered_stations.append({**_s, "line": _ln, "line_color": _ld["color"],
                                    "line_short": _ld["short"], "line_icon": _ld["icon"]})

# ── Fetch weather for a batch of stations (cached) ────────────
# NOTE: _nwp_get is plain (not cached) so nesting here is safe.
@st.cache_data(ttl=1800, show_spinner=False)
def fetch_station_batch(stations_tuple, token, horizon_idx):
    """ดึงพยากรณ์รายวันของหลายสถานีในครั้งเดียว (cache ตาม token+ช่วงเวลา)"""
    results = []
    for s_json in stations_tuple:
        s = json.loads(s_json)
        chosen = {}
        if token:
            today_str = NOW_TH.strftime("%Y-%m-%d")
            params = {
                "lat": s["lat"], "lon": s["lon"],
                "fields": "tc_max,tc_min,rh,rain,cond,wd,ws",
                "date": today_str, "duration": 3,
            }
            _d, _e = _nwp_get("forecast/location/daily/at", params, token)
            _fc = parse_daily_forecast(_d)
            if _fc:
                chosen = _fc[horizon_idx] if horizon_idx < len(_fc) else _fc[0]
        results.append({
            "name":      s["name"],
            "lat":       s["lat"],
            "lon":       s["lon"],
            "province":  s["province"],
            "km":        s.get("km", 0),
            "line":      s["line"],
            "line_color":s["line_color"],
            "line_short":s["line_short"],
            "line_icon": s["line_icon"],
            "rain":      chosen.get("rain"),
            "tc_max":    chosen.get("tc_max"),
            "tc_min":   chosen.get("tc_min"),
            "rh":       chosen.get("rh"),
            "cond":     chosen.get("cond"),
            "wd":       chosen.get("wd"),
            "ws":       chosen.get("ws"),
            "time":     chosen.get("time", ""),
        })
    return results

# Build station data
_stns_tuple = tuple(json.dumps(s, ensure_ascii=False) for s in _filtered_stations)
with st.spinner(f"⏳ กำลังดึงข้อมูลพยากรณ์ {len(_filtered_stations)} สถานี... (ใช้เวลา 10-30 วินาที)"):
    station_data = fetch_station_batch(_stns_tuple, _token(), _horizon_index) if _api_ok else []
    if not _api_ok:
        # Build placeholder data so UI still renders
        station_data = [{**s, "rain":None, "tc_max":None, "tc_min":None, "rh":None,
                         "cond":None, "wd":None, "ws":None, "time":""} for s in _filtered_stations]

# Aggregate metrics
_THRESH = {"ทั้งหมด":0, "ฝนเล็กน้อย":1, "ฝนปานกลาง":10, "ฝนหนัก":35, "ฝนหนักมาก":90}
_min_rain = _THRESH.get(sel_thresh, 0)

_all_rains = [s["rain"] for s in station_data if s["rain"] is not None]
_all_temps = [s["tc_max"] for s in station_data if s["tc_max"] is not None]
_n_critical = sum(1 for r in _all_rains if r >= 90)
_n_heavy    = sum(1 for r in _all_rains if 35 <= r < 90)
_n_medium   = sum(1 for r in _all_rains if 10 <= r < 35)
_n_ok       = sum(1 for r in _all_rains if r < 10)
_max_rain   = max(_all_rains) if _all_rains else None
_avg_rain   = round(sum(_all_rains)/len(_all_rains), 1) if _all_rains else None
_avg_temp   = round(sum(_all_temps)/len(_all_temps), 1) if _all_temps else None

# ══════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<div class='rail-header'>
    <div class='stamp'>🚂</div>
    <h1>🚆 ระบบแจ้งเตือนสภาพอากาศโครงข่ายรถไฟไทย</h1>
    <p>Thai Railway Network Weather & Disaster Alert System
    · การรถไฟแห่งประเทศไทย (SRT) × กรมอุตุนิยมวิทยา (TMD)
    · ข้อมูล {sel_horizon} · อัพเดต {NOW_TH.strftime('%d %b %Y %H:%M')} น.</p>
</div>""", unsafe_allow_html=True)

# Status bar
_dot = '<span class="dot dot-green"></span>' if _api_ok else '<span class="dot dot-red"></span>'
st.markdown(f"""
<div style='display:flex;align-items:center;gap:18px;background:rgba(10,20,35,0.7);
    border:1px solid rgba(91,200,255,0.1);border-radius:8px;padding:8px 18px;
    margin-bottom:14px;flex-wrap:wrap;'>
    <span style='font-size:0.8rem;color:#6899b8;'>{_dot}
        <b style='color:{"#10b981" if _api_ok else "#ef4444"};'>
            {"✅ TMD NWP API เชื่อมต่อสำเร็จ" if _api_ok else "❌ API ไม่ตอบสนอง"}
        </b>
        <span style='color:#4a7090;'>{("· " + _api_err) if not _api_ok and _api_err else ""}</span>
    </span>
    <span style='font-size:0.8rem;color:#6899b8;'>🛤️ สาย: <b style='color:#a8cce0;'>{sel_line}</b></span>
    <span style='font-size:0.8rem;color:#6899b8;'>📍 สถานี: <b style='color:#a8cce0;'>{len(station_data)}</b></span>
    <span style='font-size:0.8rem;color:#6899b8;'>📅 พยากรณ์: <b style='color:#a8cce0;'>{sel_horizon}</b></span>
    <span style='font-size:0.8rem;color:#6899b8;'>⚠️ เกณฑ์: <b style='color:#a8cce0;'>{sel_thresh}</b></span>
</div>""", unsafe_allow_html=True)

# Show diagnostic if API failed
if not _api_ok and _token():
    with st.expander("🔍 รายละเอียดข้อผิดพลาด API", expanded=False):
        st.code(f"""
URL Base    : {TMD_NWP_BASE}
Endpoint    : forecast/location/daily/at
Auth Header : Bearer {_token()[:30]}...{_token()[-10:]}
UID (sub)   : {_uid()}
Error       : {_api_err}

หากเห็น 'Host not in allowlist' = network ภายนอกถูกบล็อก
หากเห็น HTTP 401/403 = Token ไม่ถูกต้องหรือหมดอายุ
หากเห็น Timeout = เซิร์ฟเวอร์ TMD ตอบช้าหรือล่ม
""")

# ══════════════════════════════════════════════════════════════
#  MAIN TABS
# ══════════════════════════════════════════════════════════════
tab_exec, tab_map, tab_alert, tab_line, tab_forecast = st.tabs([
    "📊 Executive Dashboard",
    "🗺️ แผนที่",
    "⚠️ แจ้งเตือนภัย",
    "🛤️ รายสาย",
    "🌤️ พยากรณ์ละเอียด",
])

# ╔══════════════════════════════════════════════════════════╗
# ║  TAB 1 — EXECUTIVE DASHBOARD                            ║
# ╚══════════════════════════════════════════════════════════╝
with tab_exec:
    # KPI Row
    _kc = st.columns(6)
    _kpi_data = [
        ("🚨","ฝนหนักมาก",str(_n_critical),"สถานี","kpi-red"),
        ("⛈️","ฝนหนัก",str(_n_heavy),"สถานี","kpi-orange"),
        ("🌧️","ฝนปานกลาง",str(_n_medium),"สถานี","kpi-blue"),
        ("☀️","ปกติ/เล็กน้อย",str(_n_ok),"สถานี","kpi-green"),
        ("💧","ฝนสูงสุด",f"{_max_rain:.1f}" if _max_rain is not None else "—","mm","kpi-gold"),
        ("🌡️","อุณหภูมิเฉลี่ย",f"{_avg_temp}" if _avg_temp is not None else "—","°C","kpi-purple"),
    ]
    for col, (icon, label, val, unit, cls) in zip(_kc, _kpi_data):
        with col:
            st.markdown(f"""
            <div class='kpi-card {cls}'>
                <span class='kpi-icon'>{icon}</span>
                <div class='kpi-label'>{label}</div>
                <div class='kpi-value'>{val}<span style='font-size:0.78rem;color:#7ec8e3;margin-left:3px;'>{unit}</span></div>
            </div>""", unsafe_allow_html=True)

    st.markdown("")

    # Row 2: Risk summary + Bar chart + Top 5
    _c1, _c2, _c3 = st.columns([1.2, 1.8, 1.8])

    with _c1:
        st.markdown('<div class="dash-box"><h4>🎯 สรุปความเสี่ยงเส้นทาง</h4>', unsafe_allow_html=True)
        _total = max(len(station_data), 1)
        _levels = [
            ("🚨 ฝนหนักมาก", _n_critical, "#ef4444"),
            ("⛈️ ฝนหนัก",   _n_heavy,    "#f59e0b"),
            ("🌧️ ฝนปานกลาง",_n_medium,   "#3b82f6"),
            ("☀️ ปกติ",      _n_ok,       "#10b981"),
        ]
        for lbl, cnt, col in _levels:
            _pct = cnt / _total * 100
            st.markdown(f"""
            <div style='margin:6px 0;'>
                <div style='display:flex;justify-content:space-between;margin-bottom:3px;'>
                    <span style='color:#a8cce0;font-size:0.8rem;'>{lbl}</span>
                    <span style='color:#fff;font-size:0.8rem;font-weight:700;'>{cnt}</span>
                </div>
                <div class='prog-wrap'><div class='prog-fill' style='width:{_pct:.1f}%;background:{col};'></div></div>
            </div>""", unsafe_allow_html=True)

        if _n_critical > 0:
            _ov_c, _ov_l = "#ef4444", "🚨 วิกฤต"
        elif _n_heavy > 0:
            _ov_c, _ov_l = "#f59e0b", "⚠️ ต้องระวัง"
        elif _n_medium > 0:
            _ov_c, _ov_l = "#3b82f6", "ℹ️ เฝ้าระวัง"
        elif _n_ok > 0:
            _ov_c, _ov_l = "#10b981", "✅ ปกติ"
        else:
            _ov_c, _ov_l = "#4a6070", "— ไม่มีข้อมูล"

        st.markdown(f"""
        <div style='margin-top:12px;background:rgba(0,0,0,0.3);border:1px solid {_ov_c};
            border-radius:8px;padding:10px 14px;text-align:center;'>
            <div style='color:#6899b8;font-size:0.7rem;font-weight:600;text-transform:uppercase;'>ภาพรวมความเสี่ยง</div>
            <div style='color:{_ov_c};font-size:1.3rem;font-weight:800;margin-top:3px;'>{_ov_l}</div>
        </div></div>""", unsafe_allow_html=True)

    with _c2:
        st.markdown('<div class="dash-box"><h4>🌧️ ปริมาณฝนแยกตามสาย (mm)</h4>', unsafe_allow_html=True)
        _line_stats = {}
        for _s in station_data:
            _ln = _s["line"]
            if _ln not in _line_stats:
                _line_stats[_ln] = {"vals":[], "color":_s["line_color"], "icon":_s["line_icon"]}
            if _s["rain"] is not None:
                _line_stats[_ln]["vals"].append(_s["rain"])

        _max_bar = max((max(v["vals"]) for v in _line_stats.values() if v["vals"]), default=10)
        _max_bar = max(_max_bar, 10)

        for _ln_n, _ld in _line_stats.items():
            _v = _ld["vals"]
            _mx  = round(max(_v), 1) if _v else None
            _avg = round(sum(_v)/len(_v), 1) if _v else None
            _bw  = (_mx / _max_bar * 100) if _mx else 0
            _bc  = risk_color_hex(_mx)
            st.markdown(f"""
            <div style='margin:5px 0;'>
                <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:3px;'>
                    <span style='color:#a8cce0;font-size:0.78rem;'>
                        <span style='color:{_ld["color"]};'>●</span> {_ln_n}
                    </span>
                    <span style='color:#fff;font-size:0.78rem;'>
                        สูงสุด <b>{_mx if _mx is not None else "—"}</b> mm
                        {" · เฉลี่ย " + str(_avg) if _avg is not None else ""}
                    </span>
                </div>
                <div class='prog-wrap'><div class='prog-fill' style='width:{_bw:.1f}%;background:{_bc};'></div></div>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with _c3:
        st.markdown('<div class="dash-box"><h4>🚨 สถานีเสี่ยงสูงสุด TOP 5</h4>', unsafe_allow_html=True)
        _top5 = sorted([s for s in station_data if s["rain"] is not None],
                        key=lambda x: x["rain"], reverse=True)[:5]
        if not _top5:
            st.markdown("<p style='color:#4a6070;font-size:0.82rem;margin:8px 0;'>"
                        "ไม่มีข้อมูลฝน — อาจยังไม่ได้รับข้อมูลจาก TMD</p>", unsafe_allow_html=True)
        else:
            for i, _s in enumerate(_top5, 1):
                _rc = risk_color_hex(_s["rain"])
                _lbl, _em, _, _ = risk_class(_s["rain"])
                st.markdown(f"""
                <div style='display:flex;align-items:center;gap:10px;padding:7px 0;
                    border-bottom:1px solid rgba(91,200,255,0.06);'>
                    <span style='color:#4a6070;font-size:0.85rem;font-weight:800;width:18px;'>{i}</span>
                    <div style='flex:1;min-width:0;'>
                        <div style='color:#d0e8f8;font-size:0.82rem;font-weight:600;
                            overflow:hidden;text-overflow:ellipsis;'>{_em} {_s["name"]}</div>
                        <div style='color:#4a7090;font-size:0.7rem;'>{_s["province"]} · {_s["line"]}</div>
                    </div>
                    <div style='text-align:right;min-width:55px;'>
                        <div style='color:{_rc};font-size:1.05rem;font-weight:800;'>{_s["rain"]:.1f}</div>
                        <div style='color:#4a7090;font-size:0.68rem;'>mm</div>
                    </div>
                </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("")

    # Summary table
    st.markdown('<div class="sec-title">📋 ตารางสรุปทุกสถานี (พยากรณ์' + sel_horizon + ')</div>',
                unsafe_allow_html=True)
    _rows = []
    for _s in sorted(station_data, key=lambda x: x["rain"] if x["rain"] is not None else -1, reverse=True):
        _lbl, _em, _, _ = risk_class(_s["rain"])
        _rows.append({
            "สาย": f"{_s['line_icon']} {_s['line_short']}",
            "สถานี": _s["name"],
            "จังหวัด": _s["province"],
            "ฝน (mm)": round(_s["rain"], 1) if _s["rain"] is not None else None,
            "ระดับ": f"{_em} {_lbl}",
            "Tmax (°C)": round(_s["tc_max"], 1) if _s["tc_max"] is not None else None,
            "Tmin (°C)": round(_s["tc_min"], 1) if _s["tc_min"] is not None else None,
            "RH (%)": round(_s["rh"], 0) if _s["rh"] is not None else None,
            "ลม (m/s)": round(_s["ws"], 1) if _s["ws"] is not None else None,
            "สภาพอากาศ": cond_text(_s["cond"]) if _s["cond"] is not None else "—",
        })

    if _rows:
        _df = pd.DataFrame(_rows)
        st.dataframe(_df, use_container_width=True, hide_index=True, height=380,
            column_config={
                "ฝน (mm)":   st.column_config.NumberColumn("🌧️ ฝน (mm)",  format="%.1f"),
                "Tmax (°C)": st.column_config.NumberColumn("🌡️ Tmax",     format="%.1f"),
                "Tmin (°C)": st.column_config.NumberColumn("❄️ Tmin",      format="%.1f"),
                "RH (%)":    st.column_config.NumberColumn("💧 RH%",       format="%.0f"),
                "ลม (m/s)":  st.column_config.NumberColumn("💨 ลม",        format="%.1f"),
            })


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
            folium.PolyLine(_coords, color=_ld["color"], weight=3.5, opacity=0.85,
                            tooltip=f"{_ln} — {_ld['desc']}").add_to(_m)

        # Markers
        for _s in station_data:
            _rc = risk_color_hex(_s["rain"])
            _lbl, _em, _, _ = risk_class(_s["rain"])
            _ic_col = {"#ef4444":"red","#f59e0b":"orange","#3b82f6":"blue",
                        "#10b981":"green","#4a6070":"gray"}.get(_rc, "blue")
            # Precompute display strings (avoid nested f-strings)
            _v_rain = "{:.1f} mm".format(_s["rain"]) if _s["rain"] is not None else "N/A"
            _v_tmax = "{:.1f}°C".format(_s["tc_max"]) if _s["tc_max"] is not None else "N/A"
            _v_tmin = "{:.1f}°C".format(_s["tc_min"]) if _s["tc_min"] is not None else "N/A"
            _v_rh   = "{:.0f}%".format(_s["rh"]) if _s["rh"] is not None else "N/A"
            _v_cond = cond_text(_s["cond"]) if _s["cond"] is not None else "N/A"
            _popup_html = (
                "<div style='font-family:Sarabun,sans-serif;min-width:180px;'>"
                f"<b style='font-size:0.95rem;color:#111;'>{_s['name']}</b><br>"
                f"<span style='color:#555;font-size:0.78rem;'>{_s['province']} · {_s['line']}</span>"
                "<hr style='margin:5px 0;border-color:#ddd;'>"
                "<table style='font-size:0.78rem;width:100%;'>"
                f"<tr><td>🌧️ ฝน</td><td><b>{_v_rain}</b></td></tr>"
                f"<tr><td>⚠️ ระดับ</td><td>{_em} {_lbl}</td></tr>"
                f"<tr><td>🌡️ Tmax</td><td>{_v_tmax}</td></tr>"
                f"<tr><td>❄️ Tmin</td><td>{_v_tmin}</td></tr>"
                f"<tr><td>💧 RH</td><td>{_v_rh}</td></tr>"
                f"<tr><td>☁️ สภาพ</td><td>{_v_cond}</td></tr>"
                "</table></div>"
            )
            _tt = "{} {} {}".format(
                _s["name"], _em,
                "{:.1f}mm".format(_s["rain"]) if _s["rain"] is not None else ""
            )
            folium.Marker(
                location=[_s["lat"], _s["lon"]],
                popup=folium.Popup(_popup_html, max_width=260),
                tooltip=_tt,
                icon=folium.Icon(color=_ic_col, icon="train", prefix="fa"),
            ).add_to(_m)

        st.caption("🖱️ คลิกไอคอนสถานีเพื่อดูข้อมูล · 🔴 ฝนหนักมาก · 🟠 ฝนหนัก · 🔵 ฝนปานกลาง · 🟢 ปกติ")
        st_folium(_m, width="100%", height=580, returned_objects=[])

    except ImportError:
        st.warning("⚠️ ติดตั้ง `folium` และ `streamlit-folium` เพื่อแสดงแผนที่")
        _mdf = pd.DataFrame([{
            "lat":_s["lat"],"lon":_s["lon"],"สถานี":_s["name"]
        } for _s in station_data])
        if not _mdf.empty:
            st.map(_mdf, latitude="lat", longitude="lon", use_container_width=True)


# ╔══════════════════════════════════════════════════════════╗
# ║  TAB 3 — ALERTS                                         ║
# ╚══════════════════════════════════════════════════════════╝
with tab_alert:
    _ac, _bc = st.columns([1.6, 1])

    with _ac:
        st.markdown('<div class="sec-title">🚨 สถานีที่ต้องเฝ้าระวัง</div>', unsafe_allow_html=True)
        _alerts = sorted([s for s in station_data if (s["rain"] or 0) >= _min_rain],
                          key=lambda x: x["rain"] or 0, reverse=True)
        if _alerts:
            for _s in _alerts:
                _lbl, _em, _, _alc = risk_class(_s["rain"])
                _cond_txt = cond_text(_s["cond"]) if _s["cond"] is not None else ""
                st.markdown(f"""
                <div class='alert-card {_alc}'>
                    <div style='display:flex;justify-content:space-between;align-items:flex-start;gap:14px;'>
                        <div style='flex:1;min-width:0;'>
                            <div class='alert-card-title'>{_em} {_s['name']}
                                <span style='color:{_s["line_color"]};font-size:0.74rem;
                                    font-weight:600;margin-left:8px;'>
                                    [{_s["line_short"]}] {_s["line"]}
                                </span>
                            </div>
                            <div class='alert-card-body'>
                                📍 {_s['province']} · กม. {_s.get('km',0)}
                                {f" · 🌧️ <b>{_s['rain']:.1f} mm</b>" if _s["rain"] is not None else ""}
                                {f" · 🌡️ {_s['tc_max']:.1f}/{_s['tc_min']:.1f}°C" if _s["tc_max"] is not None else ""}
                                {f" · 💧 {_s['rh']:.0f}%" if _s["rh"] is not None else ""}
                                {f" · 💨 {_s['ws']:.1f} m/s" if _s["ws"] is not None else ""}
                                {f"<br>☁️ {_cond_txt}" if _cond_txt else ""}
                            </div>
                        </div>
                        <div style='text-align:right;min-width:70px;'>
                            <div style='color:#fff;font-size:1.5rem;font-weight:800;line-height:1;'>
                                {f"{_s['rain']:.0f}" if _s["rain"] is not None else "—"}
                            </div>
                            <div style='color:#6899b8;font-size:0.7rem;'>mm</div>
                        </div>
                    </div>
                </div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='alert-card alert-ok'>
                <div class='alert-card-title'>✅ ไม่มีสถานีเกินเกณฑ์ ({sel_thresh})</div>
                <div class='alert-card-body'>
                    สภาพอากาศปกติทุกสถานีในเส้นทางที่เลือก
                    {" · หรือยังไม่ได้รับข้อมูลจาก TMD" if not _api_ok else ""}
                </div>
            </div>""", unsafe_allow_html=True)

    with _bc:
        st.markdown('<div class="sec-title">📋 เกณฑ์ฝน (TMD)</div>', unsafe_allow_html=True)
        for _em, _lv, _mm, _cls in [
            ("🌦️","ฝนเล็กน้อย","< 10 mm/วัน","alert-ok"),
            ("🌧️","ฝนปานกลาง","10–35 mm/วัน","alert-info"),
            ("⛈️","ฝนหนัก","35–90 mm/วัน","alert-warning"),
            ("🌊","ฝนหนักมาก","> 90 mm/วัน","alert-critical"),
        ]:
            st.markdown(f"""
            <div class='alert-card {_cls}' style='padding:8px 14px;'>
                <div class='alert-card-body'>{_em} <b>{_lv}</b> — {_mm}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sec-title">⚠️ คำแนะนำเมื่อฝนตกหนัก</div>', unsafe_allow_html=True)
        st.markdown("""
        <div class='alert-card alert-warning'>
            <div class='alert-card-body'>
            • ตรวจสอบทางและสะพานก่อนเดินรถ<br>
            • ระวังดินถล่ม โดยเฉพาะภาคเหนือและภาคใต้<br>
            • ลดความเร็วเมื่อมีน้ำท่วมราง<br>
            • ติดต่อศูนย์ควบคุมการเดินรถทันทีหากพบความผิดปกติ
            </div>
        </div>""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════╗
# ║  TAB 4 — PER LINE                                       ║
# ╚══════════════════════════════════════════════════════════╝
with tab_line:
    _lines_show = [sel_line] if sel_line != "ทุกสาย" else list(SRT_LINES.keys())
    for _ln in _lines_show:
        _ld = SRT_LINES[_ln]
        _ln_stns = [s for s in station_data if s["line"] == _ln]
        _ln_r = [s["rain"] for s in _ln_stns if s["rain"] is not None]
        _ln_max = max(_ln_r) if _ln_r else None
        _ln_avg = round(sum(_ln_r)/len(_ln_r), 1) if _ln_r else None
        _ln_heavy = sum(1 for r in _ln_r if r >= 35)

        _title = (f"{_ld['icon']} {_ln} — {_ld['desc']}  |  "
                  f"{'🚨 ' + str(_ln_heavy) + ' สถานีเสี่ยง' if _ln_heavy else '✅ ปกติ'}")
        with st.expander(_title, expanded=(sel_line != "ทุกสาย")):
            _mc = st.columns(4)
            with _mc[0]: st.metric("🌧️ ฝนสูงสุด", f"{_ln_max:.1f} mm" if _ln_max is not None else "—")
            with _mc[1]: st.metric("📊 ฝนเฉลี่ย", f"{_ln_avg} mm" if _ln_avg is not None else "—")
            with _mc[2]: st.metric("⛈️ สถานีเสี่ยง", f"{_ln_heavy}")
            with _mc[3]: st.metric("📍 สถานี", f"{len(_ln_stns)}")

            # Station rows
            _tbl_rows = []
            for _s in _ln_stns:
                _lbl, _em, _, _ = risk_class(_s["rain"])
                _tbl_rows.append({
                    "กม.": _s.get("km", 0),
                    "สถานี": f"🚉 {_s['name']}",
                    "จังหวัด": _s["province"],
                    "ฝน (mm)": round(_s["rain"], 1) if _s["rain"] is not None else None,
                    "ระดับ": f"{_em} {_lbl}",
                    "Tmax/Tmin": f"{_s['tc_max']:.0f}°/{_s['tc_min']:.0f}°"
                                  if _s["tc_max"] is not None and _s["tc_min"] is not None else "—",
                    "RH%": round(_s["rh"], 0) if _s["rh"] is not None else None,
                    "สภาพ": cond_text(_s["cond"]) if _s["cond"] is not None else "—",
                })
            if _tbl_rows:
                st.dataframe(pd.DataFrame(_tbl_rows), use_container_width=True, hide_index=True,
                    column_config={
                        "ฝน (mm)": st.column_config.NumberColumn("🌧️ ฝน", format="%.1f"),
                        "RH%": st.column_config.NumberColumn("💧 RH%", format="%.0f"),
                    })


# ╔══════════════════════════════════════════════════════════╗
# ║  TAB 5 — DETAILED FORECAST                              ║
# ╚══════════════════════════════════════════════════════════╝
with tab_forecast:
    st.markdown('<div class="sec-title">🌤️ พยากรณ์อากาศแบบละเอียดรายสถานี</div>',
                unsafe_allow_html=True)
    _sel_stn_name = st.selectbox(
        "เลือกสถานี",
        [s["name"] for s in station_data] if station_data else ["—"],
        key="forecast_station_select",
    )
    _sel_stn = next((s for s in station_data if s["name"] == _sel_stn_name), None)

    if _sel_stn and _api_ok:
        _h_col, _d_col = st.columns(2)

        # Daily 3-day
        with _d_col:
            st.markdown('<div class="dash-box"><h4>📅 พยากรณ์ 3 วันข้างหน้า</h4>', unsafe_allow_html=True)
            with st.spinner("กำลังโหลดพยากรณ์..."):
                _d_data = fetch_daily_at(_sel_stn["lat"], _sel_stn["lon"], _token(), days=3)
                _d_fc = parse_daily_forecast(_d_data)
            if _d_fc:
                _drows = []
                for f in _d_fc:
                    _drows.append({
                        "วันที่": f["time"][:10] if f["time"] else "",
                        "ฝน (mm)": round(f["rain"],1) if f["rain"] is not None else None,
                        "Tmax/Tmin": (f"{f['tc_max']:.0f}/{f['tc_min']:.0f}°C"
                                       if f["tc_max"] is not None and f["tc_min"] is not None else "—"),
                        "RH%": round(f["rh"],0) if f["rh"] is not None else None,
                        "สภาพอากาศ": cond_text(f["cond"]) if f["cond"] is not None else "—",
                    })
                st.dataframe(pd.DataFrame(_drows), use_container_width=True, hide_index=True)
            else:
                st.info("ไม่มีข้อมูลพยากรณ์รายวัน")
            st.markdown("</div>", unsafe_allow_html=True)

        # Hourly 24h
        with _h_col:
            st.markdown('<div class="dash-box"><h4>🕐 พยากรณ์ราย ชม. (24 ชม.)</h4>', unsafe_allow_html=True)
            with st.spinner("กำลังโหลดพยากรณ์ราย ชม..."):
                _h_data = fetch_hourly_at(_sel_stn["lat"], _sel_stn["lon"], _token(), hours=24)
                _h_fc = parse_hourly_forecast(_h_data)
            if _h_fc:
                _hrows = []
                for f in _h_fc:
                    _t = f["time"]
                    _hh = _t[11:16] if len(_t) >= 16 else _t
                    _hrows.append({
                        "เวลา": _hh,
                        "อุณหภูมิ (°C)": round(f["tc"],1) if f["tc"] is not None else None,
                        "ฝน (mm)":      round(f["rain"],1) if f["rain"] is not None else None,
                        "RH%":          round(f["rh"],0) if f["rh"] is not None else None,
                        "ลม (m/s)":     round(f["ws"],1) if f["ws"] is not None else None,
                    })
                st.dataframe(pd.DataFrame(_hrows), use_container_width=True, hide_index=True, height=380)
            else:
                st.info("ไม่มีข้อมูลพยากรณ์ราย ชม.")
            st.markdown("</div>", unsafe_allow_html=True)
    elif not _api_ok:
        st.info("ℹ️ ต้องเชื่อมต่อ TMD API ก่อนเพื่อดูพยากรณ์ละเอียด — ใส่ Token ใน Sidebar")


# ══════════════════════════════════════════════════════════════
#  FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(f"""
<div style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;
    color:#2a4060;font-size:0.74rem;padding:4px 0;gap:12px;'>
    <span>🚆 SRT Weather Alert v3.0 · มิถุนายน 2569</span>
    <span>
        อุตุฯ: <a href='https://data.tmd.go.th/nwpapi/doc/main/getting_start.html'
            style='color:#2a6090;' target='_blank'>TMD NWP API v1</a>
        · โครงข่าย: <a href='https://datagov.mot.go.th/en/organization/railway'
            style='color:#2a6090;' target='_blank'>การรถไฟแห่งประเทศไทย</a>
    </span>
    <span>อัพเดต {NOW_TH.strftime('%d %b %Y · %H:%M')} น.</span>
</div>""", unsafe_allow_html=True)
