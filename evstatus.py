import time
import requests
from plyer import notification

# הכתובת המדויקת שהעתקת מהדפדפן
API_URL = "https://cp.evedge.co.il/api/v2/app/locations"

# מזהי העמדות שברצוננו לבדוק
TARGET_STATIONS = ["36091", "36092"]

def check_stations():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(API_URL, headers=headers, timeout=10)
        
        if response.status_code == 200:
            json_text = response.text.lower()
            
            # בדיקה עבור כל עמדה בנפרד בתוך הנתונים שחזרו
            available_stations = []
            
            for station_id in TARGET_STATIONS:
                # אנחנו מחפשים האם ה-ID קיים בטקסט, ואז בודקים אם המילה ava (פנוי) מופיעה קרוב אליו
                # זו בדיקה כללית ומהירה שעובדת מצוין ברוב סוגי ה-JSON
                if station_id in json_text:
                    # לוקחים את מקטע הטקסט סביב ה-ID כדי לוודא שאנחנו בודקים את הסטטוס של העמדה הספציפית הזו
                    start_index = json_text.find(station_id)
                    # נביט ב-500 התווים הבאים שמתארים את העמדה הזו
                    station_section = json_text[start_index:start_index + 500]
                    
                    if "ava" in station_section:
                        available_stations.append(station_id)
            
            # ניסוח ההודעה על פי התוצאות
            if available_stations:
                stations_str = ", ".join(available_stations)
                message = f"עמדות פנויות לטעינה: {stations_str}"
            else:
                message = "שתי העמדות (36091, 36092) תפוסות כרגע."
                
            send_notification(message)
            print(f"[{time.strftime('%H:%M:%S')}] {message}")
            
        else:
            print(f"שגיאה בקבלת נתונים מהשרת, קוד שגיאה: {response.status_code}")
            
    except Exception as e:
        print(f"התרחשה שגיאה במהלך הבדיקה: {e}")

def send_notification(text):
    try:
        notification.notify(
            title="סטטוס עמדות EVEdge",
            message=text,
            app_name="EV Monitor",
            timeout=10
        )
    except Exception as e:
        print(f"לא ניתן היה להציג התראה: {e}")

def main():
    print("מערכת הניטור הופעלה. בדיקה תתבצע בכל שעה.")
    check_stations()
    
    while True:
        time.sleep(3600)  # המתנה של שעה (3600 שניות)
        check_stations()

if __name__ == "__main__":
    main()
