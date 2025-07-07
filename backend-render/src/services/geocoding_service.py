# -*- coding: utf-8 -*-
"""
🗺️ Geocoding Service - הנוסע המתמיד
שירות גיאוקודינג - המרת כתובות לקואורדינטות
"""

import logging
import requests
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime

from ..database.queries import AddressQueries
from ..database.models import Address, AddressValidator, AddressFormatter
from ..utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

class GeocodingService:
    """שירות גיאוקודינג"""
    
    def __init__(self):
        """אתחול השירות"""
        self.queries = AddressQueries()
        self.validator = AddressValidator()
        self.formatter = AddressFormatter()
        self.rate_limiter = RateLimiter(max_requests=10, time_window=60)  # 10 בקשות לדקה
    
    def batch_geocode(self, addresses: List[str]) -> Dict:
        """הוספת כתובות בבת אחת עם גיאוקודינג"""
        try:
            results = {
                'success': True,
                'added': [],
                'failed': [],
                'total': len(addresses),
                'summary': {
                    'total_addresses': len(addresses),
                    'successfully_added': 0,
                    'failed_to_add': 0,
                    'geocoded': 0,
                    'not_geocoded': 0
                }
            }
            
            for address_str in addresses:
                try:
                    # נקה את הכתובת
                    clean_address = address_str.strip()
                    if not clean_address:
                        continue
                    
                    # בדוק אם הכתובת כבר קיימת
                    if self.queries.address_exists(clean_address):
                        results['failed'].append({
                            'address': clean_address,
                            'error': 'כתובת כבר קיימת'
                        })
                        results['summary']['failed_to_add'] += 1
                        continue
                    
                    # בצע גיאוקודינג
                    latitude, longitude = self.geocode_address(clean_address)
                    
                    # יצור אובייקט כתובת
                    address_data = {
                        'address': clean_address,
                        'city': self._extract_city(clean_address),
                        'neighborhood': self._extract_neighborhood(clean_address),
                        'latitude': latitude,
                        'longitude': longitude,
                        'visited': False,
                        'source': 'batch_geocode',
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    }
                    
                    # הוסף לבסיס הנתונים
                    result = self.queries.insert_address(address_data)
                    
                    if result:
                        results['added'].append({
                            'address': clean_address,
                            'latitude': latitude,
                            'longitude': longitude,
                            'geocoded': latitude is not None and longitude is not None
                        })
                        results['summary']['successfully_added'] += 1
                        
                        if latitude and longitude:
                            results['summary']['geocoded'] += 1
                        else:
                            results['summary']['not_geocoded'] += 1
                    else:
                        results['failed'].append({
                            'address': clean_address,
                            'error': 'לא ניתן להוסיף לבסיס הנתונים'
                        })
                        results['summary']['failed_to_add'] += 1
                
                except Exception as e:
                    logger.error(f"שגיאה בעיבוד כתובת {address_str}: {e}")
                    results['failed'].append({
                        'address': address_str,
                        'error': str(e)
                    })
                    results['summary']['failed_to_add'] += 1
            
            return results
            
        except Exception as e:
            logger.error(f"שגיאה בגיאוקודינג אצווה: {e}")
            return {
                'success': False,
                'error': str(e),
                'added': [],
                'failed': []
            }
    
    def geocode_address(self, address: str) -> Tuple[Optional[float], Optional[float]]:
        """גיאוקודינג כתובת בודדת"""
        try:
            # חכה לפי Rate Limiter
            if not self.rate_limiter.can_make_request():
                time.sleep(1)
            
            # נקה את הכתובת
            clean_address = self._clean_address(address)
            
            # בצע גיאוקודינג עם Nominatim API
            latitude, longitude = self._geocode_with_nominatim(clean_address)
            
            if latitude and longitude:
                return latitude, longitude
            
            # אם לא הצליח, נסה עם Google Maps API (אם זמין)
            # latitude, longitude = self._geocode_with_google(clean_address)
            
            return None, None
            
        except Exception as e:
            logger.error(f"שגיאה בגיאוקודינג כתובת {address}: {e}")
            return None, None
    
    def retry_geocoding(self) -> Dict:
        """ניסיון חוזר לגיאוקודינג כתובות בלי קואורדינטות"""
        try:
            # קבל כתובות בלי קואורדינטות
            addresses = self.queries.get_missing_coordinates()
            
            if not addresses:
                return {
                    'success': True,
                    'message': 'כל הכתובות כבר עם קואורדינטות',
                    'updated': 0
                }
            
            updated_count = 0
            
            for address in addresses:
                try:
                    # בצע גיאוקודינג
                    latitude, longitude = self.geocode_address(address['address'])
                    
                    if latitude and longitude:
                        # עדכן בבסיס הנתונים
                        success = self.queries.update_coordinates(
                            address['id'], 
                            latitude, 
                            longitude
                        )
                        
                        if success:
                            updated_count += 1
                            logger.info(f"עודכנו קואורדינטות לכתובת: {address['address']}")
                    
                    # המתן קצת בין בקשות
                    time.sleep(0.5)
                    
                except Exception as e:
                    logger.error(f"שגיאה בעדכון קואורדינטות לכתובת {address['address']}: {e}")
                    continue
            
            return {
                'success': True,
                'message': f'עודכנו {updated_count} כתובות',
                'updated': updated_count,
                'total': len(addresses)
            }
            
        except Exception as e:
            logger.error(f"שגיאה בניסיון חוזר לגיאוקודינג: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _geocode_with_nominatim(self, address: str) -> Tuple[Optional[float], Optional[float]]:
        """גיאוקודינג עם Nominatim API"""
        try:
            # הכן URL
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'countrycodes': 'IL',  # ישראל בלבד
                'addressdetails': 1
            }
            
            # בקש מהשרת
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                result = data[0]
                latitude = float(result.get('lat', 0))
                longitude = float(result.get('lon', 0))
                
                # וודא שהקואורדינטות בישראל
                if self._is_in_israel(latitude, longitude):
                    return latitude, longitude
            
            return None, None
            
        except Exception as e:
            logger.error(f"שגיאה בגיאוקודינג Nominatim: {e}")
            return None, None
    
    def _clean_address(self, address: str) -> str:
        """נקה כתובת לגיאוקודינג"""
        try:
            # הסר רווחים מיותרים
            address = address.strip()
            
            # הוסף "ירושלים" אם אין עיר
            if not any(city in address.lower() for city in ['ירושלים', 'jerusalem', 'תל אביב', 'חיפה']):
                address = f"{address}, ירושלים"
            
            # הוסף "ישראל" אם אין
            if 'ישראל' not in address.lower() and 'israel' not in address.lower():
                address = f"{address}, ישראל"
            
            return address
            
        except Exception as e:
            logger.error(f"שגיאה בניקוי כתובת: {e}")
            return address
    
    def _extract_city(self, address: str) -> str:
        """חלץ עיר מכתובת"""
        try:
            address_lower = address.lower()
            
            if 'ירושלים' in address_lower or 'jerusalem' in address_lower:
                return 'ירושלים'
            elif 'תל אביב' in address_lower or 'tel aviv' in address_lower:
                return 'תל אביב'
            elif 'חיפה' in address_lower or 'haifa' in address_lower:
                return 'חיפה'
            else:
                return 'ירושלים'  # ברירת מחדל
                
        except Exception as e:
            logger.error(f"שגיאה בחילוץ עיר: {e}")
            return 'ירושלים'
    
    def _extract_neighborhood(self, address: str) -> str:
        """חלץ שכונה מכתובת"""
        try:
            # רשימת שכונות ידועות בירושלים
            neighborhoods = [
                'גאולה', 'מאה שערים', 'בית וגן', 'קטמונים', 'גילה',
                'נחלאות', 'משכנות שאננים', 'תלפיות', 'עין כרם',
                'רמת שלמה', 'פסגת זאב', 'רמות', 'הר נוף'
            ]
            
            address_lower = address.lower()
            
            for neighborhood in neighborhoods:
                if neighborhood in address_lower:
                    return neighborhood
            
            return 'לא ידוע'
            
        except Exception as e:
            logger.error(f"שגיאה בחילוץ שכונה: {e}")
            return 'לא ידוע'
    
    def _is_in_israel(self, latitude: float, longitude: float) -> bool:
        """בדוק אם הקואורדינטות בישראל"""
        try:
            # גבולות ישראל בקירוב
            # קו רוחב: 29.5 - 33.5
            # קו אורך: 34.0 - 36.0
            
            return (29.5 <= latitude <= 33.5 and 
                   34.0 <= longitude <= 36.0)
            
        except Exception as e:
            logger.error(f"שגיאה בבדיקת גבולות: {e}")
            return False
