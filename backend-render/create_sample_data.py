#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
יצירת נתוני דוגמה ב-Supabase
"""

import os
from dotenv import load_dotenv

load_dotenv()

def create_sample_data():
    """יצירת נתוני דוגמה בSupabase"""
    try:
        print("🚀 יוצר נתוני דוגמה ב-Supabase...")
        
        # פרטי Supabase
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not url or not key:
            print("❌ משתני סביבה חסרים! בדוק את .env")
            return False
        
        from supabase import create_client, Client
        supabase: Client = create_client(url, key)
        
        # נתוני דוגמה - מותאמים למבנה הטבלה הקיים
        sample_addresses = [
            {
                'address': 'הרב ריינס 10, ירושלים',
                'city': 'ירושלים',
                'latitude': 31.7903429,
                'longitude': 35.1940735,
                'source_file': 'sample_data'
            },
            {
                'address': 'חירם 5, ירושלים',
                'city': 'ירושלים', 
                'latitude': 31.7929006,
                'longitude': 35.2077533,
                'source_file': 'sample_data'
            },
            {
                'address': 'יפו 234, ירושלים',
                'city': 'ירושלים',
                'latitude': 31.7857,
                'longitude': 35.2007,
                'source_file': 'sample_data'
            },
            {
                'address': 'הנביאים 58, ירושלים',
                'city': 'ירושלים',
                'latitude': 31.7908,
                'longitude': 35.2072,
                'source_file': 'sample_data'
            },
            {
                'address': 'רחוב דמוי ללא קואורדינטות',
                'city': 'ירושלים',
                'latitude': None,
                'longitude': None,
                'source_file': 'sample_data'
            }
        ]
        
        # בדיקה אם הטבלה קיימת וריקה
        result = supabase.table('addresses').select("*").execute()
        
        if result.data and len(result.data) > 0:
            print(f"⚠️  יש כבר {len(result.data)} כתובות. לא נוסיף דוגמאות נוספות.")
            return True
        
        # הכנסת הנתונים
        for addr in sample_addresses:
            try:
                supabase.table('addresses').insert(addr).execute()
                print(f"✅ נוסף: {addr['address']}")
            except Exception as e:
                print(f"❌ שגיאה בהוספת {addr['address']}: {e}")
        
        # בדיקה סופית
        result = supabase.table('addresses').select("*").execute()
        print(f"🎉 נוצרו {len(result.data)} כתובות דוגמה!")
        
        return True
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return False

if __name__ == "__main__":
    success = create_sample_data()
    if not success:
        print("\n💡 עצות לפתרון בעיות:")
        print("1. בדוק שהקובץ .env מכיל את פרטי Supabase")
        print("2. בדוק שהטבלה 'addresses' קיימת ב-Supabase")
        print("3. הרץ: pip install supabase")
