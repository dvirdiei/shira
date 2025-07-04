"""
קובץ לניהול כל פונקציות ה-API
"""
from flask import jsonify, request
import csv
import os

def get_addresses_handler(app_root_path):
    """מחזיר את כל הכתובות עם קואורדינטות מהקובץ CSV"""
    addresses = []
    csv_path = os.path.join(app_root_path, 'database', 'found_addresses.csv')
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # בדיקה שיש קואורדינטות תקינות
                if row['קו רוחב'] and row['קו אורך']:
                    try:
                        lat = float(row['קו רוחב'])
                        lon = float(row['קו אורך'])
                        addresses.append({
                            'address': row['כתובת'],
                            'lat': lat,
                            'lon': lon,
                            'neighborhood': row['שכונה'],
                            'visited': row['ביקרנו'] == 'כן',
                            'source': 'geocoded'  # מקור: גיאוקודינג אוטומטי
                        })
                    except ValueError:
                        # אם יש בעיה בהמרת הקואורדינטות, נדלג על הכתובת
                        continue
        
        return jsonify(addresses)
        
    except FileNotFoundError:
        return jsonify({'error': 'קובץ הכתובות לא נמצא'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_manual_addresses_handler(app_root_path):
    """מחזיר כתובות שנוספו באופן ידני מקובץ future_use.csv ו-not_found_addresses.csv"""
    addresses = []
    
    # קובצים לבדיקה
    csv_files = [
        ('future_use.csv', 'manual'),
        ('not_found_addresses.csv', 'manual_corrected')
    ]
    
    for file_name, source_type in csv_files:
        csv_path = os.path.join(app_root_path, 'database', file_name)
        
        try:
            with open(csv_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                for row in csv_reader:
                    # בדיקה שיש קואורדינטות תקינות (נוספו ידנית)
                    if row['קו רוחב'] and row['קו אורך']:
                        try:
                            lat = float(row['קו רוחב'])
                            lon = float(row['קו אורך'])
                            addresses.append({
                                'address': row['כתובת'],
                                'lat': lat,
                                'lon': lon,
                                'neighborhood': row['שכונה'] if row['שכונה'] else 'לא ידוע',
                                'visited': row['ביקרנו'] == 'כן',
                                'source': source_type  # מקור: הוספה ידנית או תיקון ידני
                            })
                        except ValueError:
                            # אם יש בעיה בהמרת הקואורדינטות, נדלג על הכתובת
                            continue
        except FileNotFoundError:
            continue  # אם הקובץ לא קיים, נמשיך לקובץ הבא
        except Exception as e:
            continue
    
    return jsonify(addresses)

def get_all_addresses_handler(app_root_path):
    """מחזיר את כל הכתובות - גם מגיאוקודינג וגם ידניות"""
    try:
        # קבלת כתובות מגיאוקודינג
        geocoded_response = get_addresses_handler(app_root_path)
        geocoded_data = geocoded_response.get_json()
        
        # קבלת כתובות ידניות
        manual_response = get_manual_addresses_handler(app_root_path)
        manual_data = manual_response.get_json()
        
        # איחוד הרשימות
        all_addresses = []
        if isinstance(geocoded_data, list):
            all_addresses.extend(geocoded_data)
        if isinstance(manual_data, list):
            all_addresses.extend(manual_data)
        
        return jsonify(all_addresses)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_missing_coordinates_handler(app_root_path):
    """מחזיר כתובות ללא קואורדינטות מקובץ not_found_addresses.csv"""
    addresses = []
    csv_path = os.path.join(app_root_path, 'database', 'not_found_addresses.csv')
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # בדיקה שאין קואורדינטות או שהן ריקות
                if not row['קו רוחב'] or not row['קו אורך']:
                    addresses.append({
                        'address': row['כתובת'],
                        'neighborhood': row['שכונה'],
                        'visited': row['ביקרנו'] == 'כן'
                    })
        
        return jsonify(addresses)
        
    except FileNotFoundError:
        return jsonify([])  # אם הקובץ לא קיים, החזר רשימה ריקה
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def mark_visited_handler(app_root_path):
    """מעדכן את סטטוס הביקור של כתובת בשלושת הקבצים"""
    try:
        data = request.get_json()
        address_to_update = data.get('address')
        
        if not address_to_update:
            return jsonify({'success': False, 'message': 'לא סופקה כתובת'}), 400
        
        address_found = False
        files_to_check = [
            'found_addresses.csv',
            'future_use.csv',
            'not_found_addresses.csv'
        ]
        
        # חיפוש ועדכון בכל הקבצים
        for file_name in files_to_check:
            csv_path = os.path.join(app_root_path, 'database', file_name)
            temp_path = csv_path + '.tmp'
            
            if not os.path.exists(csv_path):
                continue
            
            # קריאה ועדכון הקובץ
            with open(csv_path, 'r', encoding='utf-8') as infile, \
                 open(temp_path, 'w', encoding='utf-8', newline='') as outfile:
                
                reader = csv.DictReader(infile)
                fieldnames = reader.fieldnames
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in reader:
                    if row['כתובת'] == address_to_update:
                        row['ביקרנו'] = 'כן'
                        address_found = True
                    writer.writerow(row)
            
            if address_found:
                # החלפת הקובץ המקורי בקובץ המעודכן
                os.replace(temp_path, csv_path)
                break
            else:
                # מחיקת הקובץ הזמני אם הכתובת לא נמצאה בקובץ זה
                os.remove(temp_path)
        
        if address_found:
            return jsonify({'success': True, 'message': 'הביקור עודכן בהצלחה'})
        else:
            return jsonify({'success': False, 'message': 'כתובת לא נמצאה'}), 404
            
    except Exception as e:
        # ניקוי קבצים זמניים במקרה של שגיאה
        for file_name in ['found_addresses.csv.tmp', 'future_use.csv.tmp', 'not_found_addresses.csv.tmp']:
            temp_path = os.path.join(app_root_path, 'database', file_name)
            if os.path.exists(temp_path):
                os.remove(temp_path)
        return jsonify({'success': False, 'message': str(e)}), 500

def toggle_visit_status_handler(app_root_path):
    """מעדכן או מבטל את סטטוס הביקור של כתובת בשלושת הקבצים"""
    try:
        data = request.get_json()
        address_to_update = data.get('address')
        action = data.get('action', 'mark')  # 'mark' או 'unmark'
        
        if not address_to_update:
            return jsonify({'success': False, 'message': 'לא סופקה כתובת'}), 400
        
        address_found = False
        files_to_check = [
            'found_addresses.csv',
            'future_use.csv',
            'not_found_addresses.csv'
        ]
        
        new_status = 'כן' if action == 'mark' else 'לא'
        
        # חיפוש ועדכון בכל הקבצים
        for file_name in files_to_check:
            csv_path = os.path.join(app_root_path, 'database', file_name)
            temp_path = csv_path + '.tmp'
            
            if not os.path.exists(csv_path):
                continue
            
            # קריאה ועדכון הקובץ
            with open(csv_path, 'r', encoding='utf-8') as infile, \
                 open(temp_path, 'w', encoding='utf-8', newline='') as outfile:
                
                reader = csv.DictReader(infile)
                fieldnames = reader.fieldnames
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in reader:
                    if row['כתובת'] == address_to_update:
                        row['ביקרנו'] = new_status
                        address_found = True
                    writer.writerow(row)
            
            if address_found:
                # החלפת הקובץ המקורי בקובץ המעודכן
                os.replace(temp_path, csv_path)
                break
            else:
                # מחיקת הקובץ הזמני אם הכתובת לא נמצאה בקובץ זה
                os.remove(temp_path)
        
        if address_found:
            action_text = 'סומן כביקור' if action == 'mark' else 'בוטל הביקור'
            return jsonify({'success': True, 'message': f'{action_text} בהצלחה'})
        else:
            return jsonify({'success': False, 'message': 'כתובת לא נמצאה'}), 404
            
    except Exception as e:
        # ניקוי קבצים זמניים במקרה של שגיאה
        for file_name in ['found_addresses.csv.tmp', 'future_use.csv.tmp', 'not_found_addresses.csv.tmp']:
            temp_path = os.path.join(app_root_path, 'database', file_name)
            if os.path.exists(temp_path):
                os.remove(temp_path)
        return jsonify({'success': False, 'message': str(e)}), 500

def delete_address_handler(app_root_path):
    """מוחק כתובת מהקבצים הראשיים ומעביר לקובץ deleted_addresses.csv"""
    try:
        data = request.get_json()
        address_to_delete = data.get('address')
        
        if not address_to_delete:
            return jsonify({'success': False, 'message': 'לא סופקה כתובת'}), 400
        
        address_found = False
        deleted_row = None
        
        files_to_check = [
            'found_addresses.csv',
            'future_use.csv', 
            'not_found_addresses.csv'
        ]
        
        # חיפוש ומחיקה מהקבצים הראשיים
        for file_name in files_to_check:
            csv_path = os.path.join(app_root_path, 'database', file_name)
            temp_path = csv_path + '.tmp'
            
            if not os.path.exists(csv_path):
                continue
            
            # קריאה ומחיקה מהקובץ
            with open(csv_path, 'r', encoding='utf-8') as infile, \
                 open(temp_path, 'w', encoding='utf-8', newline='') as outfile:
                
                reader = csv.DictReader(infile)
                fieldnames = reader.fieldnames
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for row in reader:
                    if row['כתובת'] == address_to_delete:
                        deleted_row = row.copy()
                        address_found = True
                        # לא כותבים את השורה - זה המחיקה
                    else:
                        writer.writerow(row)
            
            if address_found:
                # החלפת הקובץ המקורי בקובץ המעודכן
                os.replace(temp_path, csv_path)
                break
            else:
                # מחיקת הקובץ הזמני אם הכתובת לא נמצאה בקובץ זה
                os.remove(temp_path)
        
        if not address_found:
            return jsonify({'success': False, 'message': 'כתובת לא נמצאה'}), 404
        
        # הוספה לקובץ deleted_addresses.csv
        deleted_csv_path = os.path.join(app_root_path, 'database', 'deleted_addresses.csv')
        
        # הוספת תאריך מחיקה
        from datetime import datetime
        deleted_row['תאריך_מחיקה'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # בדיקה אם הקובץ קיים
        file_exists = os.path.exists(deleted_csv_path)
        
        # כתיבה לקובץ המחוקים
        with open(deleted_csv_path, 'a', encoding='utf-8', newline='') as outfile:
            # אם זה קובץ חדש, נוסיף headers
            if not file_exists:
                fieldnames = list(deleted_row.keys())
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()
            else:
                # אם הקובץ קיים, נקרא את ה-headers הקיימים
                with open(deleted_csv_path, 'r', encoding='utf-8') as existing_file:
                    existing_reader = csv.DictReader(existing_file)
                    fieldnames = existing_reader.fieldnames
                    # אם יש עמודות חדשות, נוסיף אותן
                    if 'תאריך_מחיקה' not in fieldnames:
                        fieldnames = list(fieldnames) + ['תאריך_מחיקה']
                        # נכתוב מחדש את הקובץ עם ה-headers החדשים
                        import tempfile
                        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='', delete=False) as temp_file:
                            writer = csv.DictWriter(temp_file, fieldnames=fieldnames)
                            writer.writeheader()
                            
                            # העתקה של כל השורות הקיימות
                            existing_file.seek(0)
                            existing_reader = csv.DictReader(existing_file)
                            for row in existing_reader:
                                row['תאריך_מחיקה'] = row.get('תאריך_מחיקה', '')
                                writer.writerow(row)
                        
                        # החלפת הקובץ
                        os.replace(temp_file.name, deleted_csv_path)
                
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            
            writer.writerow(deleted_row)
        
        return jsonify({'success': True, 'message': 'הכתובת נמחקה בהצלחה'})
        
    except Exception as e:
        # ניקוי קבצים זמניים במקרה של שגיאה
        for file_name in ['found_addresses.csv.tmp', 'future_use.csv.tmp', 'not_found_addresses.csv.tmp']:
            temp_path = os.path.join(app_root_path, 'database', file_name)
            if os.path.exists(temp_path):
                os.remove(temp_path)
        return jsonify({'success': False, 'message': str(e)}), 500
