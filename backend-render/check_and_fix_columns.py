#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
עדכון מבנה טבלה ב-Supabase דרך SQL RPC
"""

import os
from dotenv import load_dotenv

load_dotenv()

def add_columns_via_supabase_client():
    """הוספת עמודות דרך Supabase Client"""
    try:
        print("🔧 מתחבר ל-Supabase להוספת עמודות...")
        
        # פרטי Supabase
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not url or not key:
            print("❌ משתני סביבה חסרים! בדוק את .env")
            return False
        
        from supabase import create_client, Client
        supabase: Client = create_client(url, key)
        
        print("✅ חיבור ל-Supabase הצלח!")
        
        # בואו נבדוק תחילה איזה עמודות יש
        print("\n🔍 בודק מבנה טבלה נוכחי...")
        result = supabase.table('addresses').select("*").limit(1).execute()
        
        if result.data:
            current_columns = list(result.data[0].keys())
            print(f"📋 עמודות נוכחיות: {', '.join(current_columns)}")
            
            # בדיקת עמודות חסרות
            required_columns = ['neighborhood', 'visited', 'source']
            missing_columns = [col for col in required_columns if col not in current_columns]
            
            if missing_columns:
                print(f"❌ עמודות חסרות: {', '.join(missing_columns)}")
                print("\n💡 צריך להוסיף עמודות ידנית ב-Supabase:")
                print("1. היכנס ל-Supabase Dashboard")
                print("2. לך ל-SQL Editor")
                print("3. הרץ את הפקודות הבאות:")
                print("---")
                for col in missing_columns:
                    if col == 'neighborhood':
                        print("ALTER TABLE addresses ADD COLUMN neighborhood TEXT DEFAULT 'לא ידוע';")
                    elif col == 'visited':
                        print("ALTER TABLE addresses ADD COLUMN visited BOOLEAN DEFAULT FALSE;")
                    elif col == 'source':
                        print("ALTER TABLE addresses ADD COLUMN source TEXT DEFAULT 'manual';")
                print("---")
                
                # בינתיים, בואו נעדכן את הנתונים הקיימים לעבוד עם מה שיש
                print("\n🔄 מעדכן handler לעבוד עם העמודות הקיימות...")
                return "manual_sql_needed"
            else:
                print("✅ כל העמודות הנדרשות קיימות!")
                return True
        else:
            print("⚠️  הטבלה ריקה, אי אפשר לבדוק מבנה")
            return False
            
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return False

def update_handler_for_existing_columns():
    """עדכון הקוד לעבוד עם העמודות הקיימות"""
    print("\n🔧 מעדכן את handler לעבוד עם העמודות הקיימות...")
    
    # קריאה לקובץ handler
    handler_file = "PYTHON/supabase_handler.py"
    
    try:
        with open(handler_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # עדכון הפונקציה
        old_format = """                # המרת הנתונים לפורמט שה-Frontend מצפה לו
                formatted_addresses = []
                for addr in result.data:
                    formatted_addr = {
                        'address': addr.get('address', ''),
                        'city': addr.get('city', ''),
                        'neighborhood': addr.get('neighborhood', 'לא ידוע'),
                        'lat': addr.get('latitude'),
                        'lon': addr.get('longitude'), 
                        'visited': addr.get('visited', False),
                        'source': addr.get('source_file', 'unknown'),
                        'id': addr.get('id'),
                        'created_at': addr.get('created_at')
                    }
                    formatted_addresses.append(formatted_addr)"""

        new_format = """                # המרת הנתונים לפורמט שה-Frontend מצפה לו
                formatted_addresses = []
                for addr in result.data:
                    formatted_addr = {
                        'address': addr.get('address', ''),
                        'city': addr.get('city', ''),
                        'neighborhood': addr.get('neighborhood', addr.get('city', 'לא ידוע')),  # אם אין neighborhood, השתמש ב-city
                        'lat': addr.get('latitude'),
                        'lon': addr.get('longitude'), 
                        'visited': addr.get('visited', False),  # ברירת מחדל false אם אין עמודה
                        'source': addr.get('source', addr.get('source_file', 'unknown')),  # נסה source ואז source_file
                        'id': addr.get('id'),
                        'created_at': addr.get('created_at')
                    }
                    formatted_addresses.append(formatted_addr)"""
        
        if old_format in content:
            content = content.replace(old_format, new_format)
            
            with open(handler_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Handler עודכן לעבוד עם העמודות הקיימות")
            return True
        else:
            print("⚠️  לא מצאתי את הקוד לעדכון")
            return False
            
    except Exception as e:
        print(f"❌ שגיאה בעדכון handler: {e}")
        return False

if __name__ == "__main__":
    print("🚀 בודק ומעדכן מבנה טבלת addresses...")
    print("=" * 60)
    
    result = add_columns_via_supabase_client()
    
    if result == "manual_sql_needed":
        print("\n🔄 בינתיים, מעדכן את הקוד לעבוד עם מה שיש...")
        update_handler_for_existing_columns()
        print("\n💡 לאחר הוספת העמודות ב-Supabase, הכל יעבוד מושלם!")
    elif result:
        print("\n✅ הכל תקין!")
    else:
        print("\n❌ יש בעיה. בדוק את השגיאות למעלה.")
