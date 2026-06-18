# 🚆 ระบบแจ้งเตือนสภาพอากาศโครงข่ายรถไฟไทย v3.0
### Thai Railway Network Weather & Disaster Alert System

[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

แอปแสดงแผนที่และแจ้งเตือนสภาพอากาศ ฝนตก และความเสี่ยงภัยพิบัติ สำหรับเส้นทาง
โครงข่ายรถไฟทั่วประเทศไทย ดึงข้อมูลจริงจาก **กรมอุตุนิยมวิทยา (TMD NWP API v1)**

---

## ✨ ฟีเจอร์

| Tab | รายละเอียด |
|---|---|
| 📊 **Executive Dashboard** | KPI 6 ช่อง · สรุปความเสี่ยง · กราฟฝนรายสาย · TOP 5 สถานีเสี่ยง · ตารางสรุป |
| 🗺️ **แผนที่** | Folium interactive map · เส้นทาง 5 สาย · marker สีตามระดับฝน |
| ⚠️ **แจ้งเตือนภัย** | สถานีเกินเกณฑ์ · เกณฑ์ฝน TMD · คำแนะนำเมื่อฝนหนัก |
| 🛤️ **รายสาย** | ตารางแยกสาย · สถิติฝนสูงสุด/เฉลี่ย/จำนวนสถานีเสี่ยง |
| 🌤️ **พยากรณ์ละเอียด** | พยากรณ์ราย ชม. (24 ชม.) + รายวัน (3 วัน) ต่อสถานี |

**คุณสมบัติเด่น:** ปรับช่วงเวลาพยากรณ์ (วันนี้/พรุ่งนี้/มะรืน) · กรองตามสาย · ปรับเกณฑ์การแจ้งเตือน · ธีมรถไฟ (รางทอง + signal colors)

---

## 🛤️ โครงข่ายรถไฟ (datagov.mot.go.th, 2026)

- **สายเหนือ** กรุงเทพ→เชียงใหม่ (13 สถานี · 751 กม.)
- **สายตะวันออกเฉียงเหนือ** กรุงเทพ→หนองคาย (8 สถานี · 624 กม.)
- **สายอีสานใต้** นครราชสีมา→อุบลราชธานี (6 สถานี · 305 กม.)
- **สายใต้** กรุงเทพ→สุไหงโก-ลก (12 สถานี · 1,144 กม.)
- **สายตะวันออก** กรุงเทพ→อรัญประเทศ (6 สถานี · 255 กม.)

---

## 🔑 TMD NWP API v1

แอปใช้ API รุ่นใหม่ของกรมอุตุฯ (Numerical Weather Prediction) ที่ใช้ **JWT Bearer token**

```
Base URL : https://data.tmd.go.th/nwpapi/v1
Auth     : Authorization: Bearer <JWT_TOKEN>
```

| Endpoint | ข้อมูล |
|---|---|
| `/forecast/location/daily/at` | พยากรณ์รายวันที่พิกัด lat/lon |
| `/forecast/location/hourly/at` | พยากรณ์ราย ชม. ที่พิกัด lat/lon |

**Parameters:** `lat`, `lon`, `fields` (tc, tc_max, tc_min, rh, rain, cond, ws, wd), `date`, `hour`, `duration`

ขอ token ได้ที่ https://data.tmd.go.th/nwpapi

---

## 🚀 รันบนเครื่อง

```bash
git clone https://github.com/<YOUR_USERNAME>/srt-weather-alert
cd srt-weather-alert

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

mkdir -p .streamlit
cp secrets.toml.example .streamlit/secrets.toml   # แก้ Token ในไฟล์

streamlit run app.py
```

---

## ☁️ Deploy บน Streamlit Community Cloud (ฟรี)

1. Push repo ขึ้น GitHub (ไฟล์ `.streamlit/secrets.toml` จะถูก `.gitignore` ไม่ขึ้น)
2. ไปที่ [share.streamlit.io](https://share.streamlit.io) → **New app** → เลือก repo → `app.py`
3. **Advanced settings → Secrets** ใส่:
   ```toml
   TMD_TOKEN = "eyJ0eXAiOiJKV1Qi..."
   ```
4. **Deploy!** (2-3 นาที)

> ถ้าไม่ตั้ง Secret ก็ใส่ Token ผ่านช่องใน Sidebar ได้เลย

---

## 📁 โครงสร้าง

```
srt-weather-alert/
├── app.py                  # แอปหลัก (Streamlit)
├── requirements.txt
├── secrets.toml.example
├── README.md
├── .gitignore
└── .streamlit/
    └── config.toml         # ธีม dark
```

---

## 🛠️ การแก้ปัญหา

| อาการ | สาเหตุ / วิธีแก้ |
|---|---|
| ❌ API ไม่ตอบสนอง | เปิด expander "รายละเอียดข้อผิดพลาด" ดู error จริง |
| HTTP 401/403 | Token หมดอายุหรือผิด — ขอใหม่ |
| Timeout | เซิร์ฟเวอร์ TMD ช้า — กดรีเฟรช |
| Host not in allowlist | network ถูกบล็อก — deploy บน Streamlit Cloud แทน |

---

## 📜 License

MIT · ข้อมูลสภาพอากาศ © กรมอุตุนิยมวิทยา · โครงข่ายรถไฟ © การรถไฟแห่งประเทศไทย
