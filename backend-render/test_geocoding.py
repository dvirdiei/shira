#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
בדיקת שירות גיאוקודינג
"""

import sys
import os
sys.path.append('.')

from src.services.geocoding_service import GeocodingService
import json

def test_geocoding_service():
    """בדיקת שירות הגיאוקודינג"""
    try:
        print("🔍 בדיקת שירות הגיאוקודינג...")
        
        # צור instance של השירות
        service = GeocodingService()
        
        # בדוק את סטטוס השירות
        print('\n=== בדיקת סטטוס השירות ===')
        status = service.get_service_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
        
        # בדוק את תוקף ה-API key
        print('\n=== בדיקת תוקף API key ===')
        validation = service.validate_maps_co_api_key()
        print(json.dumps(validation, indent=2, ensure_ascii=False))
        
        # בדוק עם כתובת מבחן
        print('\n=== בדיקת גיאוקודינג עם כתובת מבחן ===')
        test_result = service.test_geocoding_service("דרך חברון 1, ירושלים")
        print(json.dumps(test_result, indent=2, ensure_ascii=False))
        
        # נסה גיאוקודינג כתובת בודדת
        print('\n=== גיאוקודינג כתובת בודדת ===')
        geocode_result = service.geocode_address("רחוב יפו 1, ירושלים")
        print(json.dumps(geocode_result, indent=2, ensure_ascii=False))
        
        return True
        
    except Exception as e:
        print(f"❌ שגיאה בבדיקת השירות: {e}")
        return False

if __name__ == "__main__":
    test_geocoding_service()
