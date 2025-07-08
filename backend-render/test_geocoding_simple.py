#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
בדיקת רק שירות הגיאוקודינג - ללא חיבור לבסיס נתונים
"""

import os
from dotenv import load_dotenv
import requests
import json

# טען משתני סביבה
load_dotenv()

def test_maps_co_api():
    """בדיקת Maps.co API"""
    print("🔍 בדיקת Maps.co API...")
    
    api_key = os.getenv('MAPS_CO_API_KEY')
    print(f"API Key: {api_key}")
    
    if not api_key:
        print("❌ אין API key")
        return False
    
    try:
        # כתובת מבחן באנגלית
        test_address = "Hebron Road 1, Jerusalem, Israel"
        
        # בדיקת תוקף API key
        url = "https://geocode.maps.co/search"
        params = {
            'q': test_address,
            'api_key': api_key,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'IL'
        }
        
        headers = {
            'User-Agent': 'הנוסע המתמיד/1.0',
            'Accept': 'application/json'
        }
        
        print(f"Testing geocoding for: {test_address}")
        print(f"URL: {url}")
        print(f"Parameters: {params}")
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ תשובה מוצלחת!")
            print(f"📋 תוצאות: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data and len(data) > 0:
                result = data[0]
                lat = result.get('lat')
                lon = result.get('lon')
                print(f"🎯 נמצאו קואורדינטות: {lat}, {lon}")
                
                # בדיקה שהקואורדינטות בישראל
                if lat and lon:
                    lat_f = float(lat)
                    lon_f = float(lon)
                    if 29.5 <= lat_f <= 33.5 and 34.0 <= lon_f <= 36.0:
                        print("✅ הקואורדינטות בישראל")
                        return True
                    else:
                        print("⚠️ הקואורדינטות לא בישראל")
                        return False
            else:
                print("⚠️ לא נמצאו תוצאות")
                return False
                
        elif response.status_code == 401:
            print("❌ API key לא תקין")
            return False
        else:
            print(f"❌ שגיאה: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return False

def test_nominatim_api():
    """בדיקת Nominatim API כגיבוי"""
    print("\n🔍 בדיקת Nominatim API...")
    
    try:
        test_address = "Hebron Road 1, Jerusalem, Israel"
        
        url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': test_address,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'IL',
            'addressdetails': 1
        }
        
        headers = {
            'User-Agent': 'הנוסע המתמיד/1.0 (traveler.app@example.com)',
            'Accept': 'application/json',
            'Accept-Language': 'he,en'
        }
        
        print(f"📍 בדיקת גיאוקודינג עבור: {test_address}")
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ תשובה מוצלחת!")
            print(f"📋 תוצאות: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data and len(data) > 0:
                result = data[0]
                lat = result.get('lat')
                lon = result.get('lon')
                print(f"🎯 נמצאו קואורדינטות: {lat}, {lon}")
                return True
            else:
                print("⚠️ לא נמצאו תוצאות")
                return False
        else:
            print(f"❌ שגיאה: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ שגיאה: {e}")
        return False

if __name__ == "__main__":
    print("🚀 בדיקת שירותי גיאוקודינג")
    print("="*50)
    
    maps_co_result = test_maps_co_api()
    nominatim_result = test_nominatim_api()
    
    print("\n" + "="*50)
    print("📊 סיכום:")
    print(f"Maps.co API: {'✅ עובד' if maps_co_result else '❌ לא עובד'}")
    print(f"Nominatim API: {'✅ עובד' if nominatim_result else '❌ לא עובד'}")
    
    if maps_co_result or nominatim_result:
        print("🎉 לפחות שירות אחד עובד!")
    else:
        print("😞 אף שירות לא עובד")
