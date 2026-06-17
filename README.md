# 🚆 ระบบแจ้งเตือนสภาพอากาศโครงข่ายรถไฟไทย
### Thai Railway Network Weather & Disaster Alert System

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io)

ระบบแสดงแผนที่และแจ้งเตือนสภาพอากาศ ฝนตก และภัยธรรมชาติ  
สำหรับเส้นทางโครงข่ายรถไฟทั่วประเทศไทย  
ดึงข้อมูลจริงจาก **กรมอุตุนิยมวิทยา (TMD API)**

---

## ✨ ฟีเจอร์หลัก

| Feature | รายละเอียด |
|---|---|
| 🗺️ แผนที่แบบ interactive | แสดงเส้นทางรถไฟทั้ง 5 สาย + สีตามระดับฝน |
| ⚠️ แจ้งเตือนภัย | ดึงข่าวเตือนภัยสภาพอากาศจาก TMD โดยตรง |
| 🌧️ ระดับฝนรายสถานี | คำนวณจากสถานีอุตุฯ ที่ใกล้ที่สุด |
| 🌋 ข้อมูลแผ่นดินไหว | ติดตามเหตุการณ์แผ่นดินไหวในภูมิภาค |
| 📊 ตารางรายสาย | เปรียบเทียบสถานีทั้งสายเหนือ/ใต้/อีสาน/ตะวันออก |
| 🌐 พยากรณ์ 7 วัน | แสดงรายภาค เชื่อมโยงกับเส้นทางรถไฟ |

---

## 🛤️ โครงข่ายรถไฟที่รองรับ

- **สายเหนือ** — กรุงเทพ → เชียงใหม่ (7 สถานี)
- **สายตะวันออกเฉียงเหนือ** — กรุงเทพ → หนองคาย (6 สถานี)
- **สายอีสานใต้** — ถนนจิระ → อุบลราชธานี (5 สถานี)
- **สายใต้** — กรุงเทพ → ปาดังเบซาร์ (7 สถานี)
- **สายตะวันออก** — กรุงเทพ → อรัญประเทศ (4 สถานี)

---

## 🚀 วิธีติดตั้งและรัน

### รันบน Local
```bash
git clone https://github.com/<YOUR_USERNAME>/rail-weather-alert
cd rail-weather-alert

# สร้าง Virtual Environment
python -m venv venv
source venv/bin/activate          # macOS/Linux
venv\Scripts\activate             # Windows

# ติดตั้ง dependencies
pip install -r requirements.txt

# ตั้งค่า TMD Token
mkdir -p .streamlit
cp secrets.toml.example .streamlit/secrets.toml
# แก้ไข secrets.toml ใส่ Token ของคุณ

# รัน App
streamlit run app.py
```

---

## ☁️ Deploy บน Streamlit Community Cloud (ฟรี)

1. **Fork/Push** repo นี้ขึ้น GitHub ของคุณ
2. ไปที่ [share.streamlit.io](https://share.streamlit.io) → **New app**
3. เลือก repo → Branch: `main` → File: `app.py`
4. คลิก **Advanced settings** → **Secrets** แล้วใส่:
   ```toml
   TMD_TOKEN = "eyJ0eXAiOiJKV1Qi..."
   ```
5. คลิก **Deploy!** — ใช้เวลาประมาณ 2-3 นาที ✅

> **หมายเหตุ:** Token จะถูกเก็บเป็น Secret ใน Streamlit Cloud อย่างปลอดภัย ไม่ถูก commit ขึ้น GitHub

---

## 🔑 TMD API

ระบบใช้ API จาก [data.tmd.go.th](https://data.tmd.go.th/api/index1.php)

| Endpoint | ข้อมูล | อัพเดต |
|---|---|---|
| `WeatherToday/V2` | สภาพอากาศรายวัน | ทุกวัน 07:00 น. |
| `Weather3Hours/V2` | ราย 3 ชั่วโมง | ทุก 3 ชั่วโมง |
| `WeatherWarningNews/V1` | ข่าวเตือนภัย | Real-time |
| `DailySeismicEvent/V1` | แผ่นดินไหว | รายวัน |
| `WeatherForecast7DaysByRegion/V1` | พยากรณ์รายภาค | วันละ 4 ครั้ง |

---

## 📁 โครงสร้างไฟล์

```
rail-weather-alert/
├── app.py                    # Main Streamlit application
├── requirements.txt          # Python dependencies
├── secrets.toml.example      # Template สำหรับ TMD Token
├── README.md
├── .streamlit/
│   └── config.toml           # Dark theme configuration
└── .github/
    └── workflows/
        └── ci.yml            # GitHub Actions CI
```

---

## 🎨 การออกแบบ

- **Dark Navy Theme** — เหมาะกับการใช้งาน 24/7 ในห้องควบคุม
- **Color-coded alerts** — แดง/ส้ม/เหลือง/เขียว ตามระดับความเสี่ยง
- **Interactive Folium Map** — คลิกเพื่อดูรายละเอียดสถานี
- **Thai-first UI** — ภาษาไทยเป็นหลัก รองรับ Unicode

---

## 📜 License

MIT License · ข้อมูลอุตุนิยมวิทยา © กรมอุตุนิยมวิทยา · ข้อมูลรถไฟ © การรถไฟแห่งประเทศไทย
