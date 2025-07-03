import os
import json
import requests
import time
from urllib.parse import quote

# הגדרת נתיבים
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # הנתיב של הספרייה שבה הסקריפט נמצא
INPUT_DIR = os.path.join(SCRIPT_DIR, "input")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "output")
INPUT_FILE = "adrees.txt"
DATABASE_DIR = os.path.join(SCRIPT_DIR, "..", "database")
FOUND_ADDRESSES_OUTPUT = os.path.join(DATABASE_DIR, "found_addresses.csv")
NOT_FOUND_ADDRESSES_OUTPUT = os.path.join(DATABASE_DIR, "not_found_addresses.csv")
FUTURE_USE_OUTPUT = os.path.join(DATABASE_DIR, "future_use.csv")

# ייבוא מפתח ה‑API מקובץ התצורה
try:
    from config import API_KEY
    print("[מידע] מפתח API נטען מקובץ התצורה")
except ImportError:
    print("[אזהרה] לא ניתן לטעון את קובץ התצורה. משתמש במפתח ברירת מחדל.")
    API_KEY = "your_default_api_key_here"  # מפתח ברירת מחדל במקרה שקובץ התצורה לא קיים

def ensure_directories():
    """יצירת תיקיות נדרשות אם אינן קיימות"""
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(DATABASE_DIR, exist_ok=True)
    print(f"[מידע] וידוא קיום תיקיות: {INPUT_DIR}, {OUTPUT_DIR}, {DATABASE_DIR}")

def save_not_found_to_file(not_found_list):
    """שמירת כתובות שלא נמצאו בקובץ CSV למילוי ידני"""
    if not not_found_list:
        print("אין כתובות שלא נמצאו לשמירה.")
        return
        
    # יצירת תיקיית database אם לא קיימת
    database_dir = os.path.join(SCRIPT_DIR, "..", "database")
    os.makedirs(database_dir, exist_ok=True)
    
    path = os.path.join(database_dir, 'not_found_addresses.csv')
    
    # הכנת כותרות הקובץ
    headers = ['כתובת', 'קו רוחב', 'קו אורך', 'שכונה', 'ביקרנו']
    
    with open(path, 'w', encoding='utf-8') as f:
        # כתיבת שורת הכותרות
        f.write(','.join(headers) + '\n')
        
        # כתיבת הכתובות שלא נמצאו עם תאים ריקים למילוי ידני
        for addr in not_found_list:
            # יוצר שורה עם הכתובת והשאר ריקים
            row = [addr, '', '', '', 'לא']  # ברירת מחדל - לא ביקרנו
            f.write(','.join(row) + '\n')
            
    print(f"[OK] רשימת כתובות שלא נמצאו נשמרה בקובץ: {path} (מוכן למילוי ידני)")
    
def save_found_addresses_to_file(results):
    """שמירת כתובות שנמצאו להן קואורדינטות בקובץ CSV"""
    if not results:
        print("אין כתובות שנמצאו לשמירה.")
        return
        
    # יצירת תיקיית database אם לא קיימת
    database_dir = os.path.join(SCRIPT_DIR, "..", "database")
    os.makedirs(database_dir, exist_ok=True)
    
    path = os.path.join(database_dir, 'found_addresses.csv')
    
    # הכנת כותרות הקובץ
    headers = ['כתובת', 'קו רוחב', 'קו אורך', 'שכונה', 'ביקרנו']
    
    with open(path, 'w', encoding='utf-8') as f:
        # כתיבת שורת הכותרות
        f.write(','.join(headers) + '\n')
        
        # כתיבת נתוני הכתובות
        for result in results:
            if result:
                row = [
                    result['full_address'],
                    str(result['lat']),
                    str(result['lon']),
                    result['neighborhood'],
                    'לא'  # ברירת מחדל - לא ביקרנו עדיין
                ]
                f.write(','.join(row) + '\n')
                
    print(f"[OK] רשימת כתובות שנמצאו עם קואורדינטות נשמרה בקובץ: {path}")

def geocode_address(address):
    """
    מבצע geocode לכתובת וחוזר עם נתוני מיקום.
    מנסה עד 3 פעמים במקרה של שגיאה.
    """
    for attempt in range(3):  # שלושה ניסיונות לכל כתובת
        try:
            url = f"https://geocode.maps.co/search?api_key={API_KEY}&q={quote(address)}"
            resp = requests.get(url)
            
            if resp.status_code == 429:  # Too Many Requests
                print(f"[ממתין] ממתין בשל הגבלת קצב API...")
                time.sleep(2)
                continue
                
            resp.raise_for_status()
            data = resp.json()
            
            if not data:
                print(f"[אזהרה] לא נמצאו תוצאות עבור: {address}")
                return None
                
            result = data[0]
            lat = float(result['lat'])
            lon = float(result['lon'])
            
            # כעת נשיג מידע נוסף על המיקום (כגון שכונה)
            neighborhood = get_location_details(lat, lon)
            
            return {
                'lat': lat,
                'lon': lon,
                'full_address': address,
                'neighborhood': neighborhood
            }
            
        except Exception as e:
            print(f"[שגיאה] שגיאה בניסיון {attempt+1} עבור '{address}': {str(e)}")
            time.sleep(1)
    
    print(f"[נכשל] כל הניסיונות נכשלו עבור: {address}")
    return None

def get_location_details(lat, lon):
    """משיג פרטים נוספים על מיקום לפי קואורדינטות"""
    for _ in range(3):  # שלושה ניסיונות
        try:
            url = f"https://geocode.maps.co/reverse?api_key={API_KEY}&lat={lat}&lon={lon}"
            resp = requests.get(url)
            
            if resp.status_code == 429:  # Too Many Requests
                time.sleep(2)
                continue
                
            resp.raise_for_status()
            data = resp.json()
            
            addr = data.get('address', {})
            
            # נסה להשיג את השכונה או אזור
            neighborhood = (addr.get('suburb') or 
                           addr.get('neighbourhood') or 
                           addr.get('quarter') or 
                           addr.get('city_district') or 
                           addr.get('district') or 
                           "לא ידוע")
            
            return neighborhood
            
        except Exception as e:
            print(f"[שגיאה] שגיאה בהשגת פרטי מיקום: {str(e)}")
            time.sleep(1)
    
    return "לא ידוע"

def read_addresses_from_file(file_path):
    """קריאת כתובות מקובץ טקסט"""
    if not os.path.exists(file_path):
        print(f"[שגיאה] הקובץ {file_path} לא נמצא!")
        return []
        
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            addresses = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
        print(f"[מידע] נקראו {len(addresses)} כתובות מהקובץ {file_path}")
        return addresses
    except Exception as e:
        print(f"[שגיאה] בעיה בקריאת הקובץ {file_path}: {str(e)}")
        return []

def create_future_use_file():
    """יוצר או מעדכן את קובץ future_use.csv לשימוש עתידי"""
    # יצירת תיקיית database אם לא קיימת
    os.makedirs(DATABASE_DIR, exist_ok=True)
    
    path = FUTURE_USE_OUTPUT
    
    # בדיקה אם הקובץ כבר קיים
    if not os.path.exists(path):
        # הכנת כותרות הקובץ (דוגמה לשדות שייתכן ויהיו שימושיים בעתיד)
        headers = ['כתובת', 'קו רוחב', 'קו אורך', 'שכונה', 'ביקרנו', 'קטגוריה', 'הערות']
        
        with open(path, 'w', encoding='utf-8') as f:
            # כתיבת שורת הכותרות
            f.write(','.join(headers) + '\n')
            
        print(f"[OK] קובץ נתונים עתידי נוצר בהצלחה: {path}")
    else:
        print(f"[מידע] קובץ נתונים עתידי כבר קיים: {path}")

def main():
    print("[התחלה] התחלת תהליך המרת כתובות לקואורדינטות")
    
    # וידוא קיום תיקיות נדרשות
    ensure_directories()
    
    # יצירת קובץ השימוש העתידי אם לא קיים
    create_future_use_file()
    
    # קריאת כתובות מהקובץ
    file_path = os.path.join(INPUT_DIR, INPUT_FILE)
    print(f"[מידע] מנסה לקרוא כתובות מ: {file_path}")
    addresses = read_addresses_from_file(file_path)
    
    if not addresses:
        print("[שגיאה] לא נמצאו כתובות לעיבוד. בדוק את קובץ הקלט.")
        return
    
    print(f"[מידע] נמצאו {len(addresses)} כתובות לעיבוד")
    
    # עיבוד כל הכתובות
    results = []
    not_found = []
    
    for idx, address in enumerate(addresses, start=1):
        print(f"\n[מעבד] ({idx}/{len(addresses)}) מעבד כתובת: {address}")
        result = geocode_address(address)
        
        if result:
            print(f"[OK] נמצאו קואורדינטות: {result['lat']}, {result['lon']} (שכונה: {result['neighborhood']})")
            results.append(result)
        else:
            print(f"[נכשל] לא נמצאו קואורדינטות עבור: {address}")
            not_found.append(address)
        
        # המתנה קצרה בין בקשות כדי למנוע חסימת IP
        time.sleep(1)
    
    # שמירת תוצאות
    if results:
        # שמירת הכתובות שנמצאו בקובץ CSV
        save_found_addresses_to_file(results)
        
        # שמירת הקואורדינטות גם בקובץ JSON נוסף
        with open(os.path.join(OUTPUT_DIR, 'coordinates.json'), 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    # שמירת כתובות שלא נמצאו
    if not_found:
        print(f"\n[אזהרה] {len(not_found)} כתובות לא נמצאו:")
        for addr in not_found:
            print(f" - {addr}")
        save_not_found_to_file(not_found)
    
    print("[סיום] התהליך הסתיים בהצלחה")

if __name__ == '__main__':
    main()
