# -*- coding: utf-8 -*-
"""
✅ Data Validators - הנוסע המתמיד
אמת נתונים שונים במערכת
"""

import re
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class DataValidator:
    """אמת נתונים כלליים"""
    
    @staticmethod
    def validate_address_string(address: str) -> bool:
        """אמת תקינות כתובת"""
        try:
            if not address or not isinstance(address, str):
                return False
            
            # בדוק שהכתובת אינה ריקה
            if not address.strip():
                return False
            
            # בדוק אורך מינימלי
            if len(address.strip()) < 3:
                return False
            
            # בדוק שיש לפחות אות אחת
            if not re.search(r'[א-ת]|[a-zA-Z]', address):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"שגיאה באמת כתובת: {e}")
            return False
    
    @staticmethod
    def validate_coordinates(latitude: Optional[float], longitude: Optional[float]) -> bool:
        """אמת קואורדינטות גיאוגרפיות"""
        try:
            if latitude is None or longitude is None:
                return True  # קואורדינטות ריקות זה בסדר
            
            # בדוק שהם מספרים
            if not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
                return False
            
            # בדוק טווח קו רוחב
            if not -90 <= latitude <= 90:
                return False
            
            # בדוק טווח קו אורך
            if not -180 <= longitude <= 180:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"שגיאה באמת קואורדינטות: {e}")
            return False
    
    @staticmethod
    def validate_coordinates_in_israel(latitude: float, longitude: float) -> bool:
        """אמת שהקואורדינטות בתחומי ישראל"""
        try:
            # גבולות ישראל בקירוב
            # קו רוחב: 29.5 - 33.5
            # קו אורך: 34.0 - 36.0
            
            return (29.5 <= latitude <= 33.5 and 
                   34.0 <= longitude <= 36.0)
            
        except Exception as e:
            logger.error(f"שגיאה באמת גבולות ישראל: {e}")
            return False
    
    @staticmethod
    def validate_city_name(city: str) -> bool:
        """אמת שם עיר"""
        try:
            if not city or not isinstance(city, str):
                return False
            
            # בדוק שהשם אינו ריק
            if not city.strip():
                return False
            
            # בדוק אורך מינימלי
            if len(city.strip()) < 2:
                return False
            
            # בדוק שיש רק אותיות ורווחים
            if not re.match(r'^[א-ת\s]+$|^[a-zA-Z\s]+$', city.strip()):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"שגיאה באמת שם עיר: {e}")
            return False
    
    @staticmethod
    def validate_address_data(data: Dict) -> bool:
        """אמת נתוני כתובת מלאים"""
        try:
            if not isinstance(data, dict):
                return False
            
            # בדוק שדות חובה
            address = data.get('address')
            if not DataValidator.validate_address_string(address):
                return False
            
            # בדוק עיר (אם קיימת)
            city = data.get('city')
            if city and not DataValidator.validate_city_name(city):
                return False
            
            # בדוק קואורדינטות (אם קיימות)
            latitude = data.get('latitude')
            longitude = data.get('longitude')
            if not DataValidator.validate_coordinates(latitude, longitude):
                return False
            
            # בדוק סטטוס ביקור
            visited = data.get('visited')
            if visited is not None and not isinstance(visited, bool):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"שגיאה באמת נתוני כתובת: {e}")
            return False
    
    @staticmethod
    def validate_id(id_value: Any) -> bool:
        """אמת מזהה"""
        try:
            if id_value is None:
                return False
            
            # בדוק שהוא מספר חיובי
            if isinstance(id_value, (int, float)):
                return id_value > 0
            
            # בדוק שהוא מחרוזת מספרית
            if isinstance(id_value, str):
                return id_value.isdigit() and int(id_value) > 0
            
            return False
            
        except Exception as e:
            logger.error(f"שגיאה באמת מזהה: {e}")
            return False
    
    @staticmethod
    def validate_source(source: str) -> bool:
        """אמת מקור נתונים"""
        try:
            if not source or not isinstance(source, str):
                return False
            
            # רשימת מקורות מותרים
            allowed_sources = [
                'manual', 'batch_geocode', 'file_upload', 
                'api_import', 'system_init', 'migration'
            ]
            
            return source.lower() in allowed_sources
            
        except Exception as e:
            logger.error(f"שגיאה באמת מקור: {e}")
            return False
    
    @staticmethod
    def validate_batch_addresses(addresses: List[str]) -> Dict:
        """אמת רשימת כתובות לעיבוד אצווה"""
        try:
            if not isinstance(addresses, list):
                return {
                    'valid': False,
                    'error': 'רשימת כתובות חייבת להיות מערך'
                }
            
            if not addresses:
                return {
                    'valid': False,
                    'error': 'רשימת כתובות ריקה'
                }
            
            if len(addresses) > 100:
                return {
                    'valid': False,
                    'error': 'מקסימום 100 כתובות בבת אחת'
                }
            
            valid_addresses = []
            invalid_addresses = []
            
            for i, address in enumerate(addresses):
                if DataValidator.validate_address_string(address):
                    valid_addresses.append(address)
                else:
                    invalid_addresses.append({
                        'index': i,
                        'address': address,
                        'error': 'כתובת לא תקינה'
                    })
            
            return {
                'valid': True,
                'valid_count': len(valid_addresses),
                'invalid_count': len(invalid_addresses),
                'valid_addresses': valid_addresses,
                'invalid_addresses': invalid_addresses
            }
            
        except Exception as e:
            logger.error(f"שגיאה באמת רשימת כתובות: {e}")
            return {
                'valid': False,
                'error': str(e)
            }
