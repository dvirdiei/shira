"""
קובץ לניהול גיאוקודינג והוספת כתובות חדשות
"""
from flask import jsonify, request
import csv
import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def geocode_address(address):
    """
    מחפש קואורדינטות לכתובת באמצעות Maps.co API
    
    Args:
        address (str): הכתובת לחיפוש
        
    Returns:
        dict: מילון עם lat, lon, neighborhood או None אם לא נמצא
    """
    try:
        # Get API key from environment
        api_key = os.getenv('GEOCODING_API_KEY')
        if not api_key:
            print("❌ Error: GEOCODING_API_KEY not found in environment variables")
            return None
        
        # בניית URL לחיפוש עם דגש על ישראל
        base_url = "https://geocode.maps.co/search"
        
        # Format address for search
        search_query = f"{address}, Israel"
        
        params = {
            'q': search_query,
            'api_key': api_key
        }
        
        print(f"🔍 מחפש קואורדינטות עבור: {address}")
        print(f"🌐 URL: {base_url}?q={search_query}&api_key=***")
        
        # ביצוע הבקשה
        response = requests.get(base_url, params=params, timeout=15)
        response.raise_for_status()
        
        data = response.json()
        print(f"📊 תגובה מהשרת: {data}")
        
        if data and len(data) > 0:
            result = data[0]
            
            # חילוץ פרטי המיקום
            lat = float(result['lat'])
            lon = float(result['lon'])
            
            # ניסיון לחלץ שם השכונה
            neighborhood = extract_neighborhood_from_maps_co(result)
            
            print(f"✅ נמצאו קואורדינטות: {lat}, {lon} - שכונה: {neighborhood}")
            
            return {
                'lat': lat,
                'lon': lon,
                'neighborhood': neighborhood,
                'display_name': result.get('display_name', address)
            }
        
        print(f"❌ לא נמצאו קואורדינטות עבור: {address}")
        return None
            
    except requests.RequestException as e:
        print(f"❌ שגיאת רשת בחיפוש קואורדינטות: {e}")
        return None
    except Exception as e:
        print(f"❌ שגיאה כללית בגיאוקודינג: {e}")
        return None

def extract_neighborhood_from_maps_co(result):
    """
    מחלץ שם שכונה מתוצאות Maps.co API
    
    Args:
        result (dict): תוצאת החיפוש מ-Maps.co
        
    Returns:
        str: שם השכונה או 'לא ידוע'
    """
    try:
        # ניסיון לחלץ שכונה מהכתובת המפורמטת
        if 'display_name' in result:
            # ב-Maps.co הכתובת מגיעה כ-display_name
            display_name = result['display_name']
            parts = display_name.split(',')
            
            # נחפש חלקים שעשויים להיות שכונה
            for part in parts[1:4]:  # דילוג על החלק הראשון (כתובת) ובדיקת 3 החלקים הבאים
                clean_part = part.strip()
                if clean_part and not clean_part.lower() in ['israel', 'ישראל', 'jerusalem', 'ירושלים']:
                    return clean_part
        
        # אם יש שדה place_type או type
        if 'place_type' in result:
            place_type = result['place_type']
            if place_type in ['neighbourhood', 'suburb', 'quarter']:
                return result.get('name', 'לא ידוע')
        
        # ניסיון להשתמש בשדה name אם הוא קיים
        if 'name' in result and result['name']:
            return result['name']
        
        return 'לא ידוע'
        
    except Exception as e:
        print(f"שגיאה בחילוץ שכונה מ-Maps.co: {e}")
        return 'לא ידוע'

def extract_neighborhood_from_geocoding_api(result):
    """
    מחלץ שם שכונה מתוצאות GeocodingAPI
    
    Args:
        result (dict): תוצאת החיפוש מ-GeocodingAPI
        
    Returns:
        str: שם השכונה או 'לא ידוע'
    """
    try:
        # ניסיון לחלץ שכונה מהכתובת המפורמטת
        if 'address_components' in result:
            for component in result['address_components']:
                if 'types' in component:
                    # חיפוש סוגי כתובת המציינים שכונה
                    if any(type_name in ['neighborhood', 'sublocality', 'district'] 
                           for type_name in component['types']):
                        return component.get('long_name', 'לא ידוע')
        
        # אם לא נמצא, ננסה לחלץ מהכתובת המפורמטת
        if 'formatted_address' in result:
            formatted = result['formatted_address']
            parts = formatted.split(',')
            if len(parts) >= 2:
                # לרוב השכונה תהיה בחלק השני או השלישי
                return parts[1].strip()
        
        return 'לא ידוע'
        
    except Exception as e:
        print(f"שגיאה בחילוץ שכונה: {e}")
        return 'לא ידוע'

def extract_neighborhood(address_details):
    """
    מחלץ שם שכונה מפרטי הכתובת שמוחזרים מ-Nominatim
    (נשמר לתאימות לאחור)
    
    Args:
        address_details (dict): פרטי הכתובת מ-Nominatim
        
    Returns:
        str: שם השכונה או 'לא ידוע'
    """
    # סדר עדיפויות לחיפוש שכונה
    neighborhood_keys = [
        'neighbourhood', 'suburb', 'district', 'quarter',
        'city_district', 'residential', 'town', 'village'
    ]
    
    for key in neighborhood_keys:
        if key in address_details and address_details[key]:
            return address_details[key]
    
    # אם לא נמצא, ננסה להשתמש בעיר
    if 'city' in address_details:
        return address_details['city']
    
    return 'לא ידוע'

def add_address_handler(app_root_path):
    """
    מוסיף כתובת חדשה - מחפש קואורדינטות ושומר בקובץ המתאים
    
    Expected JSON:
    {
        "address": "רחוב הדקל 15 ירושלים",
        "neighborhood": "גבעת שאול" (אופציונלי)
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'לא התקבלו נתונים'}), 400
        
        address = data.get('address', '').strip()
        
        if not address:
            return jsonify({'success': False, 'message': 'יש לספק כתובת'}), 400
        
        # בדיקה אם הכתובת כבר קיימת
        if is_address_exists(app_root_path, address):
            return jsonify({
                'success': False, 
                'message': 'הכתובת כבר קיימת במערכת'
            }), 409
        
        # המתנה קצרה למניעת overload של Nominatim
        time.sleep(1)
        
        # חיפוש קואורדינטות
        geo_result = geocode_address(address)
        
        # הכנת הנתונים לשמירה
        address_data = {
            'כתובת': address,
            'שכונה': data.get('neighborhood', '') or (geo_result['neighborhood'] if geo_result else 'לא ידוע'),
            'ביקרנו': 'לא'
        }
        
        if geo_result:
            # אם נמצאו קואורדינטות - שמירה ב-found_addresses.csv
            address_data['קו רוחב'] = geo_result['lat']
            address_data['קו אורך'] = geo_result['lon']
            
            success = save_to_csv(
                app_root_path, 
                'found_addresses.csv', 
                address_data
            )
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'הכתובת נוספה בהצלחה עם קואורדינטות',
                    'data': {
                        'address': address,
                        'lat': geo_result['lat'],
                        'lon': geo_result['lon'],
                        'neighborhood': address_data['שכונה'],
                        'source': 'geocoded_new'
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'שגיאה בשמירת הכתובת'
                }), 500
        else:
            # אם לא נמצאו קואורדינטות - שמירה ב-not_found_addresses.csv
            address_data['קו רוחב'] = ''
            address_data['קו אורך'] = ''
            
            success = save_to_csv(
                app_root_path,
                'not_found_addresses.csv',
                address_data
            )
            
            if success:
                return jsonify({
                    'success': True,
                    'message': 'הכתובת נוספה אך לא נמצאו קואורדינטות',
                    'data': {
                        'address': address,
                        'neighborhood': address_data['שכונה'],
                        'source': 'manual_needed'
                    }
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'שגיאה בשמירת הכתובת'
                }), 500
                
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'שגיאה בהוספת הכתובת: {str(e)}'
        }), 500

def batch_geocode_handler(app_root_path):
    """
    מעבד כמה כתובות בבת אחת עם גיאוקודינג
    
    Expected JSON:
    {
        "addresses": [
            {"address": "רחוב הדקל 15 ירושלים"},
            {"address": "שדרות גולדה מאיר 10 ירושלים", "neighborhood": "רחביה"}
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'addresses' not in data:
            return jsonify({'success': False, 'message': 'לא התקבלה רשימת כתובות'}), 400
        
        addresses = data['addresses']
        
        if not isinstance(addresses, list) or len(addresses) == 0:
            return jsonify({'success': False, 'message': 'רשימת כתובות ריקה או לא תקינה'}), 400
        
        results = []
        found_count = 0
        not_found_count = 0
        duplicate_count = 0
        
        for i, addr_data in enumerate(addresses):
            if not isinstance(addr_data, dict) or 'address' not in addr_data:
                results.append({
                    'index': i,
                    'status': 'error',
                    'message': 'פורמט כתובת לא תקין'
                })
                continue
            
            address = addr_data['address'].strip()
            
            if not address:
                results.append({
                    'index': i,
                    'status': 'error',
                    'message': 'כתובת ריקה'
                })
                continue
            
            # בדיקת כפילות
            if is_address_exists(app_root_path, address):
                duplicate_count += 1
                results.append({
                    'index': i,
                    'address': address,
                    'status': 'duplicate',
                    'message': 'כתובת כבר קיימת'
                })
                continue
            
            # המתנה בין בקשות למניעת overload
            if i > 0:
                time.sleep(1.5)
            
            # גיאוקודינג
            geo_result = geocode_address(address)
            
            # הכנת נתונים
            address_data = {
                'כתובת': address,
                'שכונה': addr_data.get('neighborhood', '') or (geo_result['neighborhood'] if geo_result else 'לא ידוע'),
                'ביקרנו': 'לא'
            }
            
            if geo_result:
                # נמצאו קואורדינטות
                address_data['קו רוחב'] = geo_result['lat']
                address_data['קו אורך'] = geo_result['lon']
                
                if save_to_csv(app_root_path, 'found_addresses.csv', address_data):
                    found_count += 1
                    results.append({
                        'index': i,
                        'address': address,
                        'status': 'found',
                        'lat': geo_result['lat'],
                        'lon': geo_result['lon'],
                        'neighborhood': address_data['שכונה']
                    })
                else:
                    results.append({
                        'index': i,
                        'address': address,
                        'status': 'error',
                        'message': 'שגיאה בשמירה'
                    })
            else:
                # לא נמצאו קואורדינטות
                address_data['קו רוחב'] = ''
                address_data['קו אורך'] = ''
                
                if save_to_csv(app_root_path, 'not_found_addresses.csv', address_data):
                    not_found_count += 1
                    results.append({
                        'index': i,
                        'address': address,
                        'status': 'not_found',
                        'neighborhood': address_data['שכונה']
                    })
                else:
                    results.append({
                        'index': i,
                        'address': address,
                        'status': 'error',
                        'message': 'שגיאה בשמירה'
                    })
        
        return jsonify({
            'success': True,
            'message': f'הושלמה עיבוד {len(addresses)} כתובות',
            'summary': {
                'total': len(addresses),
                'found': found_count,
                'not_found': not_found_count,
                'duplicates': duplicate_count,
                'errors': len(addresses) - found_count - not_found_count - duplicate_count
            },
            'results': results
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'שגיאה בעיבוד הכתובות: {str(e)}'
        }), 500

def retry_geocoding_handler(app_root_path):
    """
    מנסה שוב לחפש קואורדינטות עבור כתובות שלא נמצאו
    """
    try:
        # קריאת כתובות ללא קואורדינטות
        not_found_path = os.path.join(app_root_path, 'database', 'not_found_addresses.csv')
        
        if not os.path.exists(not_found_path):
            return jsonify({
                'success': True,
                'message': 'אין כתובות ללא קואורדינטות',
                'processed': 0
            })
        
        addresses_to_retry = []
        
        with open(not_found_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if not row['קו רוחב'] or not row['קו אורך']:
                    addresses_to_retry.append(row)
        
        if not addresses_to_retry:
            return jsonify({
                'success': True,
                'message': 'אין כתובות לעיבוד חוזר',
                'processed': 0
            })
        
        found_count = 0
        updated_addresses = []
        
        for i, addr_row in enumerate(addresses_to_retry):
            address = addr_row['כתובת']
            
            # המתנה בין בקשות
            if i > 0:
                time.sleep(2)
            
            geo_result = geocode_address(address)
            
            if geo_result:
                # נמצאו קואורדינטות - העברה ל-found_addresses
                found_data = {
                    'כתובת': address,
                    'שכונה': addr_row['שכונה'] or geo_result['neighborhood'],
                    'קו רוחב': geo_result['lat'],
                    'קו אורך': geo_result['lon'],
                    'ביקרנו': addr_row['ביקרנו']
                }
                
                if save_to_csv(app_root_path, 'found_addresses.csv', found_data):
                    found_count += 1
                    updated_addresses.append(address)
        
        # הסרת הכתובות שנמצאו מקובץ not_found
        if updated_addresses:
            remove_addresses_from_csv(app_root_path, 'not_found_addresses.csv', updated_addresses)
        
        return jsonify({
            'success': True,
            'message': f'נמצאו קואורדינטות עבור {found_count} כתובות',
            'processed': len(addresses_to_retry),
            'found': found_count,
            'updated_addresses': updated_addresses
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'שגיאה בעיבוד חוזר: {str(e)}'
        }), 500

def is_address_exists(app_root_path, address):
    """בדיקה אם כתובת כבר קיימת באחד מהקבצים"""
    files_to_check = [
        'found_addresses.csv',
        'not_found_addresses.csv',
        'future_use.csv'
    ]
    
    for file_name in files_to_check:
        file_path = os.path.join(app_root_path, 'database', file_name)
        
        if not os.path.exists(file_path):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['כתובת'].strip().lower() == address.strip().lower():
                        return True
        except:
            continue
    
    return False

def save_to_csv(app_root_path, file_name, data):
    """שמירת נתונים לקובץ CSV"""
    try:
        file_path = os.path.join(app_root_path, 'database', file_name)
        file_exists = os.path.exists(file_path)
        
        # הגדרת סדר העמודות
        fieldnames = ['כתובת', 'שכונה', 'קו רוחב', 'קו אורך', 'ביקרנו']
        
        with open(file_path, 'a', encoding='utf-8', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            
            # כתיבת headers אם זה קובץ חדש
            if not file_exists:
                writer.writeheader()
            
            writer.writerow(data)
        
        return True
        
    except Exception as e:
        print(f"שגיאה בשמירת הקובץ {file_name}: {e}")
        return False

def remove_addresses_from_csv(app_root_path, file_name, addresses_to_remove):
    """הסרת כתובות מקובץ CSV"""
    try:
        file_path = os.path.join(app_root_path, 'database', file_name)
        temp_path = file_path + '.tmp'
        
        if not os.path.exists(file_path):
            return True
        
        addresses_set = set(addr.strip().lower() for addr in addresses_to_remove)
        
        with open(file_path, 'r', encoding='utf-8') as infile, \
             open(temp_path, 'w', encoding='utf-8', newline='') as outfile:
            
            reader = csv.DictReader(infile)
            writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
            writer.writeheader()
            
            for row in reader:
                if row['כתובת'].strip().lower() not in addresses_set:
                    writer.writerow(row)
        
        os.replace(temp_path, file_path)
        return True
        
    except Exception as e:
        print(f"שגיאה בהסרת כתובות מ-{file_name}: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return False
