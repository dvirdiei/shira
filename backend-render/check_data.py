#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
בדיקה מהירה של מה יש בSupabase
"""

def check_supabase_data():
    """בדיקת הנתונים בSupabase"""
    try:
        print("🔍 בודק מה יש בSupabase...")
        
        # פרטי Supabase
        url = "https://ivhmndizihxskjhlqaki.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml2aG1uZGl6aWh4c2tqaGxxYWtpIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1MTgzMTQ1MiwiZXhwIjoyMDY3NDA3NDUyfQ.WqHjgDitX_cgR_s36LoXHtps34l2Y2_3-5weACVFcus"
        
        from supabase import create_client, Client
        supabase: Client = create_client(url, key)
        
        # בדיקת כמות הנתונים
        result = supabase.table('addresses').select("*").execute()
        
        if result.data:
            print(f"📊 נמצאו {len(result.data)} כתובות בSupabase:")
            for i, addr in enumerate(result.data[:5]):  # רק 5 הראשונות
                coords = ""
                if addr.get('latitude') and addr.get('longitude'):
                    coords = f" ({addr['latitude']}, {addr['longitude']})"
                print(f"  {i+1}. {addr.get('address', 'N/A')}, {addr.get('city', 'N/A')}{coords}")
            
            if len(result.data) > 5:
                print(f"  ... ועוד {len(result.data) - 5} כתובות")
        else:
            print("❌ אין נתונים בSupabase!")
            print("💡 צריך להריץ מיגרציה")
        
        return len(result.data) if result.data else 0
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return 0

if __name__ == "__main__":
    count = check_supabase_data()
    if count == 0:
        print("\n🔄 להעברת נתונים:")
        print("python create_sample_data.py  # נתוני דוגמה")
        print("או")
        print("python migrate_to_supabase.py  # מCSV")
