import time
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# הגדרות כלליות של העמוד
st.set_page_config(page_title="מוניטור עמדות EVEdge", page_icon="⚡", layout="centered")

API_URL = "https://cp.evedge.co.il/api/v2/app/locations"
TARGET_STATIONS = ["36091", "36092"]

# פונקציה לבדיקת סטטוס העמדות
def get_stations_status():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    results = {}
    try:
        response = requests.get(API_URL, headers=headers, timeout=10)
        if response.status_code == 200:
            json_text = response.text.lower()
            
            for station_id in TARGET_STATIONS:
                if station_id in json_text:
                    start_index = json_text.find(station_id)
                    station_section = json_text[start_index:start_index + 500]
                    
                    if "ava" in station_section:
                        results[station_id] = "פנוי"
                    else:
                        results[station_id] = "תפוס"
                else:
                    results[station_id] = "לא נמצאה בנתונים"
        else:
            st.error(f"שגיאה בתקשורת עם השרת (קוד {response.status_code})")
    except Exception as e:
        st.error(f"התרחשה שגיאה: {e}")
    
    return results

# כותרת הממשק
st.title("⚡ מוניטור עמדות טעינה EVEdge")
st.write("המערכת בענן מנטרת את הסטטוס ומבצעת רענון אוטומטי כל שעה.")

# הגדרת רענון אוטומטי של העמוד כל שעה (3,600,000 מילישניות)
st_autorefresh(interval=3600000, key="datarefresh")

# כפתור לרענון ידני מיידי
if st.button("רענן מצב כעת 🔄"):
    st.rerun()

st.divider()

# ביצוע הבדיקה והצגת הנתונים
status_data = get_stations_status()

if status_data:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("עמדה 36091")
        status1 = status_data.get("36091", "לא ידוע")
        if status1 == "פנוי":
            st.success("✅ פנוי לטעינה")
        else:
            st.error("❌ תפוס")
            
    with col2:
        st.subheader("עמדה 36092")
        status2 = status_data.get("36092", "לא ידוע")
        if status2 == "פנוי":
            st.success("✅ פנוי לטעינה")
        else:
            st.error("❌ תפוס")

st.caption(f"בדיקה אחרונה בוצעה ב: {time.strftime('%H:%M:%S')}")
