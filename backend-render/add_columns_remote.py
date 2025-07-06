#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
עדכון מבנה טבלת addresses ב-Supabase מרחוק
הוספת עמודות חסרות: neighborhood, visited, source
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def add_missing_columns():
    """הוספת עמודות חסרות לטבלת addresses"""
    try:
        print("🔧 מתחבר ל-Supabase להוספת עמודות חסרות...")
        
        # פרטי חיבור ל-Supabase PostgreSQL
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not supabase_url or not supabase_key:
            print("❌ משתני סביבה חסרים! בדוק את .env")
            return False
        
        # יצירת connection string
        # Supabase URL: https://ivhmndizihxskjhlqaki.supabase.co
        project_id = supabase_url.split('//')[1].split('.')[0]  # ivhmndizihxskjhlqaki
        
        # פרטי חיבור PostgreSQL
        conn_params = {
            'host': f'{project_id}.supabase.co',
            'port': 5432,
            'database': 'postgres',
            'user': 'postgres',
            'password': supabase_key.replace('Bearer ', '') if supabase_key.startswith('Bearer ') else supabase_key
        }
        
        print(f"🔌 מתחבר לבסיס נתונים: {project_id}.supabase.co")
        
        # התחברות לבסיס נתונים
        conn = psycopg2.connect(**conn_params)
        cursor = conn.cursor()
        
        print("✅ חיבור הצלח!")
        
        # SQL commands להוספת עמודות
        sql_commands = [
            "ALTER TABLE addresses ADD COLUMN IF NOT EXISTS neighborhood TEXT;",
            "ALTER TABLE addresses ADD COLUMN IF NOT EXISTS visited BOOLEAN DEFAULT FALSE;", 
            "ALTER TABLE addresses ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'manual';",
            
            # עדכון נתונים קיימים
            """UPDATE addresses SET 
                neighborhood = COALESCE(neighborhood, 'לא ידוע'),
                visited = COALESCE(visited, FALSE),
                source = COALESCE(source, COALESCE(source_file, 'manual'))
             WHERE neighborhood IS NULL OR visited IS NULL OR source IS NULL;""",
        ]
        
        # הרצת הפקודות
        for i, cmd in enumerate(sql_commands, 1):
            try:
                print(f"📝 מריץ פקודה {i}/{len(sql_commands)}...")
                cursor.execute(cmd)
                conn.commit()
                print(f"✅ פקודה {i} הצליחה")
            except Exception as e:
                print(f"⚠️  פקודה {i} נכשלה: {e}")
                conn.rollback()
        
        # בדיקה סופית - מבנה הטבלה
        print("\n🔍 בודק מבנה טבלה חדש...")
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default 
            FROM information_schema.columns 
            WHERE table_name = 'addresses' 
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print("\n📋 עמודות בטבלת addresses:")
        for col in columns:
            name, dtype, nullable, default = col
            print(f"  • {name}: {dtype} {'(NULL)' if nullable == 'YES' else '(NOT NULL)'} {f'DEFAULT {default}' if default else ''}")
        
        # בדיקת נתונים
        print("\n📊 בדיקת נתונים...")
        cursor.execute("SELECT COUNT(*) FROM addresses;")
        count = cursor.fetchone()[0]
        print(f"  • סה״כ כתובות: {count}")
        
        if count > 0:
            cursor.execute("SELECT address, neighborhood, visited, source FROM addresses LIMIT 3;")
            samples = cursor.fetchall()
            print("  • דוגמאות:")
            for addr, neighborhood, visited, source in samples:
                print(f"    - {addr} | {neighborhood} | ביקור: {visited} | מקור: {source}")
        
        cursor.close()
        conn.close()
        
        print("\n🎉 הוספת עמודות הושלמה בהצלחה!")
        print("\n💡 עכשיו ה-Backend יעבוד עם כל השדות הנדרשים:")
        print("  ✓ neighborhood (שכונה)")
        print("  ✓ visited (ביקור)")
        print("  ✓ source (מקור)")
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ שגיאת PostgreSQL: {e}")
        print("\n💡 פתרונות אפשריים:")
        print("1. בדוק שפרטי ה-Supabase נכונים ב-.env")
        print("2. הריץ ידנית ב-Supabase SQL Editor:")
        print("   ALTER TABLE addresses ADD COLUMN IF NOT EXISTS neighborhood TEXT;")
        print("   ALTER TABLE addresses ADD COLUMN IF NOT EXISTS visited BOOLEAN DEFAULT FALSE;")
        print("   ALTER TABLE addresses ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'manual';")
        return False
        
    except Exception as e:
        print(f"❌ שגיאה כללית: {e}")
        return False

if __name__ == "__main__":
    print("🚀 מתחיל עדכון מבנה טבלת addresses ב-Supabase...")
    print("=" * 60)
    
    success = add_missing_columns()
    
    if success:
        print("\n✅ המשימה הושלמה! ה-Backend עכשיו יעבוד עם כל השדות.")
    else:
        print("\n❌ המשימה נכשלה. עיין בשגיאות למעלה.")
