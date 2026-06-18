"""
🚆 SRT Weather Command Center
ศูนย์เฝ้าระวังสภาพอากาศและปริมาณน้ำฝน · โครงข่ายรถไฟแห่งประเทศไทย
สำหรับผู้บริหารงานเดินรถ · ข้อมูลจากกรมอุตุนิยมวิทยา (TMD NWP API v1)
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
    page_title="SRT Weather Command Center",
    page_icon="🚆",
    layout="wide",
    initial_sidebar_state="expanded",
)

TZ_TH = pytz.timezone("Asia/Bangkok")
NOW_TH = datetime.now(TZ_TH)
TH_MONTHS = ["", "ม.ค.","ก.พ.","มี.ค.","เม.ย.","พ.ค.","มิ.ย.",
             "ก.ค.","ส.ค.","ก.ย.","ต.ค.","พ.ย.","ธ.ค."]
def th_datetime(dt):
    return f"{dt.day} {TH_MONTHS[dt.month]} {dt.year+543} · {dt.strftime('%H:%M')} น."

# ══════════════════════════════════════════════════════════════
#  THEME  — Executive control-room aesthetic
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700;800&family=Kanit:wght@500;600;700;800&display=swap');

*, html, body, [class*="css"] { font-family: 'Sarabun', sans-serif !important; }
h1,h2,h3,.kanit { font-family: 'Kanit', sans-serif !important; }

:root {
    --bg0:#070d15; --bg1:#0b1420; --bg2:#101d2e; --panel:#0e1a29;
    --line:#1c3247; --line2:#24405a;
    --ink:#e8f1f8; --ink2:#9fbcd0; --ink3:#5f8199;
    --accent:#38bdf8; --gold:#d4af37;
    --ok:#10b981; --info:#3b82f6; --warn:#f59e0b; --crit:#ef4444;
}

.stApp {
    background:
        radial-gradient(1200px 500px at 80% -10%, rgba(56,189,248,0.06), transparent),
        linear-gradient(180deg, #070d15 0%, #0b1622 55%, #070d15 100%);
}
.block-container { padding-top: 1.4rem !important; max-width: 1500px; }

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#060c14,#0a1622) !important;
    border-right: 1px solid var(--line) !important;
}
[data-testid="stSidebar"] * { color: var(--ink2) !important; }

/* Hide default header */
[data-testid="stHeader"] { background: transparent !important; }

/* ── Command header ── */
.cmd-header {
    background: linear-gradient(110deg, #0c1d30 0%, #103456 45%, #0c1d30 100%);
    border: 1px solid var(--line2);
    border-radius: 16px;
    padding: 22px 28px;
    position: relative; overflow: hidden;
    box-shadow: 0 8px 30px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04);
}
.cmd-header::before {
    content:''; position:absolute; inset:0; pointer-events:none;
    background: repeating-linear-gradient(90deg, transparent 0 38px, rgba(212,175,55,0.05) 38px 40px);
}
.cmd-title { font-size:1.75rem; font-weight:800; color:#fff; margin:0;
    letter-spacing:0.3px; display:flex; align-items:center; gap:12px; }
.cmd-sub { color:var(--ink2); font-size:0.86rem; margin-top:5px; }
.cmd-live {
    display:inline-flex; align-items:center; gap:6px;
    background:rgba(16,185,129,0.15); border:1px solid rgba(16,185,129,0.4);
    color:#34d399; font-size:0.74rem; font-weight:700; padding:3px 12px;
    border-radius:20px;
}
.pulse { width:8px; height:8px; border-radius:50%; background:#34d399;
    box-shadow:0 0 0 0 rgba(52,211,153,0.6); animation:pulse 2s infinite; }
@keyframes pulse {
    0%{box-shadow:0 0 0 0 rgba(52,211,153,0.6);}
    70%{box-shadow:0 0 0 8px rgba(52,211,153,0);}
    100%{box-shadow:0 0 0 0 rgba(52,211,153,0);}
}

/* ── Alert banner ── */
.alert-banner {
    border-radius:14px; padding:16px 22px; margin:14px 0;
    display:flex; align-items:center; gap:16px;
    border:1px solid; position:relative; overflow:hidden;
}
.ab-crit { background:linear-gradient(100deg,rgba(239,68,68,0.22),rgba(120,20,20,0.28)); border-color:rgba(239,68,68,0.5); }
.ab-warn { background:linear-gradient(100deg,rgba(245,158,11,0.18),rgba(120,80,10,0.22)); border-color:rgba(245,158,11,0.45); }
.ab-ok   { background:linear-gradient(100deg,rgba(16,185,129,0.15),rgba(10,80,60,0.2)); border-color:rgba(16,185,129,0.4); }
.ab-icon { font-size:2.4rem; line-height:1; }
.ab-text h3 { margin:0; font-size:1.2rem; color:#fff; }
.ab-text p  { margin:2px 0 0; font-size:0.88rem; color:var(--ink2); }

/* ── KPI tiles ── */
.kpi {
    background: linear-gradient(160deg, var(--panel), #0a1521);
    border:1px solid var(--line);
    border-radius:14px; padding:18px 20px; height:100%;
    position:relative; overflow:hidden;
    transition: transform .12s, box-shadow .12s, border-color .12s;
}
.kpi:hover { transform:translateY(-2px); box-shadow:0 10px 28px rgba(0,0,0,0.35); border-color:var(--line2); }
.kpi::after { content:''; position:absolute; top:0; left:0; width:100%; height:3px; background:var(--c,#38bdf8); }
.kpi-top { display:flex; align-items:center; justify-content:space-between; }
.kpi-ico { font-size:1.5rem; }
.kpi-tag { font-size:0.66rem; font-weight:700; padding:2px 8px; border-radius:10px;
    background:rgba(255,255,255,0.06); color:var(--ink3); text-transform:uppercase; letter-spacing:0.5px; }
.kpi-val { font-family:'Kanit',sans-serif; font-size:2.1rem; font-weight:700; color:#fff; line-height:1; margin:10px 0 2px; }
.kpi-val small { font-size:0.85rem; color:var(--ink2); font-weight:500; margin-left:3px; }
.kpi-lab { color:var(--ink2); font-size:0.82rem; }
.kpi-foot { color:var(--ink3); font-size:0.74rem; margin-top:6px; }
.c-crit{--c:#ef4444;} .c-warn{--c:#f59e0b;} .c-info{--c:#3b82f6;}
.c-ok{--c:#10b981;} .c-gold{--c:#d4af37;} .c-cyan{--c:#38bdf8;}

/* ── Panel ── */
.panel {
    background: linear-gradient(160deg, var(--panel), #0a1521);
    border:1px solid var(--line); border-radius:14px; padding:18px 20px; height:100%;
}
.panel-h { font-family:'Kanit',sans-serif; color:var(--accent); font-size:0.92rem;
    font-weight:600; margin:0 0 14px; display:flex; align-items:center; gap:8px;
    border-bottom:1px solid var(--line); padding-bottom:10px; }

/* ── Rain bar (executive) ── */
.rain-row { display:grid; grid-template-columns:130px 1fr 64px; align-items:center;
    gap:12px; padding:7px 0; }
.rain-name { color:var(--ink); font-size:0.84rem; font-weight:500; white-space:nowrap;
    overflow:hidden; text-overflow:ellipsis; }
.rain-track { background:rgba(255,255,255,0.05); border-radius:8px; height:22px; position:relative; overflow:hidden; }
.rain-fill { height:100%; border-radius:8px; display:flex; align-items:center; justify-content:flex-end;
    padding-right:8px; transition:width .5s cubic-bezier(.4,0,.2,1); min-width:2px; }
.rain-val { text-align:right; font-family:'Kanit',sans-serif; font-weight:600; font-size:0.9rem; }

/* ── Risk list item ── */
.risk-item { display:flex; align-items:center; gap:12px; padding:10px 0;
    border-bottom:1px solid rgba(28,50,71,0.5); }
.risk-rank { font-family:'Kanit',sans-serif; font-weight:700; font-size:1.1rem; color:var(--ink3); width:24px; text-align:center; }
.risk-body { flex:1; min-width:0; }
.risk-stn { color:var(--ink); font-weight:600; font-size:0.88rem; }
.risk-meta { color:var(--ink3); font-size:0.74rem; }
.risk-num { font-family:'Kanit',sans-serif; font-weight:700; font-size:1.15rem; text-align:right; }

/* ── badges ── */
.bdg { padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:700; white-space:nowrap; }
.bdg-crit{ background:#7f1d1d; color:#fecaca; } .bdg-warn{ background:#78350f; color:#fde68a; }
.bdg-info{ background:#1e3a5f; color:#bfdbfe; } .bdg-ok{ background:#064e3b; color:#a7f3d0; }
.bdg-na{ background:#1f2937; color:#9ca3af; }

/* ── Metric chips ── */
.chips { display:flex; gap:16px; flex-wrap:wrap; }
.chip { display:flex; align-items:center; gap:7px; color:var(--ink2); font-size:0.82rem; }
.chip b { color:var(--ink); }

/* ── Streamlit overrides ── */
.stTabs [data-baseweb="tab-list"] { background:var(--bg1); border:1px solid var(--line);
    border-radius:12px; gap:3px; padding:5px; }
.stTabs [data-baseweb="tab"] { color:var(--ink3); border-radius:8px; padding:8px 20px; font-weight:600; }
.stTabs [aria-selected="true"] { background:linear-gradient(135deg,#103456,#0c2640); color:#fff !important; }

div[data-testid="stMetric"]{ background:var(--panel); border:1px solid var(--line);
    border-radius:12px; padding:14px 16px; }
div[data-testid="stMetric"] label{ color:var(--ink3) !important; font-size:0.76rem !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"]{ color:#fff !important; font-family:'Kanit'; }

div[data-baseweb="select"] > div{ background:var(--bg2) !important; border-color:var(--line2) !important; }
div[data-baseweb="select"] *{ color:var(--ink) !important; }

.stButton > button{ background:linear-gradient(135deg,#103456,#0c2640) !important;
    color:var(--ink) !important; border:1px solid var(--line2) !important;
    border-radius:10px !important; font-weight:600 !important; }
.stButton > button:hover{ border-color:var(--accent) !important;
    box-shadow:0 0 16px rgba(56,189,248,0.2) !important; }

div[data-testid="stExpander"]{ background:var(--panel) !important; border:1px solid var(--line) !important; border-radius:12px !important; }
.stDataFrame{ border-radius:10px !important; overflow:hidden !important; }

::-webkit-scrollbar{ width:6px; height:6px; }
::-webkit-scrollbar-track{ background:var(--bg0); }
::-webkit-scrollbar-thumb{ background:var(--line2); border-radius:3px; }

.sec-label { font-family:'Kanit',sans-serif; color:var(--ink); font-size:1.05rem;
    font-weight:600; margin:6px 0 12px; display:flex; align-items:center; gap:10px; }
.sec-label::before { content:''; width:4px; height:18px; background:var(--accent); border-radius:2px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  TOKEN
# ══════════════════════════════════════════════════════════════
def _decode_jwt(token):
    try:
        p = token.split(".")[1]; p += "=" * (-len(p) % 4)
        return json.loads(base64.urlsafe_b64decode(p))
    except Exception:
        return {}

def _set_token(raw):
    raw = (raw or "").strip()
    st.session_state["_tk"] = raw
    st.session_state["_tk_jwt"] = _decode_jwt(raw)
    st.session_state["_tk_uid"] = str(st.session_state["_tk_jwt"].get("sub",""))

if "_tk" not in st.session_state:
    _boot = ""
    try:
        _boot = str(st.secrets.get("TMD_TOKEN","") or st.secrets.get("tmd_token",""))
    except Exception:
        pass
    if not _boot:
        import os; _boot = os.environ.get("TMD_TOKEN","")
    _set_token(_boot)

def _token(): return st.session_state.get("_tk","")
def _uid():   return st.session_state.get("_tk_uid","")
def _jwt():   return st.session_state.get("_tk_jwt",{})

# ══════════════════════════════════════════════════════════════
#  SRT RAILWAY NETWORK
# ══════════════════════════════════════════════════════════════
SRT_LINES = {
    "สายเหนือ": {"color":"#ef4444","short":"N","icon":"🔴","desc":"กรุงเทพ → เชียงใหม่ · 751 กม.",
        "stations":[
            {"name":"กรุงเทพ (หัวลำโพง)","lat":13.7401,"lon":100.5178,"province":"กรุงเทพมหานคร","km":0},
            {"name":"ดอนเมือง","lat":13.9186,"lon":100.5970,"province":"กรุงเทพมหานคร","km":22},
            {"name":"อยุธยา","lat":14.3554,"lon":100.5679,"province":"พระนครศรีอยุธยา","km":71},
            {"name":"ลพบุรี","lat":14.7987,"lon":100.6141,"province":"ลพบุรี","km":133},
            {"name":"นครสวรรค์","lat":15.7028,"lon":100.1363,"province":"นครสวรรค์","km":246},
            {"name":"พิษณุโลก","lat":16.8204,"lon":100.2714,"province":"พิษณุโลก","km":389},
            {"name":"อุตรดิตถ์","lat":17.6236,"lon":100.0987,"province":"อุตรดิตถ์","km":485},
            {"name":"เด่นชัย","lat":17.9827,"lon":100.0569,"province":"แพร่","km":535},
            {"name":"ลำปาง","lat":18.2896,"lon":99.4905,"province":"ลำปาง","km":642},
            {"name":"เชียงใหม่","lat":18.7883,"lon":98.9933,"province":"เชียงใหม่","km":751},
        ]},
    "สายตะวันออกเฉียงเหนือ": {"color":"#f59e0b","short":"NE","icon":"🟡","desc":"กรุงเทพ → หนองคาย · 624 กม.",
        "stations":[
            {"name":"กรุงเทพ (หัวลำโพง)","lat":13.7401,"lon":100.5178,"province":"กรุงเทพมหานคร","km":0},
            {"name":"สระบุรี","lat":14.5291,"lon":100.9101,"province":"สระบุรี","km":107},
            {"name":"ปากช่อง","lat":14.7043,"lon":101.4180,"province":"นครราชสีมา","km":180},
            {"name":"นครราชสีมา","lat":14.9734,"lon":102.1112,"province":"นครราชสีมา","km":264},
            {"name":"ขอนแก่น","lat":16.4419,"lon":102.8330,"province":"ขอนแก่น","km":449},
            {"name":"อุดรธานี","lat":17.4043,"lon":102.7877,"province":"อุดรธานี","km":569},
            {"name":"หนองคาย","lat":17.8818,"lon":102.7433,"province":"หนองคาย","km":624},
        ]},
    "สายอีสานใต้": {"color":"#a78bfa","short":"IS","icon":"🟣","desc":"นครราชสีมา → อุบลราชธานี · 305 กม.",
        "stations":[
            {"name":"นครราชสีมา (ถนนจิระ)","lat":14.9734,"lon":102.1112,"province":"นครราชสีมา","km":0},
            {"name":"บุรีรัมย์","lat":14.9950,"lon":103.1030,"province":"บุรีรัมย์","km":101},
            {"name":"สุรินทร์","lat":14.8835,"lon":103.4935,"province":"สุรินทร์","km":142},
            {"name":"ศรีสะเกษ","lat":15.1174,"lon":104.3221,"province":"ศรีสะเกษ","km":237},
            {"name":"อุบลราชธานี","lat":15.2241,"lon":104.8579,"province":"อุบลราชธานี","km":305},
        ]},
    "สายใต้": {"color":"#34d399","short":"S","icon":"🟢","desc":"กรุงเทพ → สุไหงโก-ลก · 1,144 กม.",
        "stations":[
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
            {"name":"สุไหงโก-ลก","lat":6.0277,"lon":101.9784,"province":"นราธิวาส","km":1144},
        ]},
    "สายตะวันออก": {"color":"#60a5fa","short":"E","icon":"🔵","desc":"กรุงเทพ → อรัญประเทศ · 255 กม.",
        "stations":[
            {"name":"กรุงเทพ (มักกะสัน)","lat":13.7524,"lon":100.5684,"province":"กรุงเทพมหานคร","km":0},
            {"name":"ฉะเชิงเทรา","lat":13.6903,"lon":101.0768,"province":"ฉะเชิงเทรา","km":61},
            {"name":"ชลบุรี","lat":13.3639,"lon":100.9905,"province":"ชลบุรี","km":120},
            {"name":"พัทยา","lat":12.9236,"lon":100.8825,"province":"ชลบุรี","km":154},
            {"name":"อรัญประเทศ","lat":13.6942,"lon":102.5062,"province":"สระแก้ว","km":255},
        ]},
}

# ══════════════════════════════════════════════════════════════
#  TMD NWP API v1
# ══════════════════════════════════════════════════════════════
TMD_NWP_BASE = "https://data.tmd.go.th/nwpapi/v1"

def _nwp_get(path, params, token):
    if not token:
        return None, "ไม่มี Token"
    url = f"{TMD_NWP_BASE}/{path.lstrip('/')}"
    headers = {"accept":"application/json", "authorization":f"Bearer {token}"}
    for attempt in range(2):
        try:
            r = requests.get(url, headers=headers, params=params, timeout=15, allow_redirects=True)
            if r.status_code == 200:
                try: return r.json(), ""
                except Exception: return None, f"200 non-JSON: {r.text[:60]}"
            if r.status_code in (401,403): return None, f"HTTP {r.status_code}: Token ไม่ถูกต้อง/หมดอายุ"
            if r.status_code == 404: return None, f"HTTP 404: {path}"
            if r.status_code == 429: return None, "HTTP 429: rate limit"
            if r.status_code >= 500:
                if attempt < 1: time.sleep(1.0); continue
                return None, f"HTTP {r.status_code}: server error"
            return None, f"HTTP {r.status_code}"
        except requests.exceptions.Timeout:
            if attempt < 1: continue
            return None, "Timeout 15s"
        except requests.exceptions.ConnectionError as e:
            return None, f"ConnError: {str(e)[:60]}"
        except Exception as e:
            return None, f"{type(e).__name__}: {str(e)[:60]}"
    return None, "Unknown"

DAILY_FIELDS = "tc_max,tc_min,rh,rain,cond,ws10m,wd10m"
HOURLY_FIELDS = "tc,rh,rain,cond,ws10m"

@st.cache_data(ttl=900, show_spinner=False)
def fetch_daily_at(lat, lon, token, days=7):
    p = {"lat":round(float(lat),4),"lon":round(float(lon),4),"fields":DAILY_FIELDS,
         "date":NOW_TH.strftime("%Y-%m-%d"),"hour":6,"duration":days}
    return _nwp_get("forecast/location/daily/at", p, token)[0]

@st.cache_data(ttl=900, show_spinner=False)
def fetch_daily_place(province, token, days=7):
    p = {"province":province,"fields":DAILY_FIELDS,
         "date":NOW_TH.strftime("%Y-%m-%d"),"hour":6,"duration":days}
    return _nwp_get("forecast/location/daily/place", p, token)[0]

@st.cache_data(ttl=900, show_spinner=False)
def fetch_hourly_at(lat, lon, token, hours=24):
    p = {"lat":round(float(lat),4),"lon":round(float(lon),4),"fields":HOURLY_FIELDS,
         "date":NOW_TH.strftime("%Y-%m-%d"),"hour":0,"duration":hours}
    return _nwp_get("forecast/location/hourly/at", p, token)[0]

@st.cache_data(ttl=900, show_spinner=False)
def fetch_hourly_place(province, token, hours=24):
    p = {"province":province,"fields":HOURLY_FIELDS,
         "date":NOW_TH.strftime("%Y-%m-%d"),"hour":0,"duration":hours}
    return _nwp_get("forecast/location/hourly/place", p, token)[0]

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_token_test(token):
    if not token: return False, "ไม่มี Token"
    p = {"lat":13.7563,"lon":100.5018,"fields":"tc","date":NOW_TH.strftime("%Y-%m-%d"),"hour":6,"duration":1}
    d, err = _nwp_get("forecast/location/daily/at", p, token)
    if d and isinstance(d, dict) and d.get("WeatherForecasts"):
        return True, "OK"
    return False, err

# ── parse helpers ──
def _scalar(v):
    if v is None: return None
    if isinstance(v, dict):
        for k in ("value","val","data","amount"):
            if k in v: return _scalar(v[k])
        return None
    if isinstance(v, list): return _scalar(v[0]) if v else None
    return v

def _to_float(v):
    v = _scalar(v)
    if v is None or v == "" or v == "-": return None
    try:
        f = float(v); return None if math.isnan(f) else f
    except (TypeError, ValueError): return None

def _pick(d, *keys):
    for k in keys:
        if k in d and d[k] is not None: return d[k]
    return None

def parse_daily(data):
    if not data or not isinstance(data, dict): return []
    wf = data.get("WeatherForecasts") or data.get("forecasts") or []
    if not wf or not isinstance(wf, list): return []
    fcs = wf[0].get("forecasts", []) if isinstance(wf[0], dict) else []
    out = []
    for f in fcs:
        if not isinstance(f, dict): continue
        d = f.get("data", {}) or {}
        out.append({
            "time": f.get("time","") or f.get("Time",""),
            "tc_max": _to_float(_pick(d,"tc_max","tcMax","tmax","tc")),
            "tc_min": _to_float(_pick(d,"tc_min","tcMin","tmin")),
            "rh":   _to_float(_pick(d,"rh","humidity")),
            "rain": _to_float(_pick(d,"rain","rainfall","precip")),
            "cond": _scalar(_pick(d,"cond","condition")),
            "ws":   _to_float(_pick(d,"ws10m","ws","windspeed")),
            "wd":   _to_float(_pick(d,"wd10m","wd","winddir")),
        })
    return out

def parse_hourly(data):
    if not data or not isinstance(data, dict): return []
    wf = data.get("WeatherForecasts") or []
    if not wf or not isinstance(wf, list): return []
    fcs = wf[0].get("forecasts", []) if isinstance(wf[0], dict) else []
    out = []
    for f in fcs:
        if not isinstance(f, dict): continue
        d = f.get("data", {}) or {}
        out.append({
            "time": f.get("time","") or f.get("Time",""),
            "tc":   _to_float(_pick(d,"tc","temp")),
            "rh":   _to_float(_pick(d,"rh","humidity")),
            "rain": _to_float(_pick(d,"rain","rainfall","precip")),
            "cond": _scalar(_pick(d,"cond","condition")),
            "ws":   _to_float(_pick(d,"ws10m","ws","windspeed")),
        })
    return out

# ── TMD condition codes ──
COND_MAP = {1:("ท้องฟ้าแจ่มใส","☀️"),2:("มีเมฆบางส่วน","🌤️"),3:("เมฆเป็นส่วนมาก","⛅"),
    4:("มีเมฆมาก","☁️"),5:("ฝนตกเล็กน้อย","🌦️"),6:("ฝนปานกลาง","🌧️"),
    7:("ฝนตกหนัก","⛈️"),8:("ฝนฟ้าคะนอง","⛈️"),9:("อากาศหนาวจัด","❄️"),
    10:("อากาศหนาว","🥶"),11:("อากาศเย็น","😎"),12:("อากาศร้อนจัด","🥵")}
def cond_text(c):
    try: t = COND_MAP.get(int(c)); return f"{t[1]} {t[0]}" if t else f"รหัส {c}"
    except Exception: return "—"
def cond_emoji(c):
    try: t = COND_MAP.get(int(c)); return t[1] if t else "•"
    except Exception: return "•"

# ── rainfall risk model (TMD criteria) ──
def rain_risk(mm):
    """return (level_int, label, emoji, hex, badge_class)"""
    if mm is None:        return (-1,"ไม่มีข้อมูล","⚪","#5f8199","bdg-na")
    if mm <= 0:           return (0,"ไม่มีฝน","☀️","#10b981","bdg-ok")
    if mm < 10:           return (1,"ฝนเล็กน้อย","🌦️","#22c55e","bdg-ok")
    if mm < 35:           return (2,"ฝนปานกลาง","🌧️","#3b82f6","bdg-info")
    if mm < 90:           return (3,"ฝนหนัก","⛈️","#f59e0b","bdg-warn")
    return (4,"ฝนหนักมาก","🌊","#ef4444","bdg-crit")

def rain_hex(mm):
    return rain_risk(mm)[3]

# ══════════════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:10px 0 16px;'>
        <div style='font-size:2.6rem;'>🚆</div>
        <div style='font-family:Kanit;color:#fff;font-size:1.1rem;font-weight:700;'>Weather Command</div>
        <div style='color:#5f8199;font-size:0.72rem;letter-spacing:0.5px;'>SRT EXECUTIVE CENTER</div>
    </div>""", unsafe_allow_html=True)

    # Token
    if _token():
        jd = _jwt(); exp = jd.get("exp",0)
        exp_dt = datetime.fromtimestamp(exp, tz=TZ_TH) if exp else None
        days = (exp_dt - NOW_TH).days if exp_dt else 0
        col = "#10b981" if days>30 else "#f59e0b" if days>0 else "#ef4444"
        st.markdown(f"""
        <div style='background:rgba(10,20,35,0.8);border:1px solid #1c3247;border-radius:10px;padding:10px 14px;margin-bottom:14px;'>
            <div style='color:#5f8199;font-size:0.7rem;'>🔑 TMD NWP API</div>
            <div style='color:#38bdf8;font-size:0.8rem;font-weight:600;'>uid <b style='color:#fff;'>{_uid()}</b></div>
            <div style='color:{col};font-size:0.72rem;margin-top:2px;'>{"●ใช้งานได้ ·เหลือ "+str(days)+"วัน" if days>0 else "●หมดอายุ"}</div>
        </div>""", unsafe_allow_html=True)
        if st.button("เปลี่ยน Token", use_container_width=True):
            _set_token(""); st.cache_data.clear(); st.rerun()
    else:
        st.markdown("<div style='color:#ef4444;font-size:0.8rem;'>⚠️ ใส่ Token เพื่อเริ่มใช้งาน</div>", unsafe_allow_html=True)
        ti = st.text_input("Token", type="password", placeholder="eyJ0eXA...", label_visibility="collapsed")
        if st.button("✅ เชื่อมต่อ", use_container_width=True):
            if ti.strip(): _set_token(ti.strip()); st.cache_data.clear(); st.rerun()

    st.markdown("<hr style='border-color:#1c3247;margin:14px 0;'>", unsafe_allow_html=True)

    st.markdown("<div style='color:#38bdf8;font-size:0.74rem;font-weight:700;letter-spacing:0.6px;margin-bottom:5px;'>🛤️ เส้นทาง</div>", unsafe_allow_html=True)
    sel_line = st.selectbox("line", ["ทุกสาย"]+list(SRT_LINES.keys()), label_visibility="collapsed")

    st.markdown("<div style='color:#38bdf8;font-size:0.74rem;font-weight:700;letter-spacing:0.6px;margin:12px 0 5px;'>📅 วันพยากรณ์</div>", unsafe_allow_html=True)
    HORIZONS = ["วันนี้","พรุ่งนี้","มะรืน","+3 วัน","+4 วัน","+5 วัน","+6 วัน"]
    sel_day = st.selectbox("day", HORIZONS, label_visibility="collapsed")
    day_idx = HORIZONS.index(sel_day)

    st.markdown("<div style='color:#38bdf8;font-size:0.74rem;font-weight:700;letter-spacing:0.6px;margin:12px 0 5px;'>🔴 Real-time</div>", unsafe_allow_html=True)
    auto = st.toggle("เชื่อมข้อมูลอัตโนมัติ", value=False)
    refresh_sec = 0
    if auto:
        rl = st.selectbox("rate", ["1 นาที","5 นาที","10 นาที"], index=1, label_visibility="collapsed")
        refresh_sec = {"1 นาที":60,"5 นาที":300,"10 นาที":600}[rl]

    if st.button("🔄 รีเฟรชเดี๋ยวนี้", use_container_width=True):
        st.cache_data.clear(); st.rerun()

    st.markdown(f"""
    <div style='color:#5f8199;font-size:0.74rem;margin-top:12px;line-height:1.7;'>
        🕐 ดึงข้อมูลล่าสุด<br>
        <span style='color:#38bdf8;font-weight:700;font-size:0.84rem;'>{th_datetime(NOW_TH)}</span>
        {"<br><span style='color:#10b981;'>🔴 auto-refresh เปิด</span>" if auto else ""}
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#1c3247;margin:14px 0;'>", unsafe_allow_html=True)
    for ln, ld in SRT_LINES.items():
        st.markdown(f"<div style='display:flex;align-items:center;gap:8px;margin:3px 0;'><div style='width:24px;height:3px;background:{ld['color']};border-radius:2px;'></div><span style='color:#5f8199;font-size:0.72rem;'>{ld['short']} · {ln}</span></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  LOAD DATA
# ══════════════════════════════════════════════════════════════
api_ok, api_err = (False, "ไม่มี Token")
if _token():
    api_ok, api_err = fetch_token_test(_token())

# Build station list
stations = []
seen = set()
for ln, ld in SRT_LINES.items():
    if sel_line != "ทุกสาย" and ln != sel_line: continue
    for s in ld["stations"]:
        if s["name"] in seen: continue
        seen.add(s["name"])
        stations.append({**s, "line":ln, "line_color":ld["color"],
                         "line_short":ld["short"], "line_icon":ld["icon"]})

@st.cache_data(ttl=600, show_spinner=False)
def load_all(stns_tuple, token, day_idx, bucket):
    rows = []; n_ok = 0
    for sj in stns_tuple:
        s = json.loads(sj)
        chosen = {}; series = []
        if token:
            d = fetch_daily_at(s["lat"], s["lon"], token, days=7)
            fc = parse_daily(d)
            if not fc and s.get("province"):
                d = fetch_daily_place(s["province"], token, days=7)
                fc = parse_daily(d)
            if fc:
                series = fc
                chosen = fc[day_idx] if day_idx < len(fc) else fc[-1]
                n_ok += 1
        rows.append({**s,
            "rain":chosen.get("rain"), "tc_max":chosen.get("tc_max"),
            "tc_min":chosen.get("tc_min"), "rh":chosen.get("rh"),
            "cond":chosen.get("cond"), "ws":chosen.get("ws"), "wd":chosen.get("wd"),
            "time":chosen.get("time",""), "series":series})
    return rows, n_ok

bucket = int(time.time()//600)
n_fetched = 0
with st.spinner(f"⏳ เชื่อมข้อมูลพยากรณ์ {len(stations)} สถานีแบบ real-time..."):
    if api_ok:
        sd_tuple = tuple(json.dumps(s, ensure_ascii=False) for s in stations)
        station_data, n_fetched = load_all(sd_tuple, _token(), day_idx, bucket)
    else:
        station_data = [{**s,"rain":None,"tc_max":None,"tc_min":None,"rh":None,
                         "cond":None,"ws":None,"wd":None,"time":"","series":[]} for s in stations]

# Aggregates
rains = [s["rain"] for s in station_data if s["rain"] is not None]
temps = [s["tc_max"] for s in station_data if s["tc_max"] is not None]
n_crit  = sum(1 for r in rains if r>=90)
n_heavy = sum(1 for r in rains if 35<=r<90)
n_med   = sum(1 for r in rains if 10<=r<35)
n_ok    = sum(1 for r in rains if r<10)
max_rain = max(rains) if rains else None
avg_rain = sum(rains)/len(rains) if rains else None
total_rain = sum(rains) if rains else 0
avg_temp = sum(temps)/len(temps) if temps else None

# ══════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════
_live = ('<span class="cmd-live"><span class="pulse"></span>LIVE · REAL-TIME</span>'
         if api_ok else '<span class="cmd-live" style="background:rgba(239,68,68,0.15);border-color:rgba(239,68,68,0.4);color:#f87171;">● OFFLINE</span>')
st.markdown(f"""
<div class='cmd-header'>
    <div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;'>
        <div>
            <h1 class='cmd-title'>🚆 SRT Weather Command Center</h1>
            <div class='cmd-sub'>ศูนย์เฝ้าระวังปริมาณน้ำฝนและสภาพอากาศ · โครงข่ายรถไฟแห่งประเทศไทย · สำหรับผู้บริหารงานเดินรถ</div>
        </div>
        <div style='text-align:right;'>
            {_live}
            <div style='color:#9fbcd0;font-size:0.78rem;margin-top:6px;'>📅 {th_datetime(NOW_TH)}</div>
            <div style='color:#5f8199;font-size:0.74rem;'>พยากรณ์: <b style='color:#38bdf8;'>{sel_day}</b> · {sel_line}</div>
        </div>
    </div>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  EXECUTIVE ALERT BANNER
# ══════════════════════════════════════════════════════════════
if not api_ok:
    st.markdown(f"""
    <div class='alert-banner ab-warn'>
        <div class='ab-icon'>🔌</div>
        <div class='ab-text'><h3>ยังไม่ได้เชื่อมต่อ TMD API</h3>
        <p>{api_err} — กรุณาใส่ Token ในแถบด้านซ้ายเพื่อเริ่มแสดงข้อมูลพยากรณ์</p></div>
    </div>""", unsafe_allow_html=True)
else:
    if n_crit > 0:
        crit_names = ", ".join(s["name"] for s in station_data if (s["rain"] or 0)>=90)
        st.markdown(f"""
        <div class='alert-banner ab-crit'>
            <div class='ab-icon'>🚨</div>
            <div class='ab-text'><h3>เตือนภัยระดับวิกฤต — ฝนหนักมาก {n_crit} สถานี</h3>
            <p>สถานีเสี่ยง: {crit_names} · แนะนำตรวจสอบทาง/สะพาน และพิจารณาชะลอการเดินรถ</p></div>
        </div>""", unsafe_allow_html=True)
    elif n_heavy > 0:
        st.markdown(f"""
        <div class='alert-banner ab-warn'>
            <div class='ab-icon'>⚠️</div>
            <div class='ab-text'><h3>เฝ้าระวัง — ฝนหนัก {n_heavy} สถานี</h3>
            <p>มีฝนตกหนัก 35–90 มม. ในบางช่วงทาง · ติดตามสถานการณ์ใกล้ชิดและเตรียมความพร้อม</p></div>
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class='alert-banner ab-ok'>
            <div class='ab-icon'>✅</div>
            <div class='ab-text'><h3>สถานการณ์ปกติ — ไม่มีฝนตกหนักในเส้นทาง</h3>
            <p>สภาพอากาศเอื้ออำนวยต่อการเดินรถทุกสาย · เชื่อมข้อมูล {n_fetched}/{len(station_data)} สถานี</p></div>
        </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  KPI ROW
# ══════════════════════════════════════════════════════════════
def kpi(col, ico, tag, val, unit, lab, foot, cls):
    col.markdown(f"""
    <div class='kpi {cls}'>
        <div class='kpi-top'><span class='kpi-ico'>{ico}</span><span class='kpi-tag'>{tag}</span></div>
        <div class='kpi-val'>{val}<small>{unit}</small></div>
        <div class='kpi-lab'>{lab}</div>
        <div class='kpi-foot'>{foot}</div>
    </div>""", unsafe_allow_html=True)

k = st.columns(6)
kpi(k[0],"🌧️","สูงสุด", f"{max_rain:.0f}" if max_rain is not None else "—","มม.",
    "ปริมาณฝนสูงสุด", "ในเส้นทางที่เลือก", "c-cyan")
kpi(k[1],"📊","เฉลี่ย", f"{avg_rain:.1f}" if avg_rain is not None else "—","มม.",
    "ฝนเฉลี่ยทุกสถานี", f"รวม {total_rain:.0f} มม." , "c-info")
kpi(k[2],"🚨","วิกฤต", str(n_crit),"สถานี",
    "ฝนหนักมาก (>90)", "ต้องระวังสูงสุด", "c-crit")
kpi(k[3],"⚠️","เสี่ยง", str(n_heavy),"สถานี",
    "ฝนหนัก (35–90)", "เฝ้าระวัง", "c-warn")
kpi(k[4],"🌡️","อุณหภูมิ", f"{avg_temp:.0f}" if avg_temp is not None else "—","°C",
    "อุณหภูมิเฉลี่ยสูงสุด", "ทั้งเครือข่าย", "c-gold")
kpi(k[5],"📍","ครอบคลุม", f"{n_fetched}","สถานี",
    f"จาก {len(station_data)} สถานี", "เชื่อมข้อมูลสำเร็จ", "c-ok")

st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  TABS
# ══════════════════════════════════════════════════════════════
tab_dash, tab_rain, tab_map, tab_lines, tab_detail = st.tabs([
    "📊 ภาพรวมผู้บริหาร", "🌧️ ปริมาณน้ำฝน", "🗺️ แผนที่", "🛤️ รายสาย", "🔍 เจาะลึกสถานี"])

# ╔═══════════════════════════════════════════════════════════╗
# ║  TAB: EXECUTIVE OVERVIEW                                  ║
# ╚═══════════════════════════════════════════════════════════╝
with tab_dash:
    c1, c2 = st.columns([1.15, 1])

    # — Risk distribution donut-like + line summary —
    with c1:
        st.markdown("<div class='panel'><div class='panel-h'>🎯 สรุปความเสี่ยงภาพรวม</div>", unsafe_allow_html=True)
        total = max(len(station_data), 1)
        levels = [("🌊 ฝนหนักมาก", n_crit, "#ef4444"),
                  ("⛈️ ฝนหนัก", n_heavy, "#f59e0b"),
                  ("🌧️ ฝนปานกลาง", n_med, "#3b82f6"),
                  ("☀️ ปกติ/เล็กน้อย", n_ok, "#10b981")]
        for lab, cnt, col in levels:
            pct = cnt/total*100
            st.markdown(f"""
            <div style='margin:9px 0;'>
                <div style='display:flex;justify-content:space-between;margin-bottom:4px;'>
                    <span style='color:#9fbcd0;font-size:0.84rem;'>{lab}</span>
                    <span style='color:#fff;font-weight:700;font-family:Kanit;'>{cnt} <span style='color:#5f8199;font-size:0.78rem;'>({pct:.0f}%)</span></span>
                </div>
                <div style='background:rgba(255,255,255,0.05);border-radius:8px;height:12px;overflow:hidden;'>
                    <div style='width:{pct:.1f}%;height:100%;background:{col};border-radius:8px;box-shadow:0 0 10px {col}66;'></div>
                </div>
            </div>""", unsafe_allow_html=True)

        # overall verdict
        if n_crit>0: ov_c,ov_t,ov_d = "#ef4444","🚨 ระดับวิกฤต","ควรพิจารณามาตรการชะลอ/งดเดินรถบางช่วง"
        elif n_heavy>0: ov_c,ov_t,ov_d = "#f59e0b","⚠️ ต้องเฝ้าระวัง","ติดตามใกล้ชิดและเตรียมความพร้อม"
        elif n_med>0: ov_c,ov_t,ov_d = "#3b82f6","ℹ️ ปกติ-เฝ้าระวัง","มีฝนปานกลางบางจุด"
        elif n_ok>0: ov_c,ov_t,ov_d = "#10b981","✅ ปลอดภัย","เดินรถได้ตามปกติทุกสาย"
        else: ov_c,ov_t,ov_d = "#5f8199","— ไม่มีข้อมูล","รอเชื่อมต่อข้อมูล"
        st.markdown(f"""
        <div style='margin-top:14px;background:rgba(0,0,0,0.25);border:1px solid {ov_c};border-radius:12px;padding:14px 18px;'>
            <div style='display:flex;justify-content:space-between;align-items:center;'>
                <div><div style='color:#5f8199;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.6px;'>สถานะการเดินรถ (ด้านสภาพอากาศ)</div>
                <div style='font-family:Kanit;color:{ov_c};font-size:1.4rem;font-weight:700;'>{ov_t}</div></div>
            </div>
            <div style='color:#9fbcd0;font-size:0.84rem;margin-top:4px;'>💡 {ov_d}</div>
        </div></div>""", unsafe_allow_html=True)

    # — Top risk stations —
    with c2:
        st.markdown("<div class='panel'><div class='panel-h'>🚨 สถานีเสี่ยงสูงสุด</div>", unsafe_allow_html=True)
        top = sorted([s for s in station_data if s["rain"] is not None],
                     key=lambda x:x["rain"], reverse=True)[:6]
        if not top:
            st.markdown("<p style='color:#5f8199;font-size:0.84rem;'>ยังไม่มีข้อมูลปริมาณฝน</p>", unsafe_allow_html=True)
        else:
            for i, s in enumerate(top, 1):
                lv,lab,em,hx,bc = rain_risk(s["rain"])
                st.markdown(f"""
                <div class='risk-item'>
                    <div class='risk-rank'>{i}</div>
                    <div class='risk-body'>
                        <div class='risk-stn'>{em} {s['name']}</div>
                        <div class='risk-meta'>{s['province']} · {s['line']} · กม.{s.get('km',0)}</div>
                    </div>
                    <div style='text-align:right;'>
                        <div class='risk-num' style='color:{hx};'>{s['rain']:.0f}<span style='font-size:0.7rem;color:#5f8199;'> มม.</span></div>
                        <span class='bdg {bc}'>{lab}</span>
                    </div>
                </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # — Per-line rainfall bars —
    st.markdown("<div class='panel'><div class='panel-h'>🌧️ ปริมาณน้ำฝนเฉลี่ย/สูงสุด แยกตามสายทาง</div>", unsafe_allow_html=True)
    line_stat = {}
    for s in station_data:
        L = s["line"]
        line_stat.setdefault(L, {"vals":[], "color":s["line_color"], "icon":s["line_icon"]})
        if s["rain"] is not None: line_stat[L]["vals"].append(s["rain"])
    maxbar = max((max(v["vals"]) for v in line_stat.values() if v["vals"]), default=10)
    maxbar = max(maxbar, 10)
    for L, st_ in line_stat.items():
        v = st_["vals"]
        mx = max(v) if v else 0
        av = sum(v)/len(v) if v else 0
        w = mx/maxbar*100 if mx else 0
        hx = rain_hex(mx)
        st.markdown(f"""
        <div class='rain-row'>
            <div class='rain-name'>{st_['icon']} {L}</div>
            <div class='rain-track'>
                <div class='rain-fill' style='width:{w:.1f}%;background:linear-gradient(90deg,{hx}99,{hx});'>
                    <span style='font-size:0.7rem;color:#fff;font-weight:700;'>{("เฉลี่ย "+format(av,'.0f')) if av else ""}</span>
                </div>
            </div>
            <div class='rain-val' style='color:{hx};'>{mx:.0f}</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("<div style='color:#5f8199;font-size:0.74rem;margin-top:8px;'>แถบแสดงปริมาณฝนสูงสุดของแต่ละสาย (มม.) · ตัวเลขในแถบคือค่าเฉลี่ย</div></div>", unsafe_allow_html=True)

# ╔═══════════════════════════════════════════════════════════╗
# ║  TAB: RAINFALL FOCUS                                      ║
# ╚═══════════════════════════════════════════════════════════╝
with tab_rain:
    st.markdown("<div class='sec-label'>ปริมาณน้ำฝนรายสถานี — เรียงจากมากไปน้อย</div>", unsafe_allow_html=True)

    ranked = sorted(station_data, key=lambda x: x["rain"] if x["rain"] is not None else -1, reverse=True)
    maxr = max([r for r in rains], default=10) or 10

    colL, colR = st.columns(2)
    half = (len(ranked)+1)//2
    for ci, chunk in enumerate([ranked[:half], ranked[half:]]):
        with (colL if ci==0 else colR):
            for s in chunk:
                lv,lab,em,hx,bc = rain_risk(s["rain"])
                rv = s["rain"]
                w = (rv/maxr*100) if rv else 0
                rain_disp = f"{rv:.1f}" if rv is not None else "—"
                st.markdown(f"""
                <div style='background:#0e1a29;border:1px solid #1c3247;border-radius:10px;padding:10px 14px;margin:5px 0;'>
                    <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;'>
                        <span style='color:#e8f1f8;font-size:0.86rem;font-weight:600;'>{em} {s['name']}</span>
                        <span style='font-family:Kanit;font-weight:700;color:{hx};font-size:1rem;'>{rain_disp}<span style='font-size:0.7rem;color:#5f8199;'> มม.</span></span>
                    </div>
                    <div style='background:rgba(255,255,255,0.05);border-radius:6px;height:8px;overflow:hidden;'>
                        <div style='width:{w:.1f}%;height:100%;background:{hx};border-radius:6px;'></div>
                    </div>
                    <div style='display:flex;justify-content:space-between;margin-top:5px;'>
                        <span style='color:#5f8199;font-size:0.72rem;'>{s['line_short']} · {s['province']}</span>
                        <span class='bdg {bc}' style='font-size:0.66rem;'>{lab}</span>
                    </div>
                </div>""", unsafe_allow_html=True)

    # rainfall criteria reference
    st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='panel'><div class='panel-h'>📋 เกณฑ์ปริมาณน้ำฝน (กรมอุตุนิยมวิทยา) และคำแนะนำการเดินรถ</div>", unsafe_allow_html=True)
    crit_rows = [
        ("☀️","ไม่มีฝน / เล็กน้อย","0–10 มม./วัน","#10b981","เดินรถปกติ"),
        ("🌧️","ฝนปานกลาง","10–35 มม./วัน","#3b82f6","เฝ้าระวัง ตรวจสอบทางตามปกติ"),
        ("⛈️","ฝนหนัก","35–90 มม./วัน","#f59e0b","ลดความเร็ว ตรวจสอบจุดเสี่ยงน้ำท่วม/ดินสไลด์"),
        ("🌊","ฝนหนักมาก","> 90 มม./วัน","#ef4444","พิจารณาชะลอ/งดเดินรถ ตรวจสอบสะพานและคันทาง"),
    ]
    for em,lab,rng,hx,act in crit_rows:
        st.markdown(f"""
        <div style='display:grid;grid-template-columns:40px 150px 130px 1fr;align-items:center;gap:12px;padding:8px 0;border-bottom:1px solid rgba(28,50,71,0.4);'>
            <span style='font-size:1.3rem;'>{em}</span>
            <span style='color:{hx};font-weight:700;font-size:0.86rem;'>{lab}</span>
            <span style='color:#9fbcd0;font-size:0.82rem;'>{rng}</span>
            <span style='color:#9fbcd0;font-size:0.82rem;'>💡 {act}</span>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ╔═══════════════════════════════════════════════════════════╗
# ║  TAB: MAP                                                 ║
# ╚═══════════════════════════════════════════════════════════╝
with tab_map:
    st.markdown("<div class='sec-label'>แผนที่โครงข่าย — สีหมุดตามระดับปริมาณน้ำฝน</div>", unsafe_allow_html=True)
    try:
        import folium
        from streamlit_folium import st_folium
        m = folium.Map(location=[13.5,101.5], zoom_start=6, tiles=None)
        folium.TileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
                         attr="© CARTO", name="Dark", max_zoom=19).add_to(m)
        for ln, ld in SRT_LINES.items():
            if sel_line!="ทุกสาย" and ln!=sel_line: continue
            coords=[[s["lat"],s["lon"]] for s in ld["stations"]]
            folium.PolyLine(coords, color=ld["color"], weight=3.5, opacity=0.8, tooltip=ln).add_to(m)
        for s in station_data:
            lv,lab,em,hx,bc = rain_risk(s["rain"])
            ic = {"#ef4444":"red","#f59e0b":"orange","#3b82f6":"blue","#22c55e":"green",
                  "#10b981":"green","#5f8199":"gray"}.get(hx,"blue")
            rv = f"{s['rain']:.1f} มม." if s["rain"] is not None else "N/A"
            tx = f"{s['tc_max']:.0f}/{s['tc_min']:.0f}°C" if s["tc_max"] is not None and s["tc_min"] is not None else "N/A"
            cd = cond_text(s["cond"]) if s["cond"] is not None else "N/A"
            pop = (f"<div style='font-family:Sarabun;min-width:170px;'>"
                   f"<b style='font-size:0.95rem;'>{s['name']}</b><br>"
                   f"<span style='color:#666;font-size:0.78rem;'>{s['province']} · {s['line']}</span><hr style='margin:5px 0;'>"
                   f"<b>🌧️ ฝน: {rv}</b><br>⚠️ {em} {lab}<br>🌡️ {tx}<br>☁️ {cd}</div>")
            folium.Marker([s["lat"],s["lon"]], popup=folium.Popup(pop,max_width=240),
                          tooltip=f"{s['name']} · {rv}",
                          icon=folium.Icon(color=ic, icon="train", prefix="fa")).add_to(m)
        st.caption("🔴 ฝนหนักมาก · 🟠 ฝนหนัก · 🔵 ฝนปานกลาง · 🟢 ปกติ — คลิกหมุดเพื่อดูรายละเอียด")
        st_folium(m, width="100%", height=560, returned_objects=[])
    except ImportError:
        mdf = pd.DataFrame([{"lat":s["lat"],"lon":s["lon"]} for s in station_data])
        if not mdf.empty: st.map(mdf, latitude="lat", longitude="lon")

# ╔═══════════════════════════════════════════════════════════╗
# ║  TAB: PER LINE                                            ║
# ╚═══════════════════════════════════════════════════════════╝
with tab_lines:
    lines_show = [sel_line] if sel_line!="ทุกสาย" else list(SRT_LINES.keys())
    for ln in lines_show:
        ld = SRT_LINES[ln]
        lstn = [s for s in station_data if s["line"]==ln]
        lr = [s["rain"] for s in lstn if s["rain"] is not None]
        lmax = max(lr) if lr else None
        lavg = sum(lr)/len(lr) if lr else None
        lheavy = sum(1 for r in lr if r>=35)
        title = f"{ld['icon']} {ln} — {ld['desc']}   |   {'🚨 '+str(lheavy)+' สถานีเสี่ยง' if lheavy else '✅ ปกติ'}"
        with st.expander(title, expanded=(sel_line!="ทุกสาย")):
            mc = st.columns(4)
            mc[0].metric("🌧️ ฝนสูงสุด", f"{lmax:.0f} มม." if lmax is not None else "—")
            mc[1].metric("📊 ฝนเฉลี่ย", f"{lavg:.1f} มม." if lavg is not None else "—")
            mc[2].metric("⛈️ สถานีเสี่ยง", f"{lheavy} สถานี")
            mc[3].metric("📍 สถานีทั้งหมด", f"{len(lstn)} สถานี")
            rows=[]
            for s in lstn:
                lv,lab,em,hx,bc = rain_risk(s["rain"])
                rows.append({
                    "กม.":s.get("km",0),
                    "สถานี":f"🚉 {s['name']}",
                    "จังหวัด":s["province"],
                    "ฝน (มม.)":round(s["rain"],1) if s["rain"] is not None else None,
                    "ระดับ":f"{em} {lab}",
                    "Tmax/Tmin":f"{s['tc_max']:.0f}/{s['tc_min']:.0f}°" if s["tc_max"] is not None and s["tc_min"] is not None else "—",
                    "RH%":round(s["rh"],0) if s["rh"] is not None else None,
                    "สภาพอากาศ":cond_text(s["cond"]) if s["cond"] is not None else "—",
                })
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True,
                    column_config={"ฝน (มม.)":st.column_config.NumberColumn("🌧️ ฝน (มม.)",format="%.1f"),
                                   "RH%":st.column_config.NumberColumn("💧 RH%",format="%.0f")})

# ╔═══════════════════════════════════════════════════════════╗
# ║  TAB: STATION DEEP-DIVE                                   ║
# ╚═══════════════════════════════════════════════════════════╝
with tab_detail:
    st.markdown("<div class='sec-label'>เจาะลึกพยากรณ์รายสถานี</div>", unsafe_allow_html=True)
    if not api_ok:
        st.info("ℹ️ ต้องเชื่อมต่อ TMD API ก่อน")
    else:
        names = [s["name"] for s in station_data]
        sel_stn = st.selectbox("เลือกสถานี", names) if names else None
        stn = next((s for s in station_data if s["name"]==sel_stn), None)
        if stn:
            # 7-day outlook from series
            series = stn.get("series", [])
            st.markdown(f"<div class='panel'><div class='panel-h'>📅 แนวโน้ม 7 วัน — {stn['name']} ({stn['province']})</div>", unsafe_allow_html=True)
            if series:
                day_cols = st.columns(min(len(series),7))
                for i, f in enumerate(series[:7]):
                    lv,lab,em,hx,bc = rain_risk(f["rain"])
                    tdate = f["time"][5:10] if len(f["time"])>=10 else f"+{i}"
                    rain_d = f"{f['rain']:.0f}" if f["rain"] is not None else "—"
                    temp_d = f"{f['tc_max']:.0f}°" if f["tc_max"] is not None else "—"
                    with day_cols[i]:
                        st.markdown(f"""
                        <div style='background:#0e1a29;border:1px solid #1c3247;border-top:3px solid {hx};
                            border-radius:10px;padding:10px 6px;text-align:center;'>
                            <div style='color:#5f8199;font-size:0.7rem;'>{tdate}</div>
                            <div style='font-size:1.6rem;margin:4px 0;'>{cond_emoji(f['cond'])}</div>
                            <div style='font-family:Kanit;color:{hx};font-weight:700;font-size:1.1rem;'>{rain_d}</div>
                            <div style='color:#5f8199;font-size:0.66rem;'>มม.</div>
                            <div style='color:#9fbcd0;font-size:0.74rem;margin-top:3px;'>🌡️ {temp_d}</div>
                        </div>""", unsafe_allow_html=True)
            else:
                st.info("ไม่มีข้อมูลแนวโน้มรายวัน")
            st.markdown("</div>", unsafe_allow_html=True)

            # Hourly 24h
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='panel'><div class='panel-h'>🕐 พยากรณ์ราย 24 ชั่วโมง</div>", unsafe_allow_html=True)
            with st.spinner("กำลังโหลด..."):
                hd = fetch_hourly_at(stn["lat"], stn["lon"], _token(), hours=24)
                hf = parse_hourly(hd)
                if not hf and stn.get("province"):
                    hd = fetch_hourly_place(stn["province"], _token(), hours=24)
                    hf = parse_hourly(hd)
            if hf:
                hrows=[]
                for f in hf:
                    t=f["time"]; hh=t[11:16] if len(t)>=16 else t
                    hrows.append({"เวลา":hh,
                        "🌡️ อุณหภูมิ (°C)":round(f["tc"],1) if f["tc"] is not None else None,
                        "🌧️ ฝน (มม.)":round(f["rain"],1) if f["rain"] is not None else None,
                        "💧 RH%":round(f["rh"],0) if f["rh"] is not None else None,
                        "💨 ลม (m/s)":round(f["ws"],1) if f["ws"] is not None else None,
                        "☁️ สภาพ":cond_text(f["cond"]) if f["cond"] is not None else "—"})
                st.dataframe(pd.DataFrame(hrows), use_container_width=True, hide_index=True, height=420)
            else:
                st.info("ไม่มีข้อมูลพยากรณ์ราย ชม.")
            st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  FOOTER + AUTO-REFRESH
# ══════════════════════════════════════════════════════════════
st.markdown("<hr style='border-color:#1c3247;margin:20px 0 10px;'>", unsafe_allow_html=True)
st.markdown(f"""
<div style='display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;color:#3a5570;font-size:0.74rem;'>
    <span>🚆 SRT Weather Command Center · สำหรับผู้บริหารงานเดินรถ</span>
    <span>ข้อมูล: <a href='https://data.tmd.go.th/nwpapi/doc/main/getting_start.html' target='_blank' style='color:#38bdf8;'>TMD NWP API v1</a> · โครงข่าย: <a href='https://datagov.mot.go.th' target='_blank' style='color:#38bdf8;'>รฟท.</a></span>
    <span>อัพเดต {th_datetime(NOW_TH)}</span>
</div>""", unsafe_allow_html=True)

if auto and refresh_sec>0:
    done=False
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=refresh_sec*1000, key="rt")
        done=True
    except Exception:
        done=False
    if not done:
        st.markdown(f"<script>setTimeout(function(){{window.location.reload();}},{refresh_sec*1000});</script>", unsafe_allow_html=True)
