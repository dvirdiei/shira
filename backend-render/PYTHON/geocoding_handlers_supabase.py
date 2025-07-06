# -*- coding: utf-8 -*-
"""
Geocoding Handlers for Supabase - הנוסע המתמיד
טיפול בגיאוקודינג עם Maps.co API ועדכון Supabase
"""

import os
import requests
import time
import logging
from typing import List, Dict, Tuple, Optional

from .supabase_handler import get_supabase_handler

logger = logging.getLogger(__name__)

class GeocodingService:
    """שירות גיאוקודינג עם Maps.co"""
    
    def __init__(self):
        self.api_key = os.getenv('MAPS_CO_API_KEY')
        if not self.api_key:
            logger.warning("⚠️  לא נמצא מפתח API של Maps.co - גיאוקודינג לא יעבוד")
        
        self.base_url = "https://geocode.maps.co/search"
        self.session = requests.Session()
        
        # הגדרות headers
        self.session.headers.update({
            'User-Agent': 'hanose-mitamid/1.0 (traveler-app)',
            'Accept': 'application/json'
        })
    
    def geocode_address(self, address: str, city: str = "") -> Optional[Tuple[float, float]]:
        """גיאוקודינג כתובת בודדת"""
        if not self.api_key:
            logger.error("חסר מפתח API של Maps.co")
            return None
        
        try:
            # בניית מחרוזת החיפוש
            search_query = f"{address}"
            if city:
                search_query += f", {city}"
            search_query += ", Israel"
            
            # פרמטרים לבקשה
            params = {
                'q': search_query,
                'api_key': self.api_key,
                'limit': 1,
                'format': 'json'
            }
            
            logger.info(f"מחפש: {search_query}")
            
            # שליחת בקשה
            response = self.session.get(self.base_url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data and len(data) > 0:
                    result = data[0]
                    lat = float(result.get('lat', 0))
                    lon = float(result.get('lon', 0))
                    
                    # בדיקה שהקואורדינטות בישראל (בערך)
                    if 29.0 <= lat <= 34.0 and 34.0 <= lon <= 36.0:
                        logger.info(f"✅ נמצאו קואורדינטות: {lat}, {lon}")
                        return (lat, lon)
                    else:
                        logger.warning(f"⚠️  קואורדינטות מחוץ לישראל: {lat}, {lon}")
                        return None
                else:
                    logger.warning(f"❌ לא נמצאו תוצאות עבור: {search_query}")
                    return None
            
            elif response.status_code == 429:
                logger.warning("⏳ הגעת למגבלת בקשות - ממתין...")
                time.sleep(5)
                return None
            
            elif response.status_code == 401:
                logger.error("❌ מפתח API לא תקין")
                return None
            
            else:
                logger.error(f"❌ שגיאה HTTP {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("⏰ timeout בבקשת גיאוקודינג")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ שגיאת רשת: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ שגיאה בגיאוקודינג: {e}")
            return None

def geocode_addresses_batch(addresses: List[Dict], delay: float = 1.0) -> Dict:
    """גיאוקודינג קבוצת כתובות"""
    geocoding_service = GeocodingService()
    handler = get_supabase_handler()
    
    results = {
        'success_count': 0,
        'failed_count': 0,
        'errors': []
    }
    
    total_addresses = len(addresses)
    logger.info(f"🚀 מתחיל גיאוקודינג של {total_addresses} כתובות")
    
    for i, address_data in enumerate(addresses):
        try:
            address_id = address_data.get('id')
            address = address_data.get('address', '')
            city = address_data.get('city', '')
            
            logger.info(f"[{i+1}/{total_addresses}] מעבד: {address}")
            
            # גיאוקודינג
            coordinates = geocoding_service.geocode_address(address, city)
            
            if coordinates:
                lat, lon = coordinates
                
                # עדכון בבסיס הנתונים
                if handler.update_address_coordinates(address_id, lat, lon):
                    results['success_count'] += 1
                    logger.info(f"✅ עודכן: {address} -> {lat}, {lon}")
                else:
                    results['failed_count'] += 1
                    error_msg = f"לא ניתן לעדכן בסיס נתונים עבור: {address}"
                    results['errors'].append(error_msg)
                    logger.error(error_msg)
            else:
                results['failed_count'] += 1
                error_msg = f"לא נמצאו קואורדינטות עבור: {address}"
                results['errors'].append(error_msg)
                logger.warning(error_msg)
            
            # המתנה בין בקשות
            if i < total_addresses - 1:  # לא ממתין אחרי האחרונה
                time.sleep(delay)
                
        except Exception as e:
            results['failed_count'] += 1
            error_msg = f"שגיאה בעיבוד {address}: {e}"
            results['errors'].append(error_msg)
            logger.error(error_msg)
    
    # סיכום
    logger.info(f"🏁 גיאוקודינג הושלם:")
    logger.info(f"   ✅ הצליח: {results['success_count']}")
    logger.info(f"   ❌ נכשל: {results['failed_count']}")
    
    return results

def test_geocoding_service() -> Dict:
    """בדיקת שירות הגיאוקודינג"""
    try:
        geocoding_service = GeocodingService()
        
        # בדיקה עם כתובת מוכרת
        test_address = "דיזנגוף 99, תל אביב"
        logger.info(f"בוחן גיאוקודינג עם: {test_address}")
        
        coordinates = geocoding_service.geocode_address(test_address)
        
        if coordinates:
            lat, lon = coordinates
            return {
                'success': True,
                'message': f'גיאוקודינג עובד ✅',
                'test_address': test_address,
                'coordinates': {'lat': lat, 'lon': lon}
            }
        else:
            return {
                'success': False,
                'error': 'לא נמצאו קואורדינטות לכתובת הבדיקה',
                'test_address': test_address
            }
            
    except Exception as e:
        logger.error(f"שגיאה בבדיקת גיאוקודינג: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def get_geocoding_statistics() -> Dict:
    """סטטיסטיקות גיאוקודינג"""
    try:
        handler = get_supabase_handler()
        stats = handler.get_statistics()
        
        # הוספת מידע על שירות הגיאוקודינג
        api_key_available = bool(os.getenv('MAPS_CO_API_KEY'))
        
        return {
            'total_addresses': stats['total_addresses'],
            'geocoded_addresses': stats['geocoded_addresses'],
            'pending_geocoding': stats['pending_geocoding'],
            'geocoded_percentage': stats['geocoded_percentage'],
            'api_key_configured': api_key_available,
            'geocoding_service': 'Maps.co' if api_key_available else 'לא זמין'
        }
        
    except Exception as e:
        logger.error(f"שגיאה בסטטיסטיקות גיאוקודינג: {e}")
        return {
            'total_addresses': 0,
            'geocoded_addresses': 0,
            'pending_geocoding': 0,
            'geocoded_percentage': 0,
            'api_key_configured': False,
            'geocoding_service': 'שגיאה'
        }
