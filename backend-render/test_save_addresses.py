"""
🧪 בדיקת שמירת כתובות בבסיס הנתונים
"""

import os
from src.database.connection import get_database_client
from src.services.geocoding_service import GeocodingService

def test_save_addresses():
    """בדיקת שמירת כתובות"""
    # כתובות לבדיקה
    test_addresses = [
        "מרקו ברוך 11, ירושלים",
        "רחוב הרצל 15, תל אביב",
        "כתובת לא קיימת 999, עיר לא קיימת"
    ]
    
    print("🧪 בדיקת שמירת כתובות...")
    
    # יצירת שירות גיאוקודינג
    service = GeocodingService()
    
    # עיבוד הכתובות
    result = service.batch_geocode_advanced(test_addresses)
    
    print(f"📊 תוצאות:")
    print(f"✅ הצלחה: {result.get('successful', 0)}")
    print(f"💾 נשמרו: {result.get('saved', 0)}")
    print(f"❌ כשלון: {result.get('failed', 0)}")
    
    if result.get('failed_addresses'):
        print(f"📝 כתובות שנכשלו: {result['failed_addresses']}")
    
    # בדיקת הטבלאות
    client = get_database_client()
    
    print("\n🗂️ בדיקת טבלאות:")
    
    # בדיקת טבלת addresses
    addresses_result = client.table('addresses').select('*').execute()
    print(f"📋 טבלת addresses: {len(addresses_result.data)} רשומות")
    
    # בדיקת טבלת addresses_missing_coordinates
    missing_result = client.table('addresses_missing_coordinates').select('*').execute()
    print(f"📋 טבלת missing_coordinates: {len(missing_result.data)} רשומות")
    
    # הצגת הנתונים
    print("\n📄 כתובות עם קואורדינטות:")
    for addr in addresses_result.data:
        print(f"  • {addr['address']} ({addr['lat']}, {addr['lon']})")
    
    print("\n📄 כתובות ללא קואורדינטות:")
    for addr in missing_result.data:
        print(f"  • {addr['address']} - {addr['reason']}")

if __name__ == "__main__":
    test_save_addresses()
