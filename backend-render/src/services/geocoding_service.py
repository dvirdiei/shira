# -*- coding: utf-8 -*-
"""
🗺️ Geocoding Service - שירות גיאוקודינג מתקדם
מבוסס על אלגוריתם מתקדם עם 3 ניסיונות וזיהוי ערים
"""

import os
import json
import requests
import time
import logging
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

from ..database.connection import get_database_client
from ..utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

class GeocodingService:
    """שירות גיאוקודינג מתקדם עם תמיכה בערים שונות"""
    
    def __init__(self):
        self.api_key = os.getenv('MAPS_CO_API_KEY', '674f3d5932464986828229gmn1437f0')
        self.rate_limiter = RateLimiter(max_requests=20, time_window=60)
        self.supabase = get_database_client()
        
    def geocode_and_validate(self, addresses: List[str]) -> List[Dict]:
        """
        מבצע עד 3 ניסיונות geocode+reverse לכל כתובת:
        • 2 ניסיונות ראשונים עם הכתובת כפי שהיא
        • ניסיון שלישי עם הוספת העיר מהכתובת או ירושלים כברירת מחדל
        
        Args:
            addresses: רשימת כתובות לעיבוד
            
        Returns:
            רשימת תוצאות עם lat, lon, street, city
        """
        results = []
        total = len(addresses)
        
        for idx, address in enumerate(addresses, start=1):
            logger.info(f"🔄 ({idx}/{total}) מעבד כתובת: {address}")
            result = self._process_single_address(address)
            results.append(result)
            
            # המתנה קצרה למניעת rate limit
            time.sleep(0.5)
            
        return results
    
    def _process_single_address(self, address: str) -> Dict:
        """עיבוד כתובת בודדת עם 3 ניסיונות"""
        found = False
        
        # חלץ עיר מהכתובת אם קיימת
        city_from_address = self._extract_city_from_address(address)
        
        # שלושה ניסיונות
        for attempt in range(3):
            query = self._build_query(address, attempt, city_from_address)
            
            # 1. Forward Geocode
            lat, lon = self._forward_geocode(query)
            if lat is None:
                logger.warning(f"⚠️ ניסיון {attempt+1}: forward geocode נכשל עבור '{query}'")
                continue
                
            time.sleep(1)  # המתנה בין בקשות
            
            # 2. Reverse Geocode
            street, city_en = self._reverse_geocode(lat, lon)
            
            # 3. בדיקה וסיום
            if city_en:
                logger.info(f"✅ {query}: זוהתה עיר {city_en}, רחוב: {street}")
                return {
                    'lat': lat,
                    'lon': lon,
                    'street': street,
                    'city': city_en,
                    'original_address': address
                }
            else:
                logger.warning(f"⚠️ ניסיון {attempt+1}: לא זוהתה עיר עבור '{query}'")
                time.sleep(1)
        
        # אם כל הניסיונות נכשלו
        logger.error(f"❌ נכשל למצוא: {address}")
        return {
            'lat': None,
            'lon': None,
            'street': None,
            'city': address,
            'original_address': address
        }
    
    def _extract_city_from_address(self, address: str) -> Optional[str]:
        """חילוץ עיר מהכתובת"""
        # רשימת ערים נפוצות
        cities = [
            'ירושלים', 'תל אביב', 'חיפה', 'באר שבע', 'נתניה', 'פתח תקווה',
            'בית חורון', 'מעלה אדומים', 'ביתר עלית', 'גבעת זאב', 'מבוא ביתר',
            'שורש', 'הר אדר', 'רמת גן', 'בני ברק', 'חולון', 'רחובות'
        ]
        
        address_lower = address.lower()
        for city in cities:
            if city in address_lower:
                return city
        
        return None
    
    def _build_query(self, address: str, attempt: int, city_from_address: Optional[str]) -> str:
        """בניית שאילתה בהתאם לניסיון"""
        if attempt < 2:
            return address
        else:
            # ניסיון שלישי - הוסף עיר
            if city_from_address and city_from_address not in address:
                return f"{address} {city_from_address}"
            elif 'ירושלים' not in address:
                return f"{address} ירושלים"
            else:
                return address
    
    def _forward_geocode(self, query: str) -> Tuple[Optional[float], Optional[float]]:
        """Forward geocoding עם retry"""
        for retry in range(3):
            try:
                self.rate_limiter.wait_if_needed()
                
                url = f"https://geocode.maps.co/search?api_key={self.api_key}&q={quote(query)}"
                response = requests.get(url, timeout=30)
                
                if response.status_code == 429:
                    logger.warning(f"Rate limit hit, waiting...")
                    time.sleep(2)
                    continue
                    
                response.raise_for_status()
                data = response.json()
                
                if not data:
                    return None, None
                    
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return lat, lon
                
            except Exception as e:
                logger.error(f"שגיאה ב-forward geocoding (retry {retry+1}): {e}")
                time.sleep(1)
                
        return None, None
    
    def _reverse_geocode(self, lat: float, lon: float) -> Tuple[Optional[str], Optional[str]]:
        """Reverse geocoding עם retry"""
        for retry in range(3):
            try:
                self.rate_limiter.wait_if_needed()
                
                url = f"https://geocode.maps.co/reverse?api_key={self.api_key}&lat={lat}&lon={lon}"
                response = requests.get(url, timeout=30)
                
                if response.status_code == 429:
                    logger.warning(f"Rate limit hit, waiting...")
                    time.sleep(2)
                    continue
                    
                response.raise_for_status()
                data = response.json()
                
                address_info = data.get('address', {})
                street = (address_info.get('road') or 
                         address_info.get('pedestrian') or 
                         address_info.get('residential'))
                
                display_name = data.get('display_name', '')
                
                # זיהוי עיר מהתוצאה
                city = self._identify_city_from_display_name(display_name, address_info)
                
                return street, city
                
            except Exception as e:
                logger.error(f"שגיאה ב-reverse geocoding (retry {retry+1}): {e}")
                time.sleep(1)
                
        return None, None
    
    def _identify_city_from_display_name(self, display_name: str, address_info: Dict) -> Optional[str]:
        """זיהוי עיר מה-display_name או מפרטי הכתובת"""
        
        # מפת זיהוי ערים
        city_mapping = {
            'Jerusalem': 'ירושלים',
            'Tel Aviv': 'תל אביב',
            'Haifa': 'חיפה',
            'Beer Sheva': 'באר שבע',
            'Netanya': 'נתניה',
            'Petah Tikva': 'פתח תקווה',
            'Bet Horon': 'בית חורון',
            'Maale Adumim': 'מעלה אדומים',
            'Beitar Illit': 'ביתר עלית',
            'Givat Zeev': 'גבעת זאב',
            'Shoresh': 'שורש',
            'Har Adar': 'הר אדר'
        }
        
        # חפש בשם המלא
        for eng_name, heb_name in city_mapping.items():
            if eng_name in display_name or heb_name in display_name:
                return heb_name
        
        # חפש בפרטי הכתובת
        city_fields = ['city', 'town', 'village', 'municipality']
        for field in city_fields:
            if field in address_info:
                city_value = address_info[field]
                if city_value in city_mapping:
                    return city_mapping[city_value]
                # אם זה שם עברי, החזר כמו שהוא
                if any(char in 'אבגדהוזחטיכלמנסעפצקרשת' for char in city_value):
                    return city_value
        
        return None
    
    def batch_geocode_advanced(self, addresses: List[str]) -> Dict:
        """עיבוד מצרפי מתקדם של כתובות"""
        try:
            logger.info(f"🚀 מתחיל עיבוד מצרפי של {len(addresses)} כתובות")
            
            # גיאוקודינג מתקדם
            results = self.geocode_and_validate(addresses)
            
            # חלוקה לתוצאות מוצלחות ולא מוצלחות
            successful = [r for r in results if r['lat'] is not None]
            failed = [r for r in results if r['lat'] is None]
            
            logger.info(f"✅ הצלחה: {len(successful)}, ❌ כשלון: {len(failed)}")
            
            # שמירה בבסיס הנתונים
            saved_count = 0
            failed_save = []
            
            for result in successful:
                try:
                    # שמירת הכתובת
                    insert_result = self.supabase.table('addresses').insert({
                        'address': result['original_address'],
                        'lat': result['lat'],
                        'lon': result['lon'],
                        'neighborhood': result['street'] or result['city'],
                        'visited': False,
                        'source': 'geocoding_api'
                    }).execute()
                    
                    if insert_result.data:
                        saved_count += 1
                        logger.info(f"💾 נשמר: {result['original_address']}")
                    
                except Exception as e:
                    logger.error(f"שגיאה בשמירת {result['original_address']}: {e}")
                    failed_save.append(result['original_address'])
            
            # שמירת כתובות שנכשלו בטבלת missing_coordinates
            for result in failed:
                try:
                    insert_result = self.supabase.table('addresses_missing_coordinates').insert({
                        'address': result['original_address'],
                        'reason': 'geocoding_failed',
                        'manual_coordinates_needed': True,
                        'manual_coordinates_added': False,
                        'attempts': 3
                    }).execute()
                    
                    if insert_result.data:
                        logger.info(f"📝 נכשל - הועבר לטבלת missing: {result['original_address']}")
                        
                except Exception as e:
                    logger.error(f"שגיאה בשמירת כתובת נכשלת {result['original_address']}: {e}")
            
            return {
                'success': True,
                'message': f'עובדו {len(addresses)} כתובות: {saved_count} נשמרו, {len(failed)} נכשלו',
                'processed': len(addresses),
                'successful': len(successful),
                'failed': len(failed),
                'saved': saved_count,
                'failed_addresses': [r['original_address'] for r in failed]
            }
            
        except Exception as e:
            logger.error(f"שגיאה בעיבוד מצרפי: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def batch_geocode(self, addresses: List[str]) -> Dict:
        """גיאוקודינג רגיל (לתאימות לאחור)"""
        return self.batch_geocode_advanced(addresses)
    
    def geocode_address(self, address: str) -> Dict:
        """גיאוקודינג כתובת בודדת"""
        try:
            result = self._process_single_address(address)
            
            if result['lat'] is not None:
                return {
                    'success': True,
                    'address': address,
                    'latitude': result['lat'],
                    'longitude': result['lon'],
                    'neighborhood': result['street'] or result['city']
                }
            else:
                return {
                    'success': False,
                    'address': address,
                    'error': 'לא נמצאה כתובת'
                }
                
        except Exception as e:
            logger.error(f"שגיאה בגיאוקודינג כתובת בודדת: {e}")
            return {
                'success': False,
                'address': address,
                'error': str(e)
            }
    
    def validate_maps_co_api_key(self) -> Dict:
        """בדיקת תוקף API key"""
        try:
            url = f"https://geocode.maps.co/search?api_key={self.api_key}&q=Jerusalem"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'message': 'API key תקין'
                }
            else:
                return {
                    'success': False,
                    'message': f'API key לא תקין: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"שגיאה בבדיקת API key: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_geocoding_status(self) -> Dict:
        """קבלת סטטוס שירות הגיאוקודינג"""
        try:
            api_status = self.validate_maps_co_api_key()
            
            return {
                'success': True,
                'api_key_valid': api_status['success'],
                'rate_limiter_status': self.rate_limiter.get_status(),
                'service_status': 'active'
            }
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת סטטוס גיאוקודינג: {e}")
            return {
                'success': False,
                'error': str(e)
            }