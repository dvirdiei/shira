import os

# הגדרת ישירה של משתני סביבה
os.environ['SUPABASE_URL'] = 'https://ivhmndizihxskjhlqaki.supabase.co'
os.environ['SUPABASE_SERVICE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml2aG1uZGl6aWh4c2tqaGxxYWtpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTgzMTQ1MiwiZXhwIjoyMDY3NDA3NDUyfQ.Lv_onHITgEm0PpxVNPv9VFXjXpV7_ek2mqwGdRnr-vU'

print("🔍 בודק משתני סביבה...")
url = os.environ['SUPABASE_URL']
key = os.environ['SUPABASE_SERVICE_KEY']

print(f"SUPABASE_URL: {url}")
print(f"SUPABASE_SERVICE_KEY: ✅ קיים")

# בדיקת חיבור
try:
    print("\n🚀 מתחבר ל-Supabase...")
    from supabase import create_client
    
    supabase = create_client(url, key)
    print("✅ יצירת client הצליחה")
    
    # בדיקת חיבור בסיסי
    print("\n🔍 בודק חיבור...")
    
    # נסה לקרוא מטבלת addresses
    try:
        result = supabase.table('addresses').select("*").limit(1).execute()
        print("✅ חיבור ל-Supabase הצליח!")
        print(f"📊 נמצאו {len(result.data)} כתובות")
        
    except Exception as e:
        if "relation" in str(e) and "does not exist" in str(e):
            print("⚠️  חיבור תקין, אבל טבלת addresses לא קיימת")
            print("💡 צריך ליצור את הטבלאות")
        else:
            print(f"❌ שגיאה בחיבור: {e}")
            
except Exception as e:
    print(f"❌ שגיאה ביצירת client: {e}")
    
print("\n" + "="*50)
print("🎯 השלב הבא:")
print("1. לך ל-Supabase Dashboard: https://app.supabase.com")
print("2. בחר פרויקט: shira")
print("3. SQL Editor -> הכנס את הקוד מקובץ supabase_setup.sql")
print("4. לחץ RUN")
print("="*50)
