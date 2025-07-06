#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration script from CSV to Supabase for הנוסע המתמיד
מיגרציה ישירה עם הפרטים המוכנים
"""

import os
import sys
import pandas as pd
import logging
from typing import List, Dict
from datetime import datetime

# הוספת נתיב לחיפוש מודולים
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# הגדרת לוגינג
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def migrate_to_supabase_direct():
    """מיגרציה ישירה עם פרטי Supabase"""
    try:
        logger.info("🚀 מתחיל מיגרציה ל-Supabase...")
        
        # פרטי Supabase ישירות
        url = "https://ivhmndizihxskjhlqaki.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml2aG1uZGl6aWh4c2tqaGxxYWtpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTgzMTQ1MiwiZXhwIjoyMDY3NDA3NDUyfQ.WqHjgDitX_cgR_s36LoXHtps34l2Y2_3-5weACVFcus"
        
        # 1. חיבור לSupabase
        from supabase import create_client, Client
        supabase: Client = create_client(url, key)
        logger.info("✅ התחבר לSupabase")
        
        # 2. קריאת נתונים מ-CSV
        logger.info("📖 קורא נתונים מ-CSV...")
        addresses = read_csv_files()
        
        if not addresses:
            logger.error("❌ לא נמצאו כתובות לעיפו")
            return False
        
        # 3. בדיקה אם כבר יש נתונים
        result = supabase.table('addresses').select("*").limit(1).execute()
        if result.data:
            logger.warning(f"⚠️  נמצאו {len(result.data)} כתובות קיימות")
            response = input("האם למחוק ולהתחיל מחדש? (y/N): ")
            if response.lower() == 'y':
                delete_result = supabase.table('addresses').delete().neq('id', 0).execute()
                logger.info("🗑️  נתונים קיימים נמחקו")
            else:
                logger.info("❌ ביטול מיגרציה")
                return False
        
        # 4. העברת נתונים בקבוצות
        batch_size = 50  # קטן יותר לSupabase
        total_inserted = 0
        
        for i in range(0, len(addresses), batch_size):
            batch = addresses[i:i + batch_size]
            logger.info(f"מעביר קבוצה {i//batch_size + 1}: כתובות {i+1}-{min(i+batch_size, len(addresses))}")
            
            try:
                insert_result = supabase.table('addresses').insert(batch).execute()
                if insert_result.data:
                    total_inserted += len(insert_result.data)
                    logger.info(f"✅ הועברו {len(insert_result.data)} כתובות")
                else:
                    logger.error(f"❌ שגיאה בהעברת קבוצה {i//batch_size + 1}")
            except Exception as e:
                logger.error(f"❌ שגיאה בקבוצה {i//batch_size + 1}: {e}")
        
        # 5. סיכום
        logger.info(f"✅ מיגרציה הושלמה!")
        logger.info(f"📊 הועברו {total_inserted} כתובות מתוך {len(addresses)}")
        
        # 6. סטטיסטיקות
        final_result = supabase.table('addresses').select("*").execute()
        logger.info(f"📈 סה\"כ כתובות בSupabase: {len(final_result.data) if final_result.data else 0}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ שגיאה במיגרציה: {e}")
        return False

def read_csv_files() -> List[Dict]:
    """קריאת כל קבצי ה-CSV"""
    database_dir = os.path.join(os.path.dirname(__file__), 'database')
    all_addresses = []
    
    csv_files = [
        'addresses_cleaned.csv',
        'addresses_geocoded.csv',
        'addresses.csv'  # בסיסי
    ]
    
    for csv_file in csv_files:
        file_path = os.path.join(database_dir, csv_file)
        
        if os.path.exists(file_path):
            try:
                logger.info(f"קורא קובץ: {csv_file}")
                df = pd.read_csv(file_path, encoding='utf-8')
                
                # המרה לרשימת dictionaries
                for _, row in df.iterrows():
                    address_data = {
                        'address': str(row.get('address', '')).strip(),
                        'city': str(row.get('city', '')).strip(),
                        'latitude': row.get('latitude') if pd.notna(row.get('latitude')) else None,
                        'longitude': row.get('longitude') if pd.notna(row.get('longitude')) else None,
                        'source_file': csv_file,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    # הוספה רק אם יש כתובת
                    if address_data['address'] and address_data['address'] != 'nan':
                        all_addresses.append(address_data)
                
                logger.info(f"נמצאו {len(df)} כתובות ב-{csv_file}")
                
            except Exception as e:
                logger.error(f"שגיאה בקריאת {csv_file}: {e}")
        else:
            logger.warning(f"קובץ לא נמצא: {csv_file}")
    
    # הסרת כפילויות
    unique_addresses = []
    seen_addresses = set()
    
    for addr in all_addresses:
        # יצירת מפתח ייחודי
        key = f"{addr['address'].lower()}_{addr['city'].lower()}"
        
        if key not in seen_addresses:
            seen_addresses.add(key)
            unique_addresses.append(addr)
    
    logger.info(f"סה\"כ כתובות ייחודיות: {len(unique_addresses)}")
    return unique_addresses

def migrate_to_supabase():
    """מיגרציה עיקרית ל-Supabase"""
    try:
        logger.info("🚀 מתחיל מיגרציה ל-Supabase...")
        
        # 1. בדיקת חיבור
        handler = get_supabase_handler()
        if not handler.test_connection():
            logger.error("❌ לא ניתן להתחבר ל-Supabase")
            return False
        
        # 2. קריאת נתונים מ-CSV
        logger.info("📖 קורא נתונים מ-CSV...")
        addresses = read_csv_files()
        
        if not addresses:
            logger.error("❌ לא נמצאו כתובות לעיפו")
            return False
        
        # 3. בדיקה אם כבר יש נתונים
        existing_addresses = handler.get_all_addresses()
        if existing_addresses:
            logger.warning(f"⚠️  נמצאו {len(existing_addresses)} כתובות קיימות")
            response = input("האם למחוק ולהתחיל מחדש? (y/N): ")
            if response.lower() == 'y':
                handler.delete_all_addresses()
                logger.info("🗑️  נתונים קיימים נמחקו")
            else:
                logger.info("❌ ביטול מיגרציה")
                return False
        
        # 4. העברת נתונים בקבוצות
        batch_size = 100
        total_inserted = 0
        
        for i in range(0, len(addresses), batch_size):
            batch = addresses[i:i + batch_size]
            logger.info(f"מעביר קבוצה {i//batch_size + 1}: כתובות {i+1}-{min(i+batch_size, len(addresses))}")
            
            if handler.insert_addresses_batch(batch):
                total_inserted += len(batch)
            else:
                logger.error(f"❌ שגיאה בהעברת קבוצה {i//batch_size + 1}")
        
        # 5. סיכום
        logger.info(f"✅ מיגרציה הושלמה!")
        logger.info(f"📊 הועברו {total_inserted} כתובות מתוך {len(addresses)}")
        
        # 6. סטטיסטיקות
        stats = handler.get_statistics()
        logger.info(f"📈 סטטיסטיקות סופיות: {stats}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ שגיאה במיגרציה: {e}")
        return False

def verify_migration():
    """אימות שהמיגרציה הצליחה"""
    try:
        logger.info("🔍 מאמת מיגרציה...")
        
        handler = get_supabase_handler()
        stats = handler.get_statistics()
        
        print("\n" + "="*50)
        print("📊 סיכום מיגרציה")
        print("="*50)
        print(f"📍 סה\"כ כתובות: {stats['total_addresses']}")
        print(f"🌍 כתובות עם קואורדינטות: {stats['geocoded_addresses']}")
        print(f"⏳ כתובות ממתינות לגיאוקודינג: {stats['pending_geocoding']}")
        print(f"📊 אחוז גיאוקודינג: {stats['geocoded_percentage']}%")
        print("="*50)
        
        if stats['total_addresses'] > 0:
            print("✅ מיגרציה הושלמה בהצלחה!")
            return True
        else:
            print("❌ לא נמצאו נתונים אחרי המיגרציה")
            return False
            
    except Exception as e:
        logger.error(f"❌ שגיאה באימות: {e}")
        return False

if __name__ == "__main__":
    print("🚀 מיגרציה ל-Supabase - הנוסע המתמיד")
    print("="*50)
    
    # הרצת מיגרציה
    if migrate_to_supabase_direct():
        print("✅ המיגרציה הושלמה בהצלחה!")
    else:
        print("❌ המיגרציה נכשלה")
