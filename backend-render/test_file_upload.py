#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
בדיקת העלאת קובץ כתובות
"""

import sys
import os
from dotenv import load_dotenv

# טען משתני סביבה
load_dotenv()

sys.path.append('.')

from src.services.geocoding_service import GeocodingService
import json

def test_file_upload():
    """בדיקת עיבוד קובץ כתובות"""
    try:
        # קרא את קובץ הבדיקה
        with open('test_addresses.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # חלק לכתובות
        addresses = [line.strip() for line in content.split('\n') if line.strip()]
        print(f"נמצאו {len(addresses)} כתובות:")
        for i, addr in enumerate(addresses, 1):
            print(f"  {i}. {addr}")
        
        # צור שירות גיאוקודינג
        service = GeocodingService()
        
        print("\n🚀 מתחיל גיאוקודינג...")
        
        # בצע גיאוקודינג עם הפונקציה המתקדמת
        result = service.batch_geocode_advanced(addresses)
        
        print("\n📊 תוצאות:")
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return result
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return None

if __name__ == "__main__":
    test_file_upload()
