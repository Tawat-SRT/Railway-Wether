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
@import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@300;400;500;600;700;800&family=Kanit:wght@400;500;600;700;800&display=swap');

*, html, body, [class*="css"] { font-family: 'Sarabun', sans-serif !important; }
h1,h2,h3,.kanit { font-family: 'Kanit', sans-serif !important; }

:root {
    --bg0:#f4f7fb; --bg1:#ffffff; --bg2:#eef3f9; --panel:#ffffff;
    --line:#e3eaf2; --line2:#d3deeb;
    --ink:#1a2b42; --ink2:#5a6e88; --ink3:#90a2bb;
    --accent:#2563eb; --accent2:#0ea5e9; --gold:#c79a2e;
    --ok:#059669; --info:#2563eb; --warn:#e8820c; --crit:#dc2626;
    --shadow: 0 2px 8px rgba(30,58,95,0.06), 0 8px 24px rgba(30,58,95,0.05);
    --shadow-lg: 0 8px 30px rgba(30,58,95,0.10);
}

/* ── soft pastel aurora background ── */
.stApp {
    background:
        radial-gradient(820px 540px at 88% -8%, rgba(37,99,235,0.07), transparent 60%),
        radial-gradient(680px 520px at 6% 4%, rgba(14,165,233,0.06), transparent 58%),
        radial-gradient(760px 660px at 50% 112%, rgba(139,92,246,0.05), transparent 60%),
        linear-gradient(180deg, #f6f9fd 0%, #eef3fa 55%, #f4f7fb 100%);
    background-attachment: fixed;
}
.stApp::before {
    content:''; position:fixed; inset:0; z-index:0; pointer-events:none;
    background-image:
        linear-gradient(rgba(37,99,235,0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(37,99,235,0.035) 1px, transparent 1px);
    background-size: 46px 46px;
    mask-image: radial-gradient(ellipse 75% 55% at 50% 25%, #000 35%, transparent 88%);
    -webkit-mask-image: radial-gradient(ellipse 75% 55% at 50% 25%, #000 35%, transparent 88%);
}
.block-container { padding-top: 1.4rem !important; max-width: 1500px; position:relative; z-index:1; }

/* ── Sidebar (clean white) ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#ffffff,#f3f7fc) !important;
    border-right: 1px solid var(--line) !important;
}
[data-testid="stSidebar"] * { color: var(--ink2) !important; }
[data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 { color: var(--ink) !important; }

/* hide top-right controls */
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }
#MainMenu { visibility: hidden !important; }
header { visibility: hidden !important; }
footer { visibility: hidden !important; }
.stDeployButton { display: none !important; }

/* ── Command header (light, glassy) ── */
.cmd-header {
    background: linear-gradient(110deg, #ffffff 0%, #eaf2fe 50%, #ffffff 100%);
    border: 1px solid var(--line2);
    border-radius: 18px;
    padding: 22px 28px;
    position: relative; overflow: hidden;
    box-shadow: var(--shadow-lg);
}
.cmd-header::before {
    content:''; position:absolute; left:0; top:0; bottom:0; width:6px;
    background: linear-gradient(180deg,#2563eb,#0ea5e9);
}
.cmd-title { font-size:1.75rem; font-weight:800; color:var(--ink); margin:0;
    letter-spacing:0.2px; display:flex; align-items:center; gap:12px; }
.cmd-sub { color:var(--ink2); font-size:0.88rem; margin-top:5px; font-weight:600; }
.cmd-live {
    display:inline-flex; align-items:center; gap:6px;
    background:rgba(5,150,105,0.10); border:1px solid rgba(5,150,105,0.30);
    color:#059669; font-size:0.74rem; font-weight:700; padding:4px 13px; border-radius:20px;
}
.pulse { width:8px; height:8px; border-radius:50%; background:#10b981;
    box-shadow:0 0 0 0 rgba(16,185,129,0.5); animation:pulse 2s infinite; }
@keyframes pulse { 0%{box-shadow:0 0 0 0 rgba(16,185,129,0.5);} 70%{box-shadow:0 0 0 8px rgba(16,185,129,0);} 100%{box-shadow:0 0 0 0 rgba(16,185,129,0);} }

/* ── Alert banner ── */
.alert-banner { border-radius:16px; padding:16px 22px; margin:14px 0;
    display:flex; align-items:center; gap:16px; border:1px solid; box-shadow:var(--shadow); }
.ab-crit { background:linear-gradient(100deg,#fef2f2,#fee2e2); border-color:#fca5a5; }
.ab-warn { background:linear-gradient(100deg,#fffbeb,#fef3c7); border-color:#fcd34d; }
.ab-ok   { background:linear-gradient(100deg,#f0fdf4,#dcfce7); border-color:#86efac; }
.ab-icon { font-size:2.4rem; line-height:1; }
.ab-text h3 { margin:0; font-size:1.18rem; color:var(--ink); }
.ab-text p  { margin:3px 0 0; font-size:0.88rem; color:var(--ink2); }

/* ── KPI tiles ── */
.kpi { background:var(--panel); border:1px solid var(--line); border-radius:16px;
    padding:18px 20px; height:100%; position:relative; overflow:hidden;
    box-shadow:var(--shadow); transition:transform .14s, box-shadow .14s; }
.kpi:hover { transform:translateY(-3px); box-shadow:var(--shadow-lg); }
.kpi::after { content:''; position:absolute; top:0; left:0; width:100%; height:4px; background:var(--c,#2563eb); }
.kpi-top { display:flex; align-items:center; justify-content:space-between; }
.kpi-ico { font-size:1.5rem; }
.kpi-tag { font-size:0.66rem; font-weight:700; padding:3px 9px; border-radius:10px;
    background:var(--bg2); color:var(--ink3); text-transform:uppercase; letter-spacing:0.5px; }
.kpi-val { font-family:'Kanit',sans-serif; font-size:2.1rem; font-weight:700; color:var(--ink); line-height:1; margin:10px 0 2px; }
.kpi-val small { font-size:0.85rem; color:var(--ink2); font-weight:500; margin-left:3px; }
.kpi-lab { color:var(--ink2); font-size:0.82rem; font-weight:600; }
.kpi-foot { color:var(--ink3); font-size:0.74rem; margin-top:6px; }
.c-crit{--c:#dc2626;} .c-warn{--c:#e8820c;} .c-info{--c:#2563eb;}
.c-ok{--c:#059669;} .c-gold{--c:#c79a2e;} .c-cyan{--c:#0ea5e9;}

/* ── Panel ── */
.panel { background:var(--panel); border:1px solid var(--line); border-radius:16px;
    padding:18px 20px; height:100%; box-shadow:var(--shadow); }
.panel-h { font-family:'Kanit',sans-serif; color:var(--ink); font-size:0.95rem; font-weight:600;
    margin:0 0 14px; display:flex; align-items:center; gap:8px;
    border-bottom:1px solid var(--line); padding-bottom:10px; }

/* ── Rain bar ── */
.rain-row { display:grid; grid-template-columns:130px 1fr 64px; align-items:center; gap:12px; padding:7px 0; }
.rain-name { color:var(--ink); font-size:0.84rem; font-weight:600; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.rain-track { background:var(--bg2); border-radius:8px; height:22px; position:relative; overflow:hidden; }
.rain-fill { height:100%; border-radius:8px; display:flex; align-items:center; justify-content:flex-end;
    padding-right:8px; transition:width .5s cubic-bezier(.4,0,.2,1); min-width:2px; }
.rain-val { text-align:right; font-family:'Kanit',sans-serif; font-weight:700; font-size:0.9rem; }

/* ── Risk list ── */
.risk-item { display:flex; align-items:center; gap:12px; padding:10px 0; border-bottom:1px solid var(--line); }
.risk-rank { font-family:'Kanit',sans-serif; font-weight:700; font-size:1.1rem; color:var(--ink3); width:24px; text-align:center; }
.risk-body { flex:1; min-width:0; }
.risk-stn { color:var(--ink); font-weight:600; font-size:0.88rem; }
.risk-meta { color:var(--ink3); font-size:0.74rem; }
.risk-num { font-family:'Kanit',sans-serif; font-weight:700; font-size:1.15rem; text-align:right; }

/* ── badges ── */
.bdg { padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:700; white-space:nowrap; }
.bdg-crit{ background:#fee2e2; color:#b91c1c; } .bdg-warn{ background:#fef3c7; color:#b45309; }
.bdg-info{ background:#dbeafe; color:#1d4ed8; } .bdg-ok{ background:#dcfce7; color:#047857; }
.bdg-na{ background:#eef2f6; color:#64748b; }

/* ── Streamlit overrides ── */
.stTabs [data-baseweb="tab-list"] { background:var(--bg1); border:1px solid var(--line);
    border-radius:14px; gap:3px; padding:5px; box-shadow:var(--shadow); }
.stTabs [data-baseweb="tab"] { color:var(--ink3); border-radius:10px; padding:8px 18px; font-weight:600; }
.stTabs [aria-selected="true"] { background:linear-gradient(135deg,#2563eb,#0ea5e9); color:#fff !important; }
.stTabs [data-baseweb="tab"]:hover { color:var(--accent); }

div[data-testid="stMetric"]{ background:var(--panel); border:1px solid var(--line);
    border-radius:14px; padding:14px 16px; box-shadow:var(--shadow); }
div[data-testid="stMetric"] label{ color:var(--ink3) !important; font-size:0.76rem !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"]{ color:var(--ink) !important; font-family:'Kanit'; }

div[data-baseweb="select"] > div{ background:var(--bg1) !important; border-color:var(--line2) !important; }
div[data-baseweb="select"] *{ color:var(--ink) !important; }
.stTextInput input, .stDateInput input { background:var(--bg1) !important; color:var(--ink) !important; border-color:var(--line2) !important; }

.stButton > button{ background:linear-gradient(135deg,#2563eb,#0ea5e9) !important; color:#fff !important;
    border:none !important; border-radius:11px !important; font-weight:700 !important; box-shadow:var(--shadow); }
.stButton > button:hover{ box-shadow:0 4px 18px rgba(37,99,235,0.35) !important; transform:translateY(-1px); }

div[data-testid="stExpander"]{ background:var(--panel) !important; border:1px solid var(--line) !important;
    border-radius:14px !important; box-shadow:var(--shadow); }
div[data-testid="stExpander"] summary { color:var(--ink) !important; font-weight:600; }
.stDataFrame{ border-radius:12px !important; overflow:hidden !important; border:1px solid var(--line); }

[data-testid="stToggle"] label, .stRadio label, .stCheckbox label { color:var(--ink2) !important; }

::-webkit-scrollbar{ width:8px; height:8px; }
::-webkit-scrollbar-track{ background:var(--bg2); }
::-webkit-scrollbar-thumb{ background:#c2d1e3; border-radius:4px; }
::-webkit-scrollbar-thumb:hover{ background:#a9bcd4; }

.sec-label { font-family:'Kanit',sans-serif; color:var(--ink); font-size:1.05rem; font-weight:600;
    margin:6px 0 12px; display:flex; align-items:center; gap:10px; }
.sec-label::before { content:''; width:4px; height:18px; background:linear-gradient(180deg,#2563eb,#0ea5e9); border-radius:2px; }

/* ════════════ GRAPHIC FLOURISHES & ANIMATIONS ════════════ */

/* entrance fade-up for major blocks */
@keyframes fadeUp { from{opacity:0; transform:translateY(14px);} to{opacity:1; transform:translateY(0);} }
.cmd-header, .alert-banner, .kpi, .panel { animation: fadeUp .5s cubic-bezier(.2,.7,.3,1) both; }
.kpi:nth-child(1){animation-delay:.03s} .kpi:nth-child(2){animation-delay:.08s}
.kpi:nth-child(3){animation-delay:.13s} .kpi:nth-child(4){animation-delay:.18s}
.kpi:nth-child(5){animation-delay:.23s} .kpi:nth-child(6){animation-delay:.28s}

/* animated sheen across the header */
.cmd-header { position:relative; }
.cmd-header::after {
    content:''; position:absolute; top:0; left:-60%; width:50%; height:100%;
    background:linear-gradient(100deg, transparent, rgba(37,99,235,0.10), transparent);
    transform:skewX(-18deg); animation:sheen 6s ease-in-out infinite;
}
@keyframes sheen { 0%{left:-60%} 55%{left:140%} 100%{left:140%} }

/* gradient animated title text */
.cmd-title {
    background:linear-gradient(90deg,#1a2b42,#2563eb,#0ea5e9,#1a2b42);
    background-size:300% 100%;
    -webkit-background-clip:text; background-clip:text;
    -webkit-text-fill-color:transparent;
    animation:titleflow 8s ease infinite;
}
@keyframes titleflow { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }

/* KPI glow ring + shimmer top bar */
.kpi::after { background:linear-gradient(90deg,var(--c,#2563eb),transparent,var(--c,#2563eb)); background-size:200% 100%; animation:barflow 3s linear infinite; }
@keyframes barflow { 0%{background-position:0% 0} 100%{background-position:200% 0} }
.kpi::before {
    content:''; position:absolute; inset:0; border-radius:16px; padding:1px;
    background:linear-gradient(135deg, var(--c,#2563eb)33, transparent 40%);
    -webkit-mask:linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
    -webkit-mask-composite:xor; mask-composite:exclude; opacity:0; transition:opacity .2s;
}
.kpi:hover::before { opacity:1; }
.kpi:hover { transform:translateY(-4px) scale(1.012); }
.kpi-ico { display:inline-block; transition:transform .2s; }
.kpi:hover .kpi-ico { transform:scale(1.18) rotate(-6deg); }
.kpi-val { background:linear-gradient(120deg,var(--ink),var(--c,#2563eb)); -webkit-background-clip:text; background-clip:text; -webkit-text-fill-color:transparent; }

/* alert banner soft breathing glow */
.ab-crit { animation: fadeUp .5s both, glowcrit 2.2s ease-in-out infinite; }
@keyframes glowcrit { 0%,100%{box-shadow:0 0 0 0 rgba(220,38,38,0.0), var(--shadow)} 50%{box-shadow:0 0 22px 2px rgba(220,38,38,0.18), var(--shadow)} }
.ab-icon { animation: bob 2.6s ease-in-out infinite; }
@keyframes bob { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-4px)} }

/* panel hover lift */
.panel { transition:transform .15s, box-shadow .15s; }
.panel:hover { transform:translateY(-2px); box-shadow:var(--shadow-lg); }
.panel-h::after { content:''; flex:1; height:1px; margin-left:6px;
    background:linear-gradient(90deg,var(--line),transparent); }

/* buttons: gradient shift + ripple shine */
.stButton > button{ position:relative; overflow:hidden;
    background:linear-gradient(135deg,#2563eb,#0ea5e9,#2563eb) !important; background-size:200% 100% !important;
    transition:background-position .4s, box-shadow .2s, transform .12s !important; }
.stButton > button:hover{ background-position:100% 0 !important; transform:translateY(-2px) !important;
    box-shadow:0 6px 22px rgba(37,99,235,0.40) !important; }
.stButton > button:active{ transform:translateY(0) scale(.98) !important; }
.stButton > button::after{ content:''; position:absolute; top:0; left:-120%; width:60%; height:100%;
    background:linear-gradient(100deg,transparent,rgba(255,255,255,0.45),transparent); transform:skewX(-20deg); }
.stButton > button:hover::after{ animation:btnshine .7s ease; }
@keyframes btnshine { from{left:-120%} to{left:140%} }

/* tabs: animated underline + lift */
.stTabs [data-baseweb="tab"]{ transition:color .2s, background .2s, transform .12s; }
.stTabs [data-baseweb="tab"]:hover{ transform:translateY(-1px); }
.stTabs [aria-selected="true"]{ box-shadow:0 4px 14px rgba(37,99,235,0.32); }

/* rain-fill animated stripes */
.rain-fill{ position:relative; overflow:hidden; }
.rain-fill::after{ content:''; position:absolute; inset:0;
    background-image:linear-gradient(45deg, rgba(255,255,255,0.18) 25%, transparent 25%, transparent 50%, rgba(255,255,255,0.18) 50%, rgba(255,255,255,0.18) 75%, transparent 75%);
    background-size:18px 18px; animation:stripes 1s linear infinite; opacity:.6; }
@keyframes stripes { from{background-position:0 0} to{background-position:18px 0} }

/* risk item hover slide */
.risk-item{ transition:background .15s, padding-left .15s; border-radius:8px; }
.risk-item:hover{ background:#f3f7fc; padding-left:8px; }

/* badge pop */
.bdg{ transition:transform .12s; display:inline-block; }
.bdg:hover{ transform:scale(1.08); }

/* live pill glow */
.cmd-live{ box-shadow:0 0 0 0 rgba(5,150,105,0.0); animation:livepulse 2.4s ease-in-out infinite; }
@keyframes livepulse { 0%,100%{box-shadow:0 0 0 0 rgba(5,150,105,0)} 50%{box-shadow:0 0 14px 1px rgba(5,150,105,0.25)} }

/* metric tiles hover */
div[data-testid="stMetric"]{ transition:transform .14s, box-shadow .14s; }
div[data-testid="stMetric"]:hover{ transform:translateY(-2px); box-shadow:var(--shadow-lg); }

/* dataframe rounded glow on hover */
.stDataFrame:hover{ box-shadow:var(--shadow-lg); transition:box-shadow .2s; }

/* scrollbar gradient */
::-webkit-scrollbar-thumb{ background:linear-gradient(180deg,#9bb6d6,#c2d1e3); }

/* sidebar section headers get a tiny accent dot */
[data-testid="stSidebar"] hr{ border:none; height:1px; background:linear-gradient(90deg,var(--line),transparent) !important; }

/* floating weather emoji shimmer for KPI icons handled inline */
@keyframes floaty { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-3px)} }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  TOKEN  — เชื่อมต่ออัตโนมัติ (ฝัง Token ในตัว) + จดจำถาวร
# ══════════════════════════════════════════════════════════════
import os
_TK_FILE = os.path.join(os.path.expanduser("~"), ".srt_weather_token")

# Token เริ่มต้นในตัว — เชื่อมต่อ TMD API อัตโนมัติทันทีโดยไม่ต้องกรอก
# (uid 5439 · หมดอายุ 19 มิ.ย. 2570)
_DEFAULT_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImp0aSI6IjMyNjM1OTYxZmM5OWFiYjVmZGFlYTU0MTczZTkwM2IzYzU0YjgyMTAyZTZhODEyZjlmODRjMjIzMzQ5N2M2YjZiNzBkOWU3ODYwOTZjODJjIn0.eyJhdWQiOiIyIiwianRpIjoiMzI2MzU5NjFmYzk5YWJiNWZkYWVhNTQxNzNlOTAzYjNjNTRiODIxMDJlNmE4MTJmOWY4NGMyMjMzNDk3YzZiNmI3MGQ5ZTc4NjA5NmM4MmMiLCJpYXQiOjE3ODE4NDI0NjksIm5iZiI6MTc4MTg0MjQ2OSwiZXhwIjoxODEzMzc4NDY5LCJzdWIiOiI1NDM5Iiwic2NvcGVzIjpbXX0.QwSO6DPacn7f-jjDAdMEraGS8HSwJkuz8y0aq1tXdPBgkNQyNnNQ7OhvIFLMwlSFThUcj46uC63ZfUiXXI3xrZC_-ACMrQdKJ4RbECcqEcWq_kuVDjoEDgs5HqadIr0eo3EfH2eNTWJieW-Uw4KZfds4i9m4CrQXGkoZN315-yXiwepz5lm9n-3Wi4GWGviaaR9kEORHOJrK0Btjipzi9VPI4cegEX01j4eri3sEzs4wVWh105RC3P3wKHbmNYEwt5T9KkewT_vMcZq6Ck5RMmtGUJu4DL1p1VOeCoUk7MbQoeYmHU3MCsGPsFHDgD7rTO7yl8NV7nszwqnR5L-9aCHZhgxKrDvcKY8sfn2ZgXNlyKm5ynu-LQJj4vpf41TjpZiydhyf6IIcxv3qGHv7utv4ynEbKNV4dA4C0LX1dkEMA3wFEcwfXv8gcBSBFEPKdpmJ44arcaqddK5UEMzGb13SFNHY2CJme9L5SCNoJvKgcm1FAH_LaRf4tWY3AZ_JL87AWURnnO8YxkM_PdKcHtmlbIBKksorofpfEj38fm6iV85dTa2d1N3hyzDKu7Z6zjtXKJYVQ0TlEn-JldGLrp_NPWi_FmPPDWMcRFhccMvm8ndNYjTJvLuCmNsZFw6BUQ3-JAGqwsJwLSWlmXnUF4QTdN91d3Tig4MiamC_P90"

def _decode_jwt(token):
    try:
        p = token.split(".")[1]; p += "=" * (-len(p) % 4)
        return json.loads(base64.urlsafe_b64decode(p))
    except Exception:
        return {}

def _save_token_file(raw):
    """บันทึก token ลงไฟล์เพื่อจดจำข้ามการรีสตาร์ท (best-effort)"""
    try:
        if raw:
            with open(_TK_FILE, "w") as f: f.write(raw)
        elif os.path.exists(_TK_FILE):
            os.remove(_TK_FILE)
    except Exception:
        pass

def _load_token_file():
    try:
        if os.path.exists(_TK_FILE):
            with open(_TK_FILE) as f: return f.read().strip()
    except Exception:
        pass
    return ""

def _set_token(raw):
    raw = (raw or "").strip()
    st.session_state["_tk"] = raw
    st.session_state["_tk_jwt"] = _decode_jwt(raw)
    st.session_state["_tk_uid"] = str(st.session_state["_tk_jwt"].get("sub",""))
    _save_token_file(raw)

def _is_expired(token):
    """ตรวจว่า token หมดอายุหรือยัง"""
    try:
        exp = _decode_jwt(token).get("exp", 0)
        return bool(exp) and exp < time.time()
    except Exception:
        return False

if "_tk" not in st.session_state:
    _boot = ""
    # 1) Streamlit secrets (ถ้าตั้งไว้ จะ override token ในตัว)
    try:
        _boot = str(st.secrets.get("TMD_TOKEN","") or st.secrets.get("tmd_token",""))
    except Exception:
        pass
    # 2) environment variable
    if not _boot:
        _boot = os.environ.get("TMD_TOKEN","")
    # 3) ไฟล์ที่ผู้ใช้เคยบันทึก (ข้ามถ้าหมดอายุแล้ว)
    if not _boot:
        _saved = _load_token_file()
        if _saved and not _is_expired(_saved):
            _boot = _saved
    # 4) Token เริ่มต้นในตัว — เชื่อมต่ออัตโนมัติ (ใช้เมื่อไม่มีแหล่งอื่น หรือของเดิมหมดอายุ)
    if not _boot:
        _boot = _DEFAULT_TOKEN
    st.session_state["_tk"] = _boot.strip()
    st.session_state["_tk_jwt"] = _decode_jwt(_boot.strip())
    st.session_state["_tk_uid"] = str(st.session_state["_tk_jwt"].get("sub",""))

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
            {"name":"บางซื่อ (กลางบางซื่อ)","lat":13.8021,"lon":100.5398,"province":"กรุงเทพมหานคร","km":7},
            {"name":"ดอนเมือง","lat":13.9186,"lon":100.5970,"province":"กรุงเทพมหานคร","km":22},
            {"name":"รังสิต","lat":14.0262,"lon":100.6162,"province":"ปทุมธานี","km":31},
            {"name":"อยุธยา","lat":14.3554,"lon":100.5679,"province":"พระนครศรีอยุธยา","km":71},
            {"name":"บ้านภาชี","lat":14.5283,"lon":100.7253,"province":"พระนครศรีอยุธยา","km":90},
            {"name":"ลพบุรี","lat":14.7987,"lon":100.6141,"province":"ลพบุรี","km":133},
            {"name":"ปากน้ำโพ/นครสวรรค์","lat":15.7028,"lon":100.1363,"province":"นครสวรรค์","km":246},
            {"name":"พิจิตร","lat":16.4365,"lon":100.3485,"province":"พิจิตร","km":347},
            {"name":"พิษณุโลก","lat":16.8204,"lon":100.2714,"province":"พิษณุโลก","km":389},
            {"name":"อุตรดิตถ์","lat":17.6236,"lon":100.0987,"province":"อุตรดิตถ์","km":485},
            {"name":"ศิลาอาสน์","lat":17.6097,"lon":100.0997,"province":"อุตรดิตถ์","km":488},
            {"name":"เด่นชัย","lat":17.9827,"lon":100.0569,"province":"แพร่","km":535},
            {"name":"ลำปาง","lat":18.2896,"lon":99.4905,"province":"ลำปาง","km":642},
            {"name":"ขุนตาน","lat":18.4392,"lon":99.0247,"province":"ลำพูน","km":683},
            {"name":"ลำพูน","lat":18.5746,"lon":99.0094,"province":"ลำพูน","km":729},
            {"name":"เชียงใหม่","lat":18.7883,"lon":98.9933,"province":"เชียงใหม่","km":751},
        ]},
    "สายตะวันออกเฉียงเหนือ": {"color":"#f59e0b","short":"NE","icon":"🟡","desc":"กรุงเทพ → หนองคาย · 624 กม.",
        "stations":[
            {"name":"กรุงเทพ (หัวลำโพง)","lat":13.7401,"lon":100.5178,"province":"กรุงเทพมหานคร","km":0},
            {"name":"รังสิต","lat":14.0262,"lon":100.6162,"province":"ปทุมธานี","km":31},
            {"name":"สระบุรี","lat":14.5291,"lon":100.9101,"province":"สระบุรี","km":107},
            {"name":"แก่งคอย","lat":14.5847,"lon":101.0017,"province":"สระบุรี","km":125},
            {"name":"ปากช่อง","lat":14.7043,"lon":101.4180,"province":"นครราชสีมา","km":180},
            {"name":"นครราชสีมา","lat":14.9734,"lon":102.1112,"province":"นครราชสีมา","km":264},
            {"name":"บัวใหญ่","lat":15.5887,"lon":102.4242,"province":"นครราชสีมา","km":361},
            {"name":"บ้านไผ่","lat":16.0608,"lon":102.7331,"province":"ขอนแก่น","km":410},
            {"name":"ขอนแก่น","lat":16.4419,"lon":102.8330,"province":"ขอนแก่น","km":449},
            {"name":"อุดรธานี","lat":17.4043,"lon":102.7877,"province":"อุดรธานี","km":569},
            {"name":"หนองคาย","lat":17.8818,"lon":102.7433,"province":"หนองคาย","km":624},
        ]},
    "สายอีสานใต้": {"color":"#a78bfa","short":"IS","icon":"🟣","desc":"นครราชสีมา → อุบลราชธานี · 305 กม.",
        "stations":[
            {"name":"นครราชสีมา (ถนนจิระ)","lat":14.9734,"lon":102.1112,"province":"นครราชสีมา","km":0},
            {"name":"ลำปลายมาศ","lat":14.9420,"lon":102.8331,"province":"บุรีรัมย์","km":75},
            {"name":"บุรีรัมย์","lat":14.9950,"lon":103.1030,"province":"บุรีรัมย์","km":101},
            {"name":"ลำชี","lat":14.9100,"lon":103.3500,"province":"สุรินทร์","km":125},
            {"name":"สุรินทร์","lat":14.8835,"lon":103.4935,"province":"สุรินทร์","km":142},
            {"name":"ศีขรภูมิ","lat":14.9466,"lon":103.7889,"province":"สุรินทร์","km":175},
            {"name":"ศรีสะเกษ","lat":15.1174,"lon":104.3221,"province":"ศรีสะเกษ","km":237},
            {"name":"กันทรารมย์","lat":15.0900,"lon":104.6000,"province":"ศรีสะเกษ","km":270},
            {"name":"อุบลราชธานี (วารินชำราบ)","lat":15.2241,"lon":104.8579,"province":"อุบลราชธานี","km":305},
        ]},
    "สายใต้": {"color":"#34d399","short":"S","icon":"🟢","desc":"กรุงเทพ → สุไหงโก-ลก · 1,144 กม.",
        "stations":[
            {"name":"กรุงเทพ (หัวลำโพง)","lat":13.7401,"lon":100.5178,"province":"กรุงเทพมหานคร","km":0},
            {"name":"นครปฐม","lat":13.8199,"lon":100.0597,"province":"นครปฐม","km":56},
            {"name":"ราชบุรี","lat":13.5361,"lon":99.8163,"province":"ราชบุรี","km":117},
            {"name":"เพชรบุรี","lat":13.1093,"lon":99.9494,"province":"เพชรบุรี","km":167},
            {"name":"หัวหิน","lat":12.5675,"lon":99.9576,"province":"ประจวบคีรีขันธ์","km":229},
            {"name":"ประจวบคีรีขันธ์","lat":11.8121,"lon":99.7962,"province":"ประจวบคีรีขันธ์","km":318},
            {"name":"บางสะพานใหญ่","lat":11.2107,"lon":99.5117,"province":"ประจวบคีรีขันธ์","km":390},
            {"name":"ชุมพร","lat":10.4930,"lon":99.1800,"province":"ชุมพร","km":485},
            {"name":"หลังสวน","lat":9.9500,"lon":99.0760,"province":"ชุมพร","km":542},
            {"name":"สุราษฎร์ธานี (พุนพิน)","lat":9.1400,"lon":99.3300,"province":"สุราษฎร์ธานี","km":651},
            {"name":"ทุ่งสง","lat":8.1664,"lon":99.6818,"province":"นครศรีธรรมราช","km":767},
            {"name":"นครศรีธรรมราช","lat":8.4330,"lon":99.9630,"province":"นครศรีธรรมราช","km":832},
            {"name":"พัทลุง","lat":7.6167,"lon":100.0781,"province":"พัทลุง","km":862},
            {"name":"หาดใหญ่ (ชุมทาง)","lat":7.0080,"lon":100.4740,"province":"สงขลา","km":945},
            {"name":"ยะลา","lat":6.5410,"lon":101.2800,"province":"ยะลา","km":1055},
            {"name":"สุไหงโก-ลก","lat":6.0277,"lon":101.9784,"province":"นราธิวาส","km":1144},
        ]},
    "สายใต้ (แยกกันตัง)": {"color":"#2dd4bf","short":"SW","icon":"🟩","desc":"ทุ่งสง → กันตัง · 93 กม.",
        "stations":[
            {"name":"ทุ่งสง","lat":8.1664,"lon":99.6818,"province":"นครศรีธรรมราช","km":0},
            {"name":"ห้วยยอด","lat":7.7900,"lon":99.6350,"province":"ตรัง","km":45},
            {"name":"ตรัง","lat":7.5563,"lon":99.6114,"province":"ตรัง","km":67},
            {"name":"กันตัง","lat":7.4090,"lon":99.5160,"province":"ตรัง","km":93},
        ]},
    "สายตะวันออก": {"color":"#60a5fa","short":"E","icon":"🔵","desc":"กรุงเทพ → อรัญประเทศ · 255 กม.",
        "stations":[
            {"name":"กรุงเทพ (มักกะสัน)","lat":13.7524,"lon":100.5684,"province":"กรุงเทพมหานคร","km":0},
            {"name":"ฉะเชิงเทรา (ชุมทาง)","lat":13.6903,"lon":101.0768,"province":"ฉะเชิงเทรา","km":61},
            {"name":"ปราจีนบุรี","lat":14.0510,"lon":101.3730,"province":"ปราจีนบุรี","km":122},
            {"name":"กบินทร์บุรี","lat":13.9490,"lon":101.7180,"province":"ปราจีนบุรี","km":166},
            {"name":"สระแก้ว","lat":13.8240,"lon":102.0640,"province":"สระแก้ว","km":210},
            {"name":"อรัญประเทศ","lat":13.6942,"lon":102.5062,"province":"สระแก้ว","km":255},
        ]},
    "สายชายฝั่งทะเลตะวันออก": {"color":"#818cf8","short":"EC","icon":"🟦","desc":"ฉะเชิงเทรา → มาบตาพุด · 134 กม.",
        "stations":[
            {"name":"ฉะเชิงเทรา (ชุมทาง)","lat":13.6903,"lon":101.0768,"province":"ฉะเชิงเทรา","km":0},
            {"name":"ชลบุรี","lat":13.3639,"lon":100.9905,"province":"ชลบุรี","km":48},
            {"name":"ศรีราชา","lat":13.1740,"lon":100.9300,"province":"ชลบุรี","km":78},
            {"name":"แหลมฉบัง","lat":13.0820,"lon":100.8850,"province":"ชลบุรี","km":92},
            {"name":"พัทยา","lat":12.9236,"lon":100.8825,"province":"ชลบุรี","km":110},
            {"name":"มาบตาพุด","lat":12.6793,"lon":101.1500,"province":"ระยอง","km":134},
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

# ── USGS Earthquake feed (Thailand + neighboring region, no auth) ──
@st.cache_data(ttl=900, show_spinner=False)
def fetch_earthquakes(days=7, min_mag=2.5):
    """ดึงข้อมูลแผ่นดินไหวในไทย+ภูมิภาคใกล้เคียง จาก USGS (ไม่ต้อง token)
       ครอบคลุม: ไทย เมียนมา ลาว กัมพูชา เวียดนามตอนใต้ มาเลเซียเหนือ อันดามัน"""
    start = (NOW_TH - timedelta(days=days)).strftime("%Y-%m-%d")
    params = {
        "format":"geojson", "starttime":start,
        "minlatitude":3.0, "maxlatitude":24.0,
        "minlongitude":92.0, "maxlongitude":110.0,
        "minmagnitude":min_mag, "orderby":"time",
    }
    try:
        r = requests.get("https://earthquake.usgs.gov/fdsnws/event/1/query",
                         params=params, timeout=12)
        if r.status_code == 200:
            return r.json(), ""
        return None, f"USGS HTTP {r.status_code}"
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:50]}"

def parse_earthquakes(geojson):
    if not geojson or not isinstance(geojson, dict):
        return []
    out = []
    for feat in geojson.get("features", []):
        p = feat.get("properties", {}) or {}
        g = feat.get("geometry", {}) or {}
        coords = g.get("coordinates", [None,None,None])
        ts = p.get("time")
        when = ""
        if ts:
            try:
                when = datetime.fromtimestamp(ts/1000, tz=TZ_TH).strftime("%d/%m %H:%M")
            except Exception:
                when = ""
        out.append({
            "mag": p.get("mag"),
            "place": p.get("place","") or "",
            "time": when,
            "ts": ts or 0,
            "depth": coords[2] if len(coords)>2 else None,
            "lat": coords[1] if len(coords)>1 else None,
            "lon": coords[0] if coords else None,
        })
    out.sort(key=lambda x: x["ts"], reverse=True)
    return out

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

def assess_7day(series):
    """ประเมินความเสี่ยงล่วงหน้า 7 วันจาก series พยากรณ์รายวัน
       คืน (peak_level, peak_day_label, peak_rain, n_risk_days, advice)"""
    if not series:
        return (-1, "—", None, 0, "ไม่มีข้อมูล")
    peak = -1; peak_rain = None; peak_idx = 0; n_risk = 0
    for i, f in enumerate(series[:7]):
        r = f.get("rain")
        lv = rain_risk(r)[0]
        if lv >= 3:
            n_risk += 1
        if r is not None and (peak_rain is None or r > peak_rain):
            peak_rain = r; peak = lv; peak_idx = i
    labels = ["วันนี้","พรุ่งนี้","มะรืน","อีก 3 วัน","อีก 4 วัน","อีก 5 วัน","อีก 6 วัน"]
    peak_label = labels[peak_idx] if peak_idx < len(labels) else f"+{peak_idx}"
    if peak >= 4:   advice = "เสี่ยงสูงมาก — เตรียมแผนชะลอ/งดเดินรถ"
    elif peak >= 3: advice = "เสี่ยงสูง — เฝ้าระวังและเตรียมความพร้อม"
    elif peak >= 2: advice = "เสี่ยงปานกลาง — ติดตามสถานการณ์"
    else:           advice = "เสี่ยงต่ำ — เดินรถปกติ"
    return (peak, peak_label, peak_rain, n_risk, advice)

# ══════════════════════════════════════════════════════════════
#  PDF REPORT BUILDER  (reportlab + Thai font)
# ══════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def _register_thai_font():
    """ลงทะเบียนฟอนต์ไทย Sarabun (ดาวน์โหลดครั้งเดียว, cache).
       คืนชื่อฟอนต์ (regular, bold) ถ้าสำเร็จ ไม่งั้น Helvetica."""
    try:
        import os
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        font_dir = os.path.join(os.path.expanduser("~"), ".srt_fonts")
        os.makedirs(font_dir, exist_ok=True)
        reg = os.path.join(font_dir, "Sarabun-Regular.ttf")
        bld = os.path.join(font_dir, "Sarabun-Bold.ttf")
        urls = {
            reg: "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf",
            bld: "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf",
        }
        for path, url in urls.items():
            if not os.path.exists(path):
                r = requests.get(url, timeout=15)
                if r.status_code == 200:
                    with open(path, "wb") as f:
                        f.write(r.content)
        if os.path.exists(reg) and os.path.exists(bld):
            pdfmetrics.registerFont(TTFont("Sarabun", reg))
            pdfmetrics.registerFont(TTFont("Sarabun-Bold", bld))
            return "Sarabun", "Sarabun-Bold"
    except Exception:
        pass
    return "Helvetica", "Helvetica-Bold"


def build_executive_pdf(meta, kpis, line_stats, top_risks, day_summary, quakes):
    """สร้างรายงานสรุปผู้บริหารเป็น PDF (bytes)."""
    from io import BytesIO
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                    TableStyle, HRFlowable)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    FN, FB = _register_thai_font()
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            topMargin=16*mm, bottomMargin=16*mm,
                            leftMargin=15*mm, rightMargin=15*mm,
                            title="รายงานสรุปสภาพอากาศ")
    ss = getSampleStyleSheet()
    H1 = ParagraphStyle("H1", parent=ss["Title"], fontName=FB, fontSize=18,
                        textColor=colors.HexColor("#1a2b42"), spaceAfter=2, alignment=TA_LEFT)
    SUB = ParagraphStyle("SUB", fontName=FN, fontSize=10,
                         textColor=colors.HexColor("#5a6e88"), spaceAfter=2)
    H2 = ParagraphStyle("H2", fontName=FB, fontSize=12.5,
                        textColor=colors.HexColor("#2563eb"), spaceBefore=10, spaceAfter=6)
    BODY = ParagraphStyle("BODY", fontName=FN, fontSize=9.5,
                          textColor=colors.HexColor("#1a2b42"), leading=14)
    SMALL = ParagraphStyle("SMALL", fontName=FN, fontSize=8,
                           textColor=colors.HexColor("#90a2bb"))
    story = []

    # Header
    story.append(Paragraph("รายงานสรุปสภาพอากาศและปริมาณน้ำฝน", H1))
    story.append(Paragraph("ศูนย์ความปลอดภัย ฝ่ายการช่างโยธา · การรถไฟแห่งประเทศไทย", SUB))
    story.append(Paragraph(f"ข้อมูล ณ {meta['datetime']} · เส้นทาง: {meta['line']} · พยากรณ์: {meta['day']}", SUB))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1.4, color=colors.HexColor("#2563eb")))
    story.append(Spacer(1, 8))

    # Status verdict
    story.append(Paragraph("สถานะภาพรวม (ด้านสภาพอากาศ)", H2))
    sv = meta["verdict"]
    sv_tbl = Table([[Paragraph(f"<b>{sv['title']}</b>", ParagraphStyle("v",fontName=FB,fontSize=13,textColor=colors.white)),
                     Paragraph(sv['detail'], ParagraphStyle("vd",fontName=FN,fontSize=9.5,textColor=colors.white))]],
                   colWidths=[55*mm, 125*mm])
    sv_tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),colors.HexColor(sv["color"])),
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),10),("RIGHTPADDING",(0,0),(-1,-1),10),
        ("TOPPADDING",(0,0),(-1,-1),9),("BOTTOMPADDING",(0,0),(-1,-1),9),
        ("ROUNDEDCORNERS",[6,6,6,6]),
    ]))
    story.append(sv_tbl)
    story.append(Spacer(1, 10))

    # KPI grid (2 rows x 3)
    story.append(Paragraph("ตัวชี้วัดสำคัญ", H2))
    kc = []
    row = []
    for i, (lab, val, unit, hexc) in enumerate(kpis):
        cell = Table([[Paragraph(lab, ParagraphStyle("kl",fontName=FN,fontSize=8,textColor=colors.HexColor("#5a6e88")))],
                      [Paragraph(f"<b>{val}</b> <font size=8>{unit}</font>",
                                 ParagraphStyle("kv",fontName=FB,fontSize=16,textColor=colors.HexColor(hexc)))]],
                     colWidths=[57*mm])
        cell.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#f7fafd")),
            ("BOX",(0,0),(-1,-1),0.6,colors.HexColor("#e3eaf2")),
            ("LINEABOVE",(0,0),(-1,0),2.2,colors.HexColor(hexc)),
            ("LEFTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),6),
        ]))
        row.append(cell)
        if len(row) == 3:
            kc.append(row); row = []
    if row: kc.append(row + [""]*(3-len(row)))
    kpi_tbl = Table(kc, colWidths=[60*mm]*3, hAlign="LEFT")
    kpi_tbl.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),3),
                                 ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
                                 ("VALIGN",(0,0),(-1,-1),"TOP")]))
    story.append(kpi_tbl)
    story.append(Spacer(1, 8))

    # Per-line rainfall table
    story.append(Paragraph("ปริมาณน้ำฝนแยกตามสายทาง", H2))
    ldata = [["สายทาง","ฝนสูงสุด (มม.)","ฝนเฉลี่ย (มม.)","สถานีเสี่ยง"]]
    for ln, mx, av, heavy in line_stats:
        ldata.append([ln, f"{mx:.0f}" if mx is not None else "—",
                      f"{av:.1f}" if av is not None else "—", str(heavy)])
    lt = Table(ldata, colWidths=[70*mm, 36*mm, 36*mm, 38*mm])
    lt.setStyle(TableStyle([
        ("FONTNAME",(0,0),(-1,-1),FN),("FONTSIZE",(0,0),(-1,-1),9),
        ("FONTNAME",(0,0),(-1,0),FB),
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#2563eb")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, colors.HexColor("#f3f7fc")]),
        ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#e3eaf2")),
        ("ALIGN",(1,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5),
    ]))
    story.append(lt)
    story.append(Spacer(1, 8))

    # Top risk stations
    story.append(Paragraph("สถานีเสี่ยงสูงสุด", H2))
    if top_risks:
        tdata = [["อันดับ","สถานี","จังหวัด","สายทาง","ฝน (มม.)","ระดับ"]]
        for i,(nm,prov,line,rain,lab) in enumerate(top_risks,1):
            tdata.append([str(i), nm, prov, line, f"{rain:.0f}" if rain is not None else "—", lab])
        tt = Table(tdata, colWidths=[14*mm,46*mm,32*mm,40*mm,22*mm,26*mm])
        tt.setStyle(TableStyle([
            ("FONTNAME",(0,0),(-1,-1),FN),("FONTSIZE",(0,0),(-1,-1),8.5),
            ("FONTNAME",(0,0),(-1,0),FB),
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#dc2626")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, colors.HexColor("#fef5f5")]),
            ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#e3eaf2")),
            ("ALIGN",(0,0),(0,-1),"CENTER"),("ALIGN",(4,0),(4,-1),"CENTER"),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
        ]))
        story.append(tt)
    else:
        story.append(Paragraph("ไม่มีสถานีที่มีความเสี่ยง", BODY))
    story.append(Spacer(1, 8))

    # 7-day outlook
    story.append(Paragraph("แนวโน้มความเสี่ยง 7 วันข้างหน้า (ฝนสูงสุดรวมทั้งเครือข่าย)", H2))
    if day_summary:
        ddata = [["วัน"]+[d["label"] for d in day_summary],
                 ["ฝนสูงสุด (มม.)"]+[f"{d['max']:.0f}" if d["max"] is not None else "—" for d in day_summary],
                 ["สถานีเสี่ยง"]+[str(d["n_heavy"]) for d in day_summary]]
        dt = Table(ddata, colWidths=[34*mm]+[20.5*mm]*len(day_summary))
        cmds = [
            ("FONTNAME",(0,0),(-1,-1),FN),("FONTSIZE",(0,0),(-1,-1),8),
            ("FONTNAME",(0,0),(0,-1),FB),("FONTNAME",(0,0),(-1,0),FB),
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0ea5e9")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#e3eaf2")),
            ("ALIGN",(1,0),(-1,-1),"CENTER"),("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
        ]
        # color the max-rain cells
        for ci,d in enumerate(day_summary, start=1):
            hx = d["hex"]
            cmds.append(("BACKGROUND",(ci,1),(ci,1),colors.HexColor(hx)))
            cmds.append(("TEXTCOLOR",(ci,1),(ci,1),colors.white))
        dt.setStyle(TableStyle(cmds))
        story.append(dt)
    story.append(Spacer(1, 8))

    # Earthquakes
    if quakes:
        story.append(Paragraph("แผ่นดินไหวในภูมิภาค (7 วันล่าสุด)", H2))
        qdata = [["ขนาด (M)","ตำแหน่ง","เวลา","ลึก (กม.)"]]
        for q in quakes[:8]:
            qdata.append([f"{q['mag']:.1f}" if q["mag"] else "—", q["place"][:48],
                          q["time"], f"{q['depth']:.0f}" if q["depth"] is not None else "—"])
        qt = Table(qdata, colWidths=[24*mm, 92*mm, 34*mm, 30*mm])
        qt.setStyle(TableStyle([
            ("FONTNAME",(0,0),(-1,-1),FN),("FONTSIZE",(0,0),(-1,-1),8.5),
            ("FONTNAME",(0,0),(-1,0),FB),
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#e8820c")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, colors.HexColor("#fffaf2")]),
            ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#e3eaf2")),
            ("ALIGN",(0,0),(0,-1),"CENTER"),("ALIGN",(3,0),(3,-1),"CENTER"),
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
        ]))
        story.append(qt)
        story.append(Spacer(1, 8))

    # Footer
    story.append(Spacer(1, 6))
    story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#e3eaf2")))
    story.append(Paragraph(
        "รายงานนี้จัดทำโดยระบบอัตโนมัติ · ข้อมูลพยากรณ์จากกรมอุตุนิยมวิทยา (TMD NWP API) · "
        "แผ่นดินไหวจาก USGS · พัฒนาโดย วิศวกรกำกับการกองทางถาวร · Ver. ทดลอง", SMALL))

    doc.build(story)
    buf.seek(0)
    return buf.getvalue()


@st.cache_resource(show_spinner=False)
def _get_mpl_thai_font():
    """ดาวน์โหลด+ลงทะเบียนฟอนต์ไทยสำหรับ matplotlib (cache)."""
    try:
        import os
        from matplotlib import font_manager
        font_dir = os.path.join(os.path.expanduser("~"), ".srt_fonts")
        os.makedirs(font_dir, exist_ok=True)
        reg = os.path.join(font_dir, "Sarabun-Regular.ttf")
        bld = os.path.join(font_dir, "Sarabun-Bold.ttf")
        urls = {
            reg: "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Regular.ttf",
            bld: "https://github.com/google/fonts/raw/main/ofl/sarabun/Sarabun-Bold.ttf",
        }
        for path, url in urls.items():
            if not os.path.exists(path):
                r = requests.get(url, timeout=15)
                if r.status_code == 200:
                    with open(path, "wb") as f: f.write(r.content)
        for p in (reg, bld):
            if os.path.exists(p):
                font_manager.fontManager.addfont(p)
        return reg if os.path.exists(reg) else None
    except Exception:
        return None


def build_executive_image(meta, kpis, top_risks, severe_list, day_summary, fmt="png"):
    """สร้างภาพรายงานสรุปผู้บริหาร (PNG/JPG) ด้วย matplotlib → bytes."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch, Rectangle
    from io import BytesIO

    _get_mpl_thai_font()
    plt.rcParams["font.family"] = "Sarabun"
    plt.rcParams["axes.unicode_minus"] = False

    W, H = 11.7, 8.27  # A4 landscape inches
    fig = plt.figure(figsize=(W, H), dpi=160)
    fig.patch.set_facecolor("#f6f9fd")
    ax = fig.add_axes([0,0,1,1]); ax.axis("off")
    ax.set_xlim(0,100); ax.set_ylim(0,100)

    INK="#1a2b42"; INK2="#5a6e88"; INK3="#90a2bb"; BLUE="#2563eb"; CY="#0ea5e9"

    def box(x,y,w,h,fc,ec=None,lw=1.0,r=0.02):
        p=FancyBboxPatch((x,y),w,h,boxstyle=f"round,pad=0,rounding_size={r*100}",
                         fc=fc,ec=ec or fc,lw=lw,mutation_aspect=H/W,zorder=1)
        ax.add_patch(p); return p

    # Header band
    box(3,89,94,8.5,"#ffffff",ec="#d3deeb",lw=1.2,r=0.012)
    ax.add_patch(Rectangle((3,89),1.1,8.5,fc=BLUE,zorder=2))
    ax.text(5.5,94.6,"รายงานสรุปสภาพอากาศและปริมาณน้ำฝน",fontsize=20,fontweight="bold",color=INK,va="center")
    ax.text(5.5,91.3,"ศูนย์ความปลอดภัย ฝ่ายการช่างโยธา · การรถไฟแห่งประเทศไทย",fontsize=11,color=INK2,va="center")
    ax.text(94.5,94.6,meta["datetime"],fontsize=10,color=INK2,va="center",ha="right")
    ax.text(94.5,91.3,f"เส้นทาง: {meta['line']}  ·  พยากรณ์: {meta['day']}",fontsize=9.5,color=INK3,va="center",ha="right")

    # Status verdict bar
    sv=meta["verdict"]
    box(3,81,94,6.2,sv["color"],r=0.012)
    ax.text(5.5,84.1,sv["title"],fontsize=15,fontweight="bold",color="white",va="center")
    ax.text(40,84.1,sv["detail"],fontsize=10.5,color="white",va="center")

    # KPI tiles (6)
    kx, kw, kgap = 3, 14.7, 1.16
    ky, kh = 70.5, 8.6
    for i,(lab,val,unit,hexc) in enumerate(kpis):
        x = kx + i*(kw+kgap)
        box(x,ky,kw,kh,"#ffffff",ec="#e3eaf2",lw=1.0,r=0.02)
        ax.add_patch(Rectangle((x,ky+kh-0.5),kw,0.5,fc=hexc,zorder=2))
        ax.text(x+kw/2,ky+kh-2.2,lab,fontsize=8,color=INK2,ha="center",va="center")
        ax.text(x+kw/2,ky+kh-5.0,f"{val}",fontsize=20,fontweight="bold",color=hexc,ha="center",va="center")
        ax.text(x+kw/2,ky+1.4,unit,fontsize=8,color=INK3,ha="center",va="center")

    # Left: Top risk stations
    box(3,30,46,37,"#ffffff",ec="#e3eaf2",lw=1.0,r=0.012)
    ax.text(5.5,64.3,"🚨 สถานีเสี่ยงสูงสุด",fontsize=12.5,fontweight="bold",color=BLUE,va="center")
    ax.plot([5.5,46.5],[62.5,62.5],color="#e3eaf2",lw=1)
    if top_risks:
        for i,(nm,prov,line,rain,lab,hx) in enumerate(top_risks[:7]):
            yy=59.5-i*4.0
            ax.text(5.5,yy,f"{i+1}",fontsize=11,fontweight="bold",color=INK3,va="center")
            ax.text(8.5,yy+0.6,nm[:26],fontsize=9.5,fontweight="bold",color=INK,va="center")
            ax.text(8.5,yy-1.4,f"{prov} · {line}",fontsize=7.5,color=INK3,va="center")
            ax.text(46,yy,f"{rain:.0f} มม." if rain is not None else "—",fontsize=11,fontweight="bold",color=hx,va="center",ha="right")
    else:
        ax.text(25,48,"ไม่มีข้อมูลปริมาณฝน",fontsize=10,color=INK3,ha="center")

    # Right: Severe weather alerts
    box(51,30,46,37,"#ffffff",ec="#e3eaf2",lw=1.0,r=0.012)
    ax.text(53.5,64.3,"⚠️ การเตือนภัยสภาพอากาศร้าย",fontsize=12.5,fontweight="bold",color="#dc2626",va="center")
    ax.plot([53.5,94.5],[62.5,62.5],color="#e3eaf2",lw=1)
    if severe_list:
        for i,(nm,prov,txt,hx) in enumerate(severe_list[:7]):
            yy=59.5-i*4.0
            ax.add_patch(Rectangle((53.5,yy-1.1),1.0,2.6,fc=hx,zorder=2))
            ax.text(55.5,yy+0.6,nm[:24],fontsize=9.5,fontweight="bold",color=INK,va="center")
            ax.text(55.5,yy-1.4,f"{prov}",fontsize=7.5,color=INK3,va="center")
            ax.text(94,yy,txt,fontsize=8.5,fontweight="bold",color=hx,va="center",ha="right")
    else:
        ax.text(74,48,"✅ ไม่มีการเตือนภัยสภาพอากาศร้าย",fontsize=10.5,color="#059669",ha="center",fontweight="bold")

    # Bottom: 7-day outlook strip
    box(3,8,94,19,"#ffffff",ec="#e3eaf2",lw=1.0,r=0.012)
    ax.text(5.5,24.3,"📈 แนวโน้มความเสี่ยงฝน 7 วันข้างหน้า (ฝนสูงสุดรวมทั้งเครือข่าย)",fontsize=12,fontweight="bold",color=BLUE,va="center")
    if day_summary:
        n=len(day_summary); cw=88/n; cx0=5.5
        maxv=max([(d["max"] or 0) for d in day_summary]+[10])
        for i,d in enumerate(day_summary):
            cx=cx0+i*cw
            v=d["max"] or 0
            bh=(v/maxv)*9 if maxv else 0
            ax.add_patch(Rectangle((cx+cw*0.2,10.5),cw*0.6,bh,fc=d["hex"],zorder=2))
            ax.text(cx+cw/2,10.5+bh+0.9,f"{v:.0f}",fontsize=8.5,fontweight="bold",color=d["hex"],ha="center",va="bottom")
            ax.text(cx+cw/2,9.0,d["label"],fontsize=8,color=INK2,ha="center",va="center")

    # Footer
    ax.text(3,4.5,"ข้อมูลพยากรณ์: กรมอุตุนิยมวิทยา (TMD NWP API)  ·  พัฒนาโดย วิศวกรกำกับการกองทางถาวร  ·  Ver. ทดลอง",
            fontsize=7.5,color=INK3,va="center")

    buf=BytesIO()
    save_fmt = "jpeg" if fmt.lower() in ("jpg","jpeg") else "png"
    fig.savefig(buf,format=save_fmt,dpi=160,facecolor=fig.get_facecolor(),bbox_inches=None)
    plt.close(fig); buf.seek(0)
    return buf.getvalue()


    st.markdown("""
    <div style='text-align:center;padding:10px 0 16px;'>
        <div style='font-size:2.6rem;'>🚆</div>
        <div style='font-family:Kanit;color:#1a2b42;font-size:1.0rem;font-weight:700;line-height:1.3;'>ศูนย์ความปลอดภัย</div>
        <div style='color:#5a6e88;font-size:0.78rem;'>ฝ่ายการช่างโยธา</div>
        <div style='color:#90a2bb;font-size:0.7rem;letter-spacing:0.5px;margin-top:2px;'>การรถไฟแห่งประเทศไทย</div>
    </div>""", unsafe_allow_html=True)

    # Token — เชื่อมต่ออัตโนมัติ ไม่แสดงปุ่มแก้ไข
    if _token():
        jd = _jwt(); exp = jd.get("exp",0)
        exp_dt = datetime.fromtimestamp(exp, tz=TZ_TH) if exp else None
        days = (exp_dt - NOW_TH).days if exp_dt else 0
        col = "#059669" if days>30 else "#e8820c" if days>0 else "#dc2626"
        st.markdown(f"""
        <div style='background:linear-gradient(135deg,#eef6ff,#f3f7fc);border:1px solid #d3deeb;border-radius:12px;padding:11px 15px;margin-bottom:8px;box-shadow:0 2px 8px rgba(30,58,95,0.05);'>
            <div style='display:flex;align-items:center;justify-content:space-between;'>
                <div style='color:#90a2bb;font-size:0.7rem;font-weight:600;'>🔑 TMD NWP API</div>
                <div style='width:8px;height:8px;border-radius:50%;background:{col};box-shadow:0 0 8px {col}99;'></div>
            </div>
            <div style='color:#2563eb;font-size:0.82rem;font-weight:700;margin-top:2px;'>เชื่อมต่ออัตโนมัติ <b style='color:#1a2b42;'>· uid {_uid()}</b></div>
            <div style='color:{col};font-size:0.72rem;margin-top:2px;font-weight:600;'>{"✓ พร้อมใช้งาน · เหลือ "+str(days)+" วัน" if days>0 else "Token หมดอายุ"}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#e3eaf2;margin:14px 0;'>", unsafe_allow_html=True)

    st.markdown("<div style='color:#2563eb;font-size:0.74rem;font-weight:700;letter-spacing:0.6px;margin-bottom:5px;'>🛤️ เส้นทาง</div>", unsafe_allow_html=True)
    sel_line = st.selectbox("line", ["ทุกสาย"]+list(SRT_LINES.keys()), label_visibility="collapsed")

    st.markdown("<div style='color:#2563eb;font-size:0.74rem;font-weight:700;letter-spacing:0.6px;margin:12px 0 5px;'>📅 วันพยากรณ์</div>", unsafe_allow_html=True)
    day_mode = st.radio("เลือกแบบ", ["ด่วน","ปฏิทิน"], horizontal=True, label_visibility="collapsed")
    HORIZONS = ["วันนี้","พรุ่งนี้","มะรืน","+3 วัน","+4 วัน","+5 วัน","+6 วัน"]
    if day_mode == "ด่วน":
        sel_day = st.selectbox("day", HORIZONS, label_visibility="collapsed")
        day_idx = HORIZONS.index(sel_day)
    else:
        _min = NOW_TH.date()
        _max = (NOW_TH + timedelta(days=6)).date()
        picked = st.date_input("เลือกวันที่", value=_min, min_value=_min, max_value=_max,
                               format="DD/MM/YYYY", label_visibility="collapsed")
        day_idx = max(0, min(6, (picked - _min).days))
        sel_day = f"{picked.day} {TH_MONTHS[picked.month]} {picked.year+543}"

    # Real-time — เปิดตลอดเวลา (อัพเดตทุก 5 นาที อัตโนมัติ)
    refresh_sec = 300
    st.markdown("""
    <div style='background:linear-gradient(135deg,#ecfdf5,#f0fdf4);border:1px solid #86efac;border-radius:12px;padding:10px 14px;margin:14px 0 4px;'>
        <div style='display:flex;align-items:center;gap:8px;'>
            <span style='width:9px;height:9px;border-radius:50%;background:#10b981;box-shadow:0 0 8px #10b981;animation:livepulse 2s infinite;'></span>
            <span style='color:#059669;font-weight:700;font-size:0.82rem;'>REAL-TIME · ทำงานตลอดเวลา</span>
        </div>
        <div style='color:#5a6e88;font-size:0.72rem;margin-top:3px;'>อัพเดตข้อมูลอัตโนมัติทุก 5 นาที</div>
    </div>""", unsafe_allow_html=True)

    if st.button("🔄 รีเฟรชเดี๋ยวนี้", use_container_width=True):
        st.cache_data.clear(); st.rerun()

    st.markdown(f"""
    <div style='color:#90a2bb;font-size:0.74rem;margin-top:12px;line-height:1.7;'>
        🕐 ดึงข้อมูลล่าสุด<br>
        <span style='color:#2563eb;font-weight:700;font-size:0.84rem;'>{th_datetime(NOW_TH)}</span>
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#e3eaf2;margin:14px 0;'>", unsafe_allow_html=True)
    for ln, ld in SRT_LINES.items():
        st.markdown(f"<div style='display:flex;align-items:center;gap:8px;margin:3px 0;'><div style='width:24px;height:3px;background:{ld['color']};border-radius:2px;'></div><span style='color:#90a2bb;font-size:0.72rem;'>{ld['short']} · {ln}</span></div>", unsafe_allow_html=True)

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

# Earthquake data (independent of TMD token)
eq_data, eq_err = fetch_earthquakes(days=7, min_mag=2.5)
earthquakes = parse_earthquakes(eq_data)
eq_felt = [e for e in earthquakes if (e["mag"] or 0) >= 4.5]
eq_max = max((e["mag"] or 0) for e in earthquakes) if earthquakes else None

# ══════════════════════════════════════════════════════════════
#  HEADER
# ══════════════════════════════════════════════════════════════
_live = ('<span class="cmd-live"><span class="pulse"></span>LIVE · REAL-TIME</span>'
         if api_ok else '<span class="cmd-live" style="background:rgba(239,68,68,0.15);border-color:rgba(239,68,68,0.4);color:#f87171;">● OFFLINE</span>')
st.markdown(f"""
<div class='cmd-header'>
    <div style='position:absolute;right:-40px;top:-40px;width:180px;height:180px;border-radius:50%;
        background:radial-gradient(circle,rgba(14,165,233,0.18),transparent 70%);pointer-events:none;animation:floaty 6s ease-in-out infinite;'></div>
    <div style='position:absolute;right:90px;bottom:-50px;width:130px;height:130px;border-radius:50%;
        background:radial-gradient(circle,rgba(37,99,235,0.14),transparent 70%);pointer-events:none;animation:floaty 7.5s ease-in-out infinite reverse;'></div>
    <div style='display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;position:relative;z-index:2;'>
        <div>
            <h1 class='cmd-title'>🚆 ปริมาณน้ำฝนและสภาพอากาศ</h1>
            <div class='cmd-sub'>ศูนย์ความปลอดภัย ฝ่ายการช่างโยธา · การรถไฟแห่งประเทศไทย</div>
            <div style='color:#90a2bb;font-size:0.74rem;margin-top:3px;'>
                <span style='background:rgba(212,175,55,0.12);border:1px solid rgba(212,175,55,0.35);
                color:#c79a2e;padding:2px 9px;border-radius:8px;font-weight:600;'>Ver. ทดลอง</span>
                <span style='margin-left:8px;'>พัฒนาโดย วิศวกรกำกับการกองทางถาวร</span>
            </div>
        </div>
        <div style='text-align:right;'>
            {_live}
            <div style='color:#5a6e88;font-size:0.78rem;margin-top:6px;'>📅 {th_datetime(NOW_TH)}</div>
            <div style='color:#90a2bb;font-size:0.74rem;'>พยากรณ์: <b style='color:#2563eb;'>{sel_day}</b> · {sel_line}</div>
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

# Earthquake alert (if significant quake in region)
if eq_felt:
    _big = max(eq_felt, key=lambda e: e["mag"] or 0)
    st.markdown(f"""
    <div class='alert-banner ab-warn' style='margin-top:-6px;'>
        <div class='ab-icon'>🌋</div>
        <div class='ab-text'><h3>ตรวจพบแผ่นดินไหว M{_big['mag']:.1f} ในภูมิภาค</h3>
        <p>{_big['place']} · {_big['time']} · ลึก {_big['depth']:.0f} กม. — มี {len(eq_felt)} เหตุการณ์ M≥4.5 ใน 7 วัน · ดูรายละเอียดที่แท็บ 🌋 แผ่นดินไหว</p></div>
    </div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  KPI ROW
# ══════════════════════════════════════════════════════════════
_kpi_seq = [0]
def kpi(col, ico, tag, val, unit, lab, foot, cls):
    _kpi_seq[0] += 1
    uid = f"kpi{_kpi_seq[0]}"
    # detect numeric for count-up
    is_num = False
    try:
        fval = float(str(val).replace(",",""))
        is_num = str(val) not in ("—","")
    except Exception:
        fval = 0.0
    decimals = 1 if ("." in str(val)) else 0
    valspan = f"<span id='{uid}'>{val}</span>" if is_num else f"{val}"
    col.markdown(f"""
    <div class='kpi {cls}'>
        <div class='kpi-top'><span class='kpi-ico' style='animation:floaty 3.2s ease-in-out infinite;'>{ico}</span><span class='kpi-tag'>{tag}</span></div>
        <div class='kpi-val'>{valspan}<small>{unit}</small></div>
        <div class='kpi-lab'>{lab}</div>
        <div class='kpi-foot'>{foot}</div>
    </div>
    {f'''<script>(function(){{var el=document.getElementById("{uid}");if(!el)return;var t={fval},d={decimals},dur=900,s=performance.now();
    function tick(n){{var p=Math.min((n-s)/dur,1);var e=1-Math.pow(1-p,3);el.textContent=(t*e).toFixed(d);if(p<1)requestAnimationFrame(tick);}}
    requestAnimationFrame(tick);}})();</script>''' if is_num else ''}
    """, unsafe_allow_html=True)

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
tab_dash, tab_rain, tab_7day, tab_map, tab_lines, tab_quake, tab_detail = st.tabs([
    "📊 ภาพรวมผู้บริหาร", "🌧️ ปริมาณน้ำฝน", "📈 เสี่ยง 7 วัน", "🗺️ แผนที่",
    "🛤️ รายสาย", "🌋 แผ่นดินไหว", "🔍 เจาะลึกสถานี"])

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
                    <span style='color:#5a6e88;font-size:0.84rem;'>{lab}</span>
                    <span style='color:#1a2b42;font-weight:700;font-family:Kanit;'>{cnt} <span style='color:#90a2bb;font-size:0.78rem;'>({pct:.0f}%)</span></span>
                </div>
                <div style='background:#eef3f9;border-radius:8px;height:12px;overflow:hidden;'>
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
        <div style='margin-top:14px;background:#f3f7fc;border:1px solid {ov_c};border-radius:12px;padding:14px 18px;'>
            <div style='display:flex;justify-content:space-between;align-items:center;'>
                <div><div style='color:#90a2bb;font-size:0.72rem;text-transform:uppercase;letter-spacing:0.6px;'>สถานะการเดินรถ (ด้านสภาพอากาศ)</div>
                <div style='font-family:Kanit;color:{ov_c};font-size:1.4rem;font-weight:700;'>{ov_t}</div></div>
            </div>
            <div style='color:#5a6e88;font-size:0.84rem;margin-top:4px;'>💡 {ov_d}</div>
        </div></div>""", unsafe_allow_html=True)

    # — Top risk stations —
    with c2:
        st.markdown("<div class='panel'><div class='panel-h'>🚨 สถานีเสี่ยงสูงสุด</div>", unsafe_allow_html=True)
        top = sorted([s for s in station_data if s["rain"] is not None],
                     key=lambda x:x["rain"], reverse=True)[:6]
        if not top:
            st.markdown("<p style='color:#90a2bb;font-size:0.84rem;'>ยังไม่มีข้อมูลปริมาณฝน</p>", unsafe_allow_html=True)
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
                        <div class='risk-num' style='color:{hx};'>{s['rain']:.0f}<span style='font-size:0.7rem;color:#90a2bb;'> มม.</span></div>
                        <span class='bdg {bc}'>{lab}</span>
                    </div>
                </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # — สรุปข้อมูลการเตือนภัยสภาพอากาศร้าย —
    st.markdown("<div class='panel'><div class='panel-h'>⚠️ สรุปการเตือนภัยสภาพอากาศร้าย</div>", unsafe_allow_html=True)
    # รวบรวมสถานีที่เข้าเกณฑ์เตือนภัย (ฝนหนัก/หนักมาก + ลมแรง)
    severe = []
    for s in station_data:
        r = s.get("rain"); w = s.get("ws")
        reasons = []
        if r is not None and r >= 90: reasons.append(("ฝนหนักมาก", f"{r:.0f} มม.", "#dc2626"))
        elif r is not None and r >= 35: reasons.append(("ฝนหนัก", f"{r:.0f} มม.", "#e8820c"))
        if w is not None and w >= 10: reasons.append(("ลมกระโชกแรง", f"{w:.0f} m/s", "#7c3aed"))
        if reasons:
            severe.append((s, reasons))
    severe.sort(key=lambda x: x[0].get("rain") or 0, reverse=True)

    sv_cols = st.columns(4)
    n_storm = sum(1 for s in station_data if (s.get("cond") in (7,8)))
    n_wind  = sum(1 for s in station_data if (s.get("ws") or 0) >= 10)
    sv_metrics = [
        ("🌊","ฝนหนักมาก", n_crit, "#dc2626", "เกิน 90 มม./วัน"),
        ("⛈️","พายุฝนฟ้าคะนอง", n_storm, "#e8820c", "สภาพอากาศรหัส 7-8"),
        ("💨","ลมแรง", n_wind, "#7c3aed", "เกิน 10 m/s"),
        ("📍","จุดเตือนภัยรวม", len(severe), "#2563eb", "สถานีเข้าเกณฑ์"),
    ]
    for col,(ic,lab,val,hx,sub) in zip(sv_cols, sv_metrics):
        col.markdown(f"""
        <div style='background:#f7fafd;border:1px solid #e3eaf2;border-left:3px solid {hx};border-radius:10px;padding:11px 14px;'>
            <div style='font-size:1.3rem;'>{ic}</div>
            <div style='font-family:Kanit;font-size:1.5rem;font-weight:700;color:{hx};line-height:1;margin:3px 0;'>{val}</div>
            <div style='color:#5a6e88;font-size:0.76rem;font-weight:600;'>{lab}</div>
            <div style='color:#90a2bb;font-size:0.68rem;'>{sub}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    if severe:
        for s, reasons in severe[:6]:
            tags = " ".join(f"<span style='background:{c}1a;color:{c};border:1px solid {c}55;padding:2px 9px;border-radius:20px;font-size:0.72rem;font-weight:700;margin-right:4px;'>{lab} {val}</span>" for lab,val,c in reasons)
            st.markdown(f"""
            <div style='display:flex;align-items:center;justify-content:space-between;gap:10px;background:#fff;border:1px solid #e3eaf2;border-radius:10px;padding:10px 14px;margin:4px 0;'>
                <div>
                    <span style='color:#1a2b42;font-weight:700;font-size:0.88rem;'>{s['line_icon']} {s['name']}</span>
                    <span style='color:#90a2bb;font-size:0.74rem;'> · {s['province']} · {s['line']}</span>
                </div>
                <div style='text-align:right;white-space:nowrap;'>{tags}</div>
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background:#f0fdf4;border:1px solid #86efac;border-radius:10px;padding:14px 18px;text-align:center;'>
            <span style='font-size:1.5rem;'>✅</span>
            <span style='color:#059669;font-weight:700;font-size:0.95rem;margin-left:8px;'>ไม่มีการเตือนภัยสภาพอากาศร้ายในเส้นทาง</span>
        </div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    # — แหล่งแจ้งเตือนภัยพิบัติที่เกี่ยวข้อง —
    st.markdown("<div class='panel'><div class='panel-h'>📡 ศูนย์แจ้งเตือนภัยพิบัติ & เรดาร์ตรวจอากาศ</div>", unsafe_allow_html=True)
    st.markdown("<div style='color:#90a2bb;font-size:0.76rem;margin-bottom:10px;'>แหล่งข้อมูลแจ้งเตือนภัยและติดตามกลุ่มเมฆฝนแบบ real-time สำหรับเจ้าหน้าที่</div>", unsafe_allow_html=True)
    alert_sources = [
        ("🚨","Thai Disaster Alert (THDA)","แจ้งเตือนภัยพิบัติแห่งชาติ ปภ.","https://thda.disaster.go.th","#dc2626"),
        ("🛡️","พ้นภัย (PhonPhai)","แอปแจ้งเตือนภัยพิบัติ สสน.","https://www.phonphai.in.th","#e8820c"),
        ("🌤️","Thai Weather","พยากรณ์อากาศ กรมอุตุนิยมวิทยา","https://www.tmd.go.th","#2563eb"),
        ("📻","Zello Walkie Talkie","วิทยุสื่อสารฉุกเฉินกลุ่มกู้ภัย","https://zello.com","#059669"),
        ("📡","เรดาร์ฝน กรมอุตุนิยมวิทยา","กลุ่มเมฆฝนเรดาร์ real-time","https://weather.tmd.go.th/radar.php","#0ea5e9"),
        ("🌧️","เรดาร์ฝนหลวง","ภาพเรดาร์ กรมฝนหลวงฯ","https://www.royalrain.go.th","#7c3aed"),
        ("🏙️","ศูนย์ควบคุมน้ำ กทม.","เรดาร์ฝน-น้ำท่วม กรุงเทพมหานคร","https://weather.bangkok.go.th","#c2410c"),
    ]
    asc = st.columns(4)
    for i,(ic,name,desc,url,hx) in enumerate(alert_sources):
        with asc[i % 4]:
            st.markdown(f"""
            <a href='{url}' target='_blank' style='text-decoration:none;'>
            <div style='background:#fff;border:1px solid #e3eaf2;border-top:3px solid {hx};border-radius:12px;padding:13px 14px;margin:4px 0;min-height:118px;transition:all .15s;box-shadow:0 1px 4px rgba(30,58,95,0.05);'
                onmouseover="this.style.boxShadow='0 6px 18px rgba(30,58,95,0.13)';this.style.transform='translateY(-3px)'"
                onmouseout="this.style.boxShadow='0 1px 4px rgba(30,58,95,0.05)';this.style.transform='translateY(0)'">
                <div style='font-size:1.6rem;'>{ic}</div>
                <div style='color:#1a2b42;font-weight:700;font-size:0.84rem;margin-top:5px;line-height:1.25;'>{name}</div>
                <div style='color:#90a2bb;font-size:0.72rem;margin-top:3px;line-height:1.3;'>{desc}</div>
                <div style='color:{hx};font-size:0.7rem;font-weight:700;margin-top:6px;'>เปิดดู →</div>
            </div></a>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

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
                <div style='background:#f7fafd;border:1px solid #e3eaf2;border-radius:10px;padding:10px 14px;margin:5px 0;'>
                    <div style='display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;'>
                        <span style='color:#1a2b42;font-size:0.86rem;font-weight:600;'>{em} {s['name']}</span>
                        <span style='font-family:Kanit;font-weight:700;color:{hx};font-size:1rem;'>{rain_disp}<span style='font-size:0.7rem;color:#90a2bb;'> มม.</span></span>
                    </div>
                    <div style='background:#eef3f9;border-radius:6px;height:8px;overflow:hidden;'>
                        <div style='width:{w:.1f}%;height:100%;background:{hx};border-radius:6px;'></div>
                    </div>
                    <div style='display:flex;justify-content:space-between;margin-top:5px;'>
                        <span style='color:#90a2bb;font-size:0.72rem;'>{s['line_short']} · {s['province']}</span>
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
        <div style='display:grid;grid-template-columns:40px 150px 130px 1fr;align-items:center;gap:12px;padding:8px 0;border-bottom:1px solid #e3eaf2;'>
            <span style='font-size:1.3rem;'>{em}</span>
            <span style='color:{hx};font-weight:700;font-size:0.86rem;'>{lab}</span>
            <span style='color:#5a6e88;font-size:0.82rem;'>{rng}</span>
            <span style='color:#5a6e88;font-size:0.82rem;'>💡 {act}</span>
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
        folium.TileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
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
# ║  TAB: 7-DAY RISK ASSESSMENT                               ║
# ╚═══════════════════════════════════════════════════════════╝
with tab_7day:
    st.markdown("<div class='sec-label'>ประเมินความเสี่ยงฝนตกหนักและสภาพอากาศล่วงหน้า 7 วัน</div>", unsafe_allow_html=True)
    if not api_ok:
        st.info("ℹ️ ต้องเชื่อมต่อ TMD API ก่อน")
    else:
        # Network-wide 7-day heat strip: each station × 7 days
        labels7 = ["วันนี้","พรุ่งฯ","มะรืน","+3","+4","+5","+6"]
        # summarise per-day across all stations
        day_summary = []
        for di in range(7):
            day_rains = []
            for s in station_data:
                ser = s.get("series", [])
                if di < len(ser) and ser[di].get("rain") is not None:
                    day_rains.append(ser[di]["rain"])
            if day_rains:
                day_summary.append({
                    "idx":di, "max":max(day_rains), "avg":sum(day_rains)/len(day_rains),
                    "n_heavy":sum(1 for r in day_rains if r>=35),
                    "n_crit":sum(1 for r in day_rains if r>=90)})
            else:
                day_summary.append({"idx":di,"max":None,"avg":None,"n_heavy":0,"n_crit":0})

        # 7-day outlook cards
        st.markdown("<div class='panel'><div class='panel-h'>📅 แนวโน้มความเสี่ยงรวมทั้งเครือข่าย 7 วัน</div>", unsafe_allow_html=True)
        dcols = st.columns(7)
        for di, ds in enumerate(day_summary):
            lv,lab,em,hx,bc = rain_risk(ds["max"])
            d = NOW_TH + timedelta(days=di)
            mxd = f"{ds['max']:.0f}" if ds["max"] is not None else "—"
            with dcols[di]:
                st.markdown(f"""
                <div style='background:#f7fafd;border:1px solid #e3eaf2;border-top:3px solid {hx};
                    border-radius:12px;padding:12px 6px;text-align:center;'>
                    <div style='color:#90a2bb;font-size:0.68rem;'>{labels7[di]}</div>
                    <div style='color:#5a6e88;font-size:0.66rem;'>{d.day} {TH_MONTHS[d.month]}</div>
                    <div style='font-size:1.7rem;margin:5px 0;'>{em}</div>
                    <div style='font-family:Kanit;color:{hx};font-weight:700;font-size:1.15rem;'>{mxd}</div>
                    <div style='color:#90a2bb;font-size:0.64rem;'>มม.สูงสุด</div>
                    <div style='margin-top:5px;font-size:0.66rem;color:{"#ef4444" if ds["n_heavy"] else "#5f8199"};'>
                        {("⚠️ "+str(ds["n_heavy"])+" สถานี") if ds["n_heavy"] else "ปกติ"}
                    </div>
                </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

        # Per-station 7-day risk matrix (heat strip)
        st.markdown("<div class='panel'><div class='panel-h'>🌡️ ตารางความเสี่ยงรายสถานี × 7 วัน (ปริมาณฝน มม.)</div>", unsafe_allow_html=True)
        # header
        hdr = "<div style='display:grid;grid-template-columns:170px repeat(7,1fr);gap:4px;margin-bottom:6px;'>"
        hdr += "<div style='color:#90a2bb;font-size:0.72rem;'>สถานี \\ วัน</div>"
        for di in range(7):
            d = NOW_TH + timedelta(days=di)
            hdr += f"<div style='text-align:center;color:#90a2bb;font-size:0.68rem;'>{labels7[di]}<br>{d.day}/{d.month}</div>"
        hdr += "</div>"
        st.markdown(hdr, unsafe_allow_html=True)
        # rows — only stations that have a risk day, else show top 15 by peak
        ranked_stn = sorted(station_data,
            key=lambda s: max([f.get("rain") or 0 for f in s.get("series",[])[:7]] or [0]), reverse=True)
        for s in ranked_stn[:18]:
            ser = s.get("series", [])
            row = f"<div style='display:grid;grid-template-columns:170px repeat(7,1fr);gap:4px;margin:2px 0;align-items:center;'>"
            row += f"<div style='color:#1a2b42;font-size:0.76rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{s['line_icon']} {s['name']}</div>"
            for di in range(7):
                if di < len(ser) and ser[di].get("rain") is not None:
                    r = ser[di]["rain"]; hx = rain_hex(r)
                    txt = f"{r:.0f}"
                    row += f"<div style='background:{hx};color:#ffffff;text-align:center;border-radius:5px;padding:5px 0;font-size:0.72rem;font-weight:700;'>{txt}</div>"
                else:
                    row += "<div style='background:#eef3f9;text-align:center;border-radius:5px;padding:5px 0;color:#90a2bb;font-size:0.72rem;'>—</div>"
            row += "</div>"
            st.markdown(row, unsafe_allow_html=True)
        st.markdown("<div style='color:#90a2bb;font-size:0.72rem;margin-top:8px;'>🟢 0-10 · 🔵 10-35 · 🟠 35-90 · 🔴 >90 มม./วัน · แสดง 18 สถานีเสี่ยงสูงสุด</div></div>", unsafe_allow_html=True)

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
# ║  TAB: EARTHQUAKE                                          ║
# ╚═══════════════════════════════════════════════════════════╝
with tab_quake:
    st.markdown("<div class='sec-label'>รายงานแผ่นดินไหว — ประเทศไทยและภูมิภาคใกล้เคียง (7 วันล่าสุด)</div>", unsafe_allow_html=True)

    # KPI row for earthquakes
    qk = st.columns(4)
    qk[0].markdown(f"""<div class='kpi c-warn'><div class='kpi-top'><span class='kpi-ico'>🌋</span><span class='kpi-tag'>7 วัน</span></div>
        <div class='kpi-val'>{len(earthquakes)}</div><div class='kpi-lab'>เหตุการณ์ทั้งหมด</div>
        <div class='kpi-foot'>M ≥ 2.5 ในภูมิภาค</div></div>""", unsafe_allow_html=True)
    qk[1].markdown(f"""<div class='kpi c-crit'><div class='kpi-top'><span class='kpi-ico'>📊</span><span class='kpi-tag'>สูงสุด</span></div>
        <div class='kpi-val'>{f"{eq_max:.1f}" if eq_max else "—"}</div><div class='kpi-lab'>ขนาดใหญ่สุด (M)</div>
        <div class='kpi-foot'>มาตราริกเตอร์</div></div>""", unsafe_allow_html=True)
    qk[2].markdown(f"""<div class='kpi c-info'><div class='kpi-top'><span class='kpi-ico'>📢</span><span class='kpi-tag'>รู้สึกได้</span></div>
        <div class='kpi-val'>{len(eq_felt)}</div><div class='kpi-lab'>M ≥ 4.5</div>
        <div class='kpi-foot'>อาจรู้สึกสั่นไหว</div></div>""", unsafe_allow_html=True)
    qk[3].markdown(f"""<div class='kpi c-ok'><div class='kpi-top'><span class='kpi-ico'>🛰️</span><span class='kpi-tag'>แหล่งข้อมูล</span></div>
        <div class='kpi-val' style='font-size:1.3rem;'>USGS</div><div class='kpi-lab'>+ กรมอุตุฯ</div>
        <div class='kpi-foot'>{"●เชื่อมต่อ" if earthquakes else "○ "+str(eq_err)[:20]}</div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    cmap, clist = st.columns([1.1, 1])

    # Earthquake map
    with cmap:
        st.markdown("<div class='panel'><div class='panel-h'>🗺️ ตำแหน่งจุดศูนย์กลาง</div>", unsafe_allow_html=True)
        try:
            import folium
            from streamlit_folium import st_folium
            qm = folium.Map(location=[15.0,101.0], zoom_start=5, tiles=None)
            folium.TileLayer("https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
                             attr="© CARTO", max_zoom=19).add_to(qm)
            # draw rail lines faint for context
            for ln, ld in SRT_LINES.items():
                coords=[[s["lat"],s["lon"]] for s in ld["stations"]]
                folium.PolyLine(coords, color="#38bdf8", weight=1.5, opacity=0.35).add_to(qm)
            for e in earthquakes:
                if e["lat"] is None or e["lon"] is None: continue
                mag = e["mag"] or 0
                rad = 3 + mag*2.2
                col = "#ef4444" if mag>=5 else "#f59e0b" if mag>=4 else "#fbbf24" if mag>=3 else "#94a3b8"
                folium.CircleMarker(
                    [e["lat"],e["lon"]], radius=rad, color=col, fill=True, fill_color=col, fill_opacity=0.55,
                    popup=folium.Popup(f"<b>M {mag}</b><br>{e['place']}<br>{e['time']}<br>ลึก {e['depth']} กม.", max_width=240),
                    tooltip=f"M{mag} · {e['time']}").add_to(qm)
            st_folium(qm, width="100%", height=460, returned_objects=[])
        except ImportError:
            qdf = pd.DataFrame([{"lat":e["lat"],"lon":e["lon"]} for e in earthquakes if e["lat"]])
            if not qdf.empty: st.map(qdf, latitude="lat", longitude="lon")
        st.markdown("</div>", unsafe_allow_html=True)

    # Earthquake list
    with clist:
        st.markdown("<div class='panel'><div class='panel-h'>📋 เหตุการณ์ล่าสุด</div>", unsafe_allow_html=True)
        if not earthquakes:
            st.markdown(f"<p style='color:#90a2bb;font-size:0.84rem;'>ไม่พบเหตุการณ์ หรือเชื่อมต่อ USGS ไม่ได้ ({eq_err})</p>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='max-height:430px;overflow-y:auto;'>", unsafe_allow_html=True)
            for e in earthquakes[:25]:
                mag = e["mag"] or 0
                col = "#ef4444" if mag>=5 else "#f59e0b" if mag>=4 else "#fbbf24" if mag>=3 else "#94a3b8"
                st.markdown(f"""
                <div style='display:flex;align-items:center;gap:12px;padding:8px 0;border-bottom:1px solid #e3eaf2;'>
                    <div style='min-width:44px;height:44px;border-radius:10px;background:{col}22;border:1px solid {col};
                        display:flex;align-items:center;justify-content:center;flex-direction:column;'>
                        <span style='font-family:Kanit;font-weight:700;color:{col};font-size:1.05rem;line-height:1;'>{mag:.1f}</span>
                        <span style='color:{col};font-size:0.56rem;'>MAG</span>
                    </div>
                    <div style='flex:1;min-width:0;'>
                        <div style='color:#1a2b42;font-size:0.8rem;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;'>{e['place']}</div>
                        <div style='color:#90a2bb;font-size:0.72rem;'>🕐 {e['time']} · ลึก {e['depth']:.0f} กม.</div>
                    </div>
                </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.caption("ℹ️ ข้อมูลแผ่นดินไหวจาก USGS (United States Geological Survey) ครอบคลุมไทย เมียนมา ลาว กัมพูชา เวียดนามใต้ และทะเลอันดามัน · สามารถตรวจสอบเพิ่มเติมที่กรมอุตุนิยมวิทยา")

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
                        <div style='background:#f7fafd;border:1px solid #e3eaf2;border-top:3px solid {hx};
                            border-radius:10px;padding:10px 6px;text-align:center;'>
                            <div style='color:#90a2bb;font-size:0.7rem;'>{tdate}</div>
                            <div style='font-size:1.6rem;margin:4px 0;'>{cond_emoji(f['cond'])}</div>
                            <div style='font-family:Kanit;color:{hx};font-weight:700;font-size:1.1rem;'>{rain_d}</div>
                            <div style='color:#90a2bb;font-size:0.66rem;'>มม.</div>
                            <div style='color:#5a6e88;font-size:0.74rem;margin-top:3px;'>🌡️ {temp_d}</div>
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
st.markdown("<hr style='border-color:#e3eaf2;margin:20px 0 10px;'>", unsafe_allow_html=True)
st.markdown(f"""
<div style='display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px;color:#90a2bb;font-size:0.74rem;'>
    <span>🚆 ปริมาณน้ำฝนและสภาพอากาศ · ศูนย์ความปลอดภัย ฝ่ายการช่างโยธา · รฟท. · <b style='color:#c79a2e;'>Ver. ทดลอง</b></span>
    <span>ข้อมูล: <a href='https://data.tmd.go.th/nwpapi/doc/main/getting_start.html' target='_blank' style='color:#2563eb;'>TMD NWP API</a> · แผ่นดินไหว: <a href='https://earthquake.usgs.gov' target='_blank' style='color:#2563eb;'>USGS</a></span>
    <span>พัฒนาโดย วิศวกรกำกับการกองทางถาวร · อัพเดต {th_datetime(NOW_TH)}</span>
</div>""", unsafe_allow_html=True)

if refresh_sec>0:
    done=False
    try:
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=refresh_sec*1000, key="rt")
        done=True
    except Exception:
        done=False
    if not done:
        st.markdown(f"<script>setTimeout(function(){{window.location.reload();}},{refresh_sec*1000});</script>", unsafe_allow_html=True)
