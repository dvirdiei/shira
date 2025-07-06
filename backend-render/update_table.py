#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
עדכון מבנה הטבלה ב-Supabase
הוספת עמודות חסרות
"""

import os
from dotenv import load_dotenv

load_dotenv()

def update_table_structure():
    """עדכון מבנה הטבלה בSupabase"""
    try:
        print("🔧 מעדכן מבנה טבלה ב-Supabase...")
        
        # פרטי Supabase
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not url or not key:
            print("❌ משתני סביבה חסרים! בדוק את .env")
            return False
        
        from supabase import create_client, Client
        supabase: Client = create_client(url, key)
        
        # SQL commands להוספת עמודות חסרות
        alter_commands = [
            "ALTER TABLE addresses ADD COLUMN IF NOT EXISTS neighborhood TEXT;",
            "ALTER TABLE addresses ADD COLUMN IF NOT EXISTS visited BOOLEAN DEFAULT FALSE;", 
            "ALTER TABLE addresses ADD COLUMN IF NOT EXISTS source TEXT DEFAULT 'manual';"
        ]
        
        print("📝 מוסיף עמודות חסרות...")
        
        for cmd in alter_commands:
            try:
                # בSupabase Python client, אין דרך ישירה להריץ SQL 
                # אז נשתמש ב-RPC או נודה למשתמש להריץ ידנית
                print(f"💡 הריץ ב-Supabase SQL Editor: {cmd}")
            except Exception as e:
                print(f"⚠️  {cmd} - {e}")
        
        print("\n🎯 הוראות ידניות:")
        print("1. היכנס ל-Supabase Dashboard")
        print("2. לך ל-SQL Editor") 
        print("3. הריץ את הפקודות הבאות:")
        print("---")
        for cmd in alter_commands:
            print(cmd)
        print("---")
        print("4. חזור והרץ את create_sample_data.py")
        
        return True
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return False

if __name__ == "__main__":
    update_table_structure()
