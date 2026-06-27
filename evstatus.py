import time
import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

# הגדרות כלליות של העמוד בדפדפן
st.set_page_config(page_title="מוניטור עמדות EVEdge", page_icon="⚡", layout="centered")

# הכתובת שנמצאה בכלי המפתחים ומזהי העמדות הספציפיים שלך
API_URL = "https://cp.evedge.co.il/api/v2/app/locations"
TARGET_STATIONS = ["36091", "36092"]

def get_stations_status():
    # כותרות בקשה מורחבות המדמות דפדפן כרום אמיתי כדי למנוע שגיאת 403 בענן
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "he-IL,he;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://evedge.co.il",
        "Referer": "https://evedge.co.il/",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }
    
    results = {}
    try:
        # פנייה לשרת לקבלת הנתונים
        response = requests.get(API_URL, headers=headers, timeout=15)
        
        if response.status_code == 200:
            json_text = response.text.lower()
            
            # סריקת הנתונים עבור כל עמדה ברשימה
            for station_id in TARGET_STATIONS:
                if station_id in json_text:
                    # בידוד מקטע הטקסט הרלוונטי לעמדה זו כדי לבדוק את הסטטוס שלה במדויק
                    start_index = json_text.find(station_id)
                    station_section = json_text[start_index:start_index + 500]
                    
                    # בדיקה האם מופיע סימן לסטטוס פנוי (Ava) במקטע של העמדה
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

# מנגנון רענון אוטומטי של העמוד (3,600,000 מילישניות = שעה אחת)
st_autorefresh(interval=3600000, key="datarefresh")

# כפתור המאפשר רענון ידני מהיר בכל רגע נתון
if st.button("רענן מצב כעת 🔄"):
    st.rerun()

st.divider()

# הפעלת פונקציית הבדיקה והצגת התוצאות במבנה ויזואלי
status_data = get_stations_status()

if status_data:
    # יצירת שני טורים נפרדים, אחד עבור כל עמדה
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

# הצגת שעת העדכון האחרונה בתחתית המסך
st.caption(f"בדיקה אחרונה בוצעה בשעה: {time.strftime('%H:%M:%S')}")
