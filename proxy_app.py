"""
SRT GISTDA Proxy
ใช้เมื่อตัวแอป Streamlit Cloud เรียก api-gateway.gistda.or.th แล้วเจอ HTTP 407
Deploy ไฟล์นี้บน VPS / Render / Railway / Server หน่วยงาน แล้วตั้ง Environment:
  GISTDA_KEY=<GISTDA API Key จริง>
จากนั้นนำ URL ไปใส่ใน Streamlit Secrets:
  GISTDA_PROXY_URL="https://your-proxy-domain/gistda/flood/{period}"
"""

import os
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SRT GISTDA Proxy", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GISTDA_KEY = os.environ.get("GISTDA_KEY", "").strip()


def no_proxy_session() -> requests.Session:
    """ปิด proxy จาก environment เพื่อเลี่ยงปัญหา 407"""
    s = requests.Session()
    s.trust_env = False
    return s


@app.get("/")
def root():
    return {"status": "ok", "service": "SRT GISTDA Proxy"}


@app.get("/health")
def health():
    return {"status": "ok", "has_gistda_key": bool(GISTDA_KEY)}


@app.get("/gistda/flood/{period}")
def gistda_flood(period: str, limit: int = 1000, offset: int = 0):
    if period not in ["1day", "3day", "7day"]:
        period = "3day"

    if not GISTDA_KEY:
        raise HTTPException(status_code=500, detail="Missing GISTDA_KEY environment variable")

    url = f"https://api-gateway.gistda.or.th/api/2.0/resources/features/flood/{period}"

    headers_list = [
        {"accept": "application/json", "API-Key": GISTDA_KEY},
        {"accept": "application/json", "api-key": GISTDA_KEY},
        {"accept": "application/json", "apikey": GISTDA_KEY},
        {"accept": "application/json", "x-api-key": GISTDA_KEY},
        {"accept": "application/json", "Authorization": f"Bearer {GISTDA_KEY}"},
    ]

    last_status = None
    last_text = ""

    for headers in headers_list:
        try:
            r = no_proxy_session().get(
                url,
                headers=headers,
                params={"limit": limit, "offset": offset},
                timeout=30,
            )
            last_status = r.status_code
            last_text = r.text[:300]

            if r.status_code == 200:
                return r.json()

            # ถ้าเจอสิทธิ์ไม่ผ่าน ลอง header รูปแบบอื่นต่อ
            if r.status_code in (401, 403):
                continue

            # ถ้า proxy ของ server นี้ยังบล็อก จะรายงานทันที
            if r.status_code == 407:
                raise HTTPException(status_code=502, detail="Proxy/Gateway returned HTTP 407")

        except HTTPException:
            raise
        except Exception as e:
            last_text = str(e)[:300]

    raise HTTPException(
        status_code=502,
        detail=f"GISTDA request failed: {last_status} {last_text}",
    )
