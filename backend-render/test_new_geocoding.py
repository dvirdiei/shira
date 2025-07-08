#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
בדיקת השירות החדש
"""

import sys
import os
sys.path.append('.')

from dotenv import load_dotenv
load_dotenv()

from src.services.geocoding_service import GeocodingService
import json

def test_new_geocoding_service():
    """בדיקת השירות החדש"""
    try:
        print("🔍 בדיקת השירות החדש...")
        
        # צור instance של השירות
        service = GeocodingService()
        
        # בדוק את תוקף ה-API key
        print('\n=== בדיקת תוקף API key ===')
        validation = service.validate_maps_co_api_key()
        print(json.dumps(validation, indent=2, ensure_ascii=False))
        
        # בדוק גיאוקודינג כתובת
        print('\n=== בדיקת גיאוקודינג ===')
        test_addresses = [
            "רחוב יפו 1, ירושלים",
            "דרך חברון 1",
            "Ben Yehuda Street 1, Jerusalem"
        ]
        
        for address in test_addresses:
            print(f"\n🔍 בדיקת כתובת: {address}")
            result = service.geocode_address(address)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        
        return True
        
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return False

if __name__ == "__main__":
    test_new_geocoding_service()
