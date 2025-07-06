# -*- coding: utf-8 -*-
"""
בדיקת חיבור ל-Supabase עבור שירה פרויקט
"""
import os
import sys
from dotenv import load_dotenv

# טעינת משתני סביבה
load_dotenv()

# בדיקת משתני סביבה
print("🔍 בודק משתני סביבה...")
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')

print(f"SUPABASE_URL: {url}")
print(f"SUPABASE_SERVICE_KEY: {'✅ קיים' if key else '❌ חסר'}")

if not url or not key:
    print("❌ חסרים פרטי Supabase")
    sys.exit(1)

# בדיקת חיבור
try:
    print("\n🚀 מתחבר ל-Supabase...")
    from supabase import create_client
    
    supabase = create_client(url, key)
    print("✅ יצירת client הצליחה")
    
    # בדיקת חיבור בסיסי
    print("\n🔍 בודק חיבור...")
    
    # נסה לקרוא מטבלת addresses (גם אם היא לא קיימת)
    try:
        result = supabase.table('addresses').select("*").limit(1).execute()
        print("✅ חיבור ל-Supabase הצליח!")
        print(f"📊 נמצאו {len(result.data)} כתובות")
        
    except Exception as e:
        if "relation" in str(e) and "does not exist" in str(e):
            print("⚠️  חיבור תקין, אבל טבלת addresses לא קיימת")
            print("💡 צריך ליצור את הטבלאות - ראה הוראות למטה")
        else:
            print(f"❌ שגיאה בחיבור: {e}")
            
except Exception as e:
    print(f"❌ שגיאה ביצירת client: {e}")
    
print("\n" + "="*50)
print("🎯 השלב הבא:")
print("1. לך ל-Supabase Dashboard")
print("2. SQL Editor")
print("3. הכנס את הקוד מקובץ supabase_setup.sql")
print("4. לחץ RUN")
print("="*50)
