import os
import json
import requests
import time
from urllib.parse import quote

# הגדרת נתיבים
INPUT_DIR = "input"
OUTPUT_DIR = "output"
INPUT_FILE = "adrees.txt"
FAMOUS_LOCATIONS_OUTPUT = "../database/famous_locations.csv"
MANUAL_LOCATIONS_OUTPUT = "../database/manual_locations.csv"

# מפתח ה‑API לגאוקודינג
API_KEY = "674f3d5932464986828229gmn1437f0"

def ensure_directories():
    """יצירת תיקיות נדרשות אם אינן קיימות"""
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs("../database", exist_ok=True)

def save_not_found_to_file(not_found_list):
    """שמירת כתובות שלא נמצאו בקובץ טקסט"""
    if not not_found_list:
        print("אין כתובות שלא נמצאו לשמירה.")
        return
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, 'not_found_addresses.txt')
    with open(path, 'w', encoding='utf-8') as f:
        for addr in not_found_list:
            f.write(f"{addr}\n")
    print(f"[OK] רשימת כתובות שלא נמצאו נשמרה בקובץ: {path}")

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
        
    with open(file_path, 'r', encoding='utf-8') as f:
        addresses = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
    
    return addresses

def save_to_csv_files(results):
    """שמירת התוצאות לקבצי CSV"""
    # קריאת קבצים קיימים אם הם קיימים
    famous_data = []
    manual_data = []
    
    # קריאת קובץ המיקומים המפורסמים אם קיים
    if os.path.exists(FAMOUS_LOCATIONS_OUTPUT):
        try:
            with open(FAMOUS_LOCATIONS_OUTPUT, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    headers = lines[0].strip().split(',')
                    for line in lines[1:]:
                        values = line.strip().split(',')
                        if len(values) >= len(headers):
                            entry = {headers[i]: values[i] for i in range(len(headers))}
                            famous_data.append(entry)
        except:
            print("[שגיאה] שגיאה בקריאת קובץ המיקומים המפורסמים הקיים")
    
    # קריאת קובץ המיקומים הידניים אם קיים
    if os.path.exists(MANUAL_LOCATIONS_OUTPUT):
        try:
            with open(MANUAL_LOCATIONS_OUTPUT, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    headers = lines[0].strip().split(',')
                    for line in lines[1:]:
                        values = line.strip().split(',')
                        if len(values) >= len(headers):
                            entry = {headers[i]: values[i] for i in range(len(headers))}
                            manual_data.append(entry)
        except:
            print("[שגיאה] שגיאה בקריאת קובץ המיקומים הידניים הקיים")
    
    # הכנת הכותרות לקבצים
    famous_headers = ['שם מקום', 'תיאור', 'קו רוחב', 'קו אורך', 'כתובת', 'שכונה']
    manual_headers = ['שם מקום', 'תיאור', 'קו רוחב', 'קו אורך', 'תאריך הוספה', 'מוסף על ידי', 'שכונה']
    
    # הוספת שדה שכונה אם לא קיים
    for entry in famous_data:
        if 'שכונה' not in entry:
            entry['שכונה'] = 'לא ידוע'
    
    for entry in manual_data:
        if 'שכונה' not in entry:
            entry['שכונה'] = 'לא ידוע'
    
    # הכנת נתונים חדשים
    today = time.strftime("%d/%m/%Y")
    
    # הוספת התוצאות החדשות
    for result in results:
        if result is None:
            continue
            
        # הכנת הנתונים לשני הקבצים
        place_name = result['full_address'].split(',')[0] if ',' in result['full_address'] else result['full_address']
        
        # הוספה לקובץ המיקומים המוכרים
        new_famous = {
            'שם מקום': place_name,
            'תיאור': f"מיקום שנוסף באמצעות גאוקודינג",
            'קו רוחב': str(result['lat']),
            'קו אורך': str(result['lon']),
            'כתובת': result['full_address'],
            'שכונה': result['neighborhood']
        }
        famous_data.append(new_famous)
        
        # הוספה לקובץ המיקומים הידניים
        new_manual = {
            'שם מקום': place_name,
            'תיאור': f"מיקום שנוסף באמצעות גאוקודינג",
            'קו רוחב': str(result['lat']),
            'קו אורך': str(result['lon']),
            'תאריך הוספה': today,
            'מוסף על ידי': "מערכת גאוקודינג",
            'שכונה': result['neighborhood']
        }
        manual_data.append(new_manual)
    
    # שמירת הקבצים המעודכנים
    # שמירת קובץ המיקומים המפורסמים
    with open(FAMOUS_LOCATIONS_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(','.join(famous_headers) + '\n')
        for entry in famous_data:
            values = [str(entry.get(header, '')) for header in famous_headers]
            f.write(','.join(values) + '\n')
    
    # שמירת קובץ המיקומים הידניים
    with open(MANUAL_LOCATIONS_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(','.join(manual_headers) + '\n')
        for entry in manual_data:
            values = [str(entry.get(header, '')) for header in manual_headers]
            f.write(','.join(values) + '\n')
    
    print(f"[OK] נתונים נשמרו בהצלחה לקבצי CSV")

def main():
    print("[התחלה] התחלת תהליך המרת כתובות לקואורדינטות")
    
    # וידוא קיום תיקיות נדרשות
    ensure_directories()
    
    # קריאת כתובות מהקובץ
    file_path = os.path.join(INPUT_DIR, INPUT_FILE)
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
        save_to_csv_files(results)
        
        # שמירת הקואורדינטות גם בקובץ JSON נוסף
        with open(os.path.join(OUTPUT_DIR, 'coordinates.json'), 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    # דוח סיכום
    if not_found:
        print(f"\n[אזהרה] {len(not_found)} כתובות לא נמצאו:")
        for addr in not_found:
            print(f" - {addr}")
        save_not_found_to_file(not_found)
    
    print("[סיום] התהליך הסתיים בהצלחה")

if __name__ == '__main__':
    main()
