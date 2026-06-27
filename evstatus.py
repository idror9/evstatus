import time
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# הגדרות כלליות של העמוד בדפדפן
st.set_page_config(page_title="מוניטור עמדות EVEdge", page_icon="⚡", layout="centered")

API_URL = "https://cp.evedge.co.il/api/v2/app/locations"
TARGET_STATIONS = ["36091", "36092"]

def get_stations_status():
    # כותרות הבקשה המדמות דפדפן
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://evedge.co.il",
        "Referer": "https://evedge.co.il/",
        "Content-Type": "application/json"
    }
    
    # יצירת חותמת הזמן הנוכחית במבנה המדויק שהשרת מצפה לו (YYYY-MM-DD HH:MM:SS.000)
    current_timestamp = time.strftime("%Y-%m-%d %H:%M:%S.000")
    
    # בניית ה-Payload שגילינו בכלי המפתחים
    payload = {
        "locations": {
            "475": current_timestamp
        }
    }
    
    results = {}
    try:
        # ביצוע בקשת POST במקום GET, ושליחת הנתונים בפורמט JSON
        response = requests.post(API_URL, headers=headers, json=payload, timeout=15)
        
        if response.status_code == 200:
            json_text = response.text.lower()
            
            # סריקת הנתונים עבור כל עמדה
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
            st.error(f"שגיאה בתקשורת עם השרת (קוד שגיאה: {response.status_code})")
            
    except Exception as e:
        st.error(f"התרחשה שגיאה במהלך החיבור: {e}")
        
    return results

# כותרת הממשק הוויזואלי
st.title("⚡ מוניטור עמדות טעינה EVEdge")
st.write("המערכת מנטרת את סטטוס העמדות ומבצעת רענון אוטומטי בכל שעה עגולה.")

# מנגנון רענון אוטומטי של העמוד (שעה אחת = 3,600,000 מילישניות)
st_autorefresh(interval=3600000, key="datarefresh")

# כפתור המאפשר רענון ידני מהיר בכל רגע
if st.button("רענן מצב כעת 🔄"):
    st.rerun()

st.divider()

# הפעלת פונקציית הבדיקה והצגת התוצאות
status_data = get_stations_status()

if status_data:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("עמדה 36091")
        status1 = status_data.get("36091", "לא ידוע")
        if status1 == "פנוי":
            st.success("✅ פנוי לטעינה")
        elif status1 == "תפוס":
            st.error("❌ תפוס")
        else:
            st.warning(f"⚠️ {status1}")
            
    with col2:
        st.subheader("עמדה 36092")
        status2 = status_data.get("36092", "לא ידוע")
        if status2 == "פנוי":
            st.success("✅ פנוי לטעינה")
        elif status2 == "תפוס":
            st.error("❌ תפוס")
        else:
            st.warning(f"⚠️ {status2}")

st.caption(f"בדיקה אחרונה בוצעה בשעה: {time.strftime('%H:%M:%S')}")
