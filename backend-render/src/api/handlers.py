# -*- coding: utf-8 -*-
"""
🎯 API Handlers - הנוסע המתמיד
כל ה-handlers מקובצים לפי קטגוריות לוגיות
"""

import logging
from flask import jsonify, request
from typing import Dict, List, Optional
from datetime import datetime

from ..services.address_service import AddressService
from ..services.geocoding_service import GeocodingService
from ..services.data_service import DataService
from ..database.queries import AddressQueries

logger = logging.getLogger(__name__)

class AddressHandlers:
    """🏠 Handlers לניהול כתובות"""
    
    @staticmethod
    def get_all_addresses() -> Dict:
        """קבלת כל הכתובות"""
        try:
            service = AddressService()
            addresses = service.get_all_addresses()
            
            return {
                'success': True,
                'addresses': addresses,
                'count': len(addresses)
            }
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת כתובות: {e}")
            return {
                'success': False,
                'error': str(e),
                'addresses': []
            }
    
    @staticmethod
    def get_addresses_array() -> Dict:
        """קבלת כתובות כמערך פשוט"""
        try:
            service = AddressService()
            addresses = service.get_addresses_array()
            
            return {
                'success': True,
                'addresses': addresses,
                'count': len(addresses)
            }
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת מערך כתובות: {e}")
            return {
                'success': False,
                'error': str(e),
                'addresses': []
            }
    
    @staticmethod
    def get_all_addresses_detailed() -> Dict:
        """קבלת כל הכתובות עם מידע מפורט"""
        try:
            service = AddressService()
            addresses = service.get_all_addresses_detailed()
            
            return {
                'success': True,
                'addresses': addresses,
                'count': len(addresses)
            }
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת כתובות מפורטות: {e}")
            return {
                'success': False,
                'error': str(e),
                'addresses': []
            }
    
    @staticmethod
    def get_missing_coordinates() -> Dict:
        """קבלת כתובות ללא קואורדינטות"""
        try:
            from ..database.connection import get_addresses_without_coordinates
            addresses = get_addresses_without_coordinates()
            
            return {
                'success': True,
                'addresses': addresses,
                'count': len(addresses)
            }
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת כתובות ללא קואורדינטות: {e}")
            return {
                'success': False,
                'error': str(e),
                'addresses': []
            }
    
    @staticmethod
    def get_addresses_needing_manual() -> Dict:
        """קבלת כתובות שצריכות קואורדינטות ידניות"""
        try:
            from ..database.connection import get_addresses_needing_manual_coordinates
            addresses = get_addresses_needing_manual_coordinates()
            
            return {
                'success': True,
                'addresses': addresses,
                'count': len(addresses)
            }
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת כתובות שצריכות קואורדינטות ידניות: {e}")
            return {
                'success': False,
                'error': str(e),
                'addresses': []
            }
    
    @staticmethod
    def get_all_addresses_for_map() -> Dict:
        """קבלת כל הכתובות למפה (משתי הטבלאות)"""
        try:
            from ..database.connection import get_all_addresses_for_map
            addresses = get_all_addresses_for_map()
            
            return {
                'success': True,
                'addresses': addresses,
                'count': len(addresses)
            }
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת כל הכתובות למפה: {e}")
            return {
                'success': False,
                'error': str(e),
                'addresses': []
            }
    
    @staticmethod
    def add_manual_coordinates() -> Dict:
        """הוספת קואורדינטות ידניות לכתובת"""
        try:
            data = request.get_json()
            
            if not data:
                return {
                    'success': False,
                    'error': 'לא נשלחו נתונים'
                }
            
            missing_id = data.get('missing_id')
            lat = data.get('lat')
            lon = data.get('lon')
            neighborhood = data.get('neighborhood')
            added_by = data.get('added_by', 'unknown')
            
            if not all([missing_id, lat, lon]):
                return {
                    'success': False,
                    'error': 'חסרים נתונים נדרשים: missing_id, lat, lon'
                }
            
            from ..database.connection import add_manual_coordinates
            success = add_manual_coordinates(missing_id, lat, lon, neighborhood, added_by)
            
            if success:
                return {
                    'success': True,
                    'message': 'קואורדינטות ידניות נוספו בהצלחה'
                }
            else:
                return {
                    'success': False,
                    'error': 'שגיאה בהוספת קואורדינטות ידניות'
                }
                
        except Exception as e:
            logger.error(f"שגיאה בהוספת קואורדינטות ידניות: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def toggle_visited() -> Dict:
        """החלפת סטטוס ביקור בשתי הטבלאות"""
        try:
            data = request.get_json()
            
            # תמיכה בשדה id או address (תאימות לאחור)
            address_id = data.get('id')
            address_text = data.get('address')
            
            if not address_id and not address_text:
                return {
                    'success': False,
                    'error': 'חסר מזהה כתובת או שם כתובת'
                }
            
            # קביעת סוג הטבלה (addresses או addresses_missing_coordinates)
            table_type = data.get('table_type', 'addresses')  # ברירת מחדל לטבלת addresses
            
            service = AddressService()
            
            # אם יש id, השתמש בו; אחרת חפש לפי שם הכתובת
            if address_id:
                result = service.toggle_visited(address_id, table_type)
            else:
                # חיפוש הכתובת לפי שם והחזרת ה-id
                address_record = service.find_address_by_name(address_text, table_type)
                if address_record:
                    result = service.toggle_visited(address_record['id'], table_type)
                else:
                    result = {
                        'success': False,
                        'error': f'לא נמצאה כתובת בשם: {address_text}'
                    }
            
            return result
            
        except Exception as e:
            logger.error(f"שגיאה בהחלפת סטטוס ביקור: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def delete_address() -> Dict:
        """מחיקת כתובת משתי הטבלאות"""
        try:
            data = request.get_json()
            
            # תמיכה בשדה id או address (תאימות לאחור)
            address_id = data.get('id')
            address_text = data.get('address')
            
            if not address_id and not address_text:
                return {
                    'success': False,
                    'error': 'חסר מזהה כתובת או שם כתובת'
                }
            
            # קביעת סוג הטבלה
            table_type = data.get('table_type', 'addresses')
            
            service = AddressService()
            
            # אם יש id, השתמש בו; אחרת חפש לפי שם הכתובת
            if address_id:
                result = service.delete_address(address_id, table_type)
            else:
                # חיפוש הכתובת לפי שם והחזרת ה-id
                address_record = service.find_address_by_name(address_text, table_type)
                if address_record:
                    result = service.delete_address(address_record['id'], table_type)
                else:
                    result = {
                        'success': False,
                        'error': f'לא נמצאה כתובת בשם: {address_text}'
                    }
            
            return result
            
        except Exception as e:
            logger.error(f"שגיאה במחיקת כתובת: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def process_new_address() -> Dict:
        """עיבוד כתובת חדשה עם geocoding אוטומטי"""
        try:
            data = request.get_json()
            
            if not data:
                return {
                    'success': False,
                    'error': 'לא נשלחו נתונים'
                }
            
            address = data.get('address')
            
            if not address:
                return {
                    'success': False,
                    'error': 'חסרה כתובת'
                }
            
            # ייבוא שירות הגיאוקודינג
            from ..services.geocoding_service import GeocodingService
            from ..database.connection import process_new_address
            
            geocoding_service = GeocodingService()
            success, message = process_new_address(address, geocoding_service)
            
            return {
                'success': success,
                'message': message,
                'address': address
            }
                
        except Exception as e:
            logger.error(f"שגיאה בעיבוד כתובת חדשה: {e}")
            return {
                'success': False,
                'error': str(e)
            }


class GeocodingHandlers:
    """🗺️ Handlers לגיאוקודינג"""
    
    @staticmethod
    def batch_geocode() -> Dict:
        """הוספת כתובות בבת אחת עם גיאוקודינג"""
        try:
            data = request.get_json()
            
            if not data or 'addresses' not in data:
                return {
                    'success': False,
                    'error': 'לא נשלחו כתובות להוספה'
                }
            
            service = GeocodingService()
            result = service.batch_geocode(data['addresses'])
            
            return result
            
        except Exception as e:
            logger.error(f"שגיאה בגיאוקודינג אצווה: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def retry_geocoding() -> Dict:
        """ניסיון חוזר לגיאוקודינג"""
        try:
            service = GeocodingService()
            result = service.retry_geocoding()
            
            return result
            
        except Exception as e:
            logger.error(f"שגיאה בניסיון חוזר לגיאוקודינג: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def test_geocoding_service() -> Dict:
        """בדיקת שירות הגיאוקודינג"""
        try:
            data = request.get_json() if request.get_json() else {}
            test_address = data.get('test_address', 'דרך חברון 1, ירושלים')
            
            service = GeocodingService()
            result = service.test_geocoding_service(test_address)
            
            return result
            
        except Exception as e:
            logger.error(f"שגיאה בבדיקת שירות הגיאוקודינג: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_service_status() -> Dict:
        """קבלת סטטוס שירות הגיאוקודינג"""
        try:
            service = GeocodingService()
            result = service.get_service_status()
            
            return result
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת סטטוס השירות: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def validate_api_key() -> Dict:
        """בדיקת תוקף API key"""
        try:
            service = GeocodingService()
            result = service.validate_maps_co_api_key()
            
            return result
            
        except Exception as e:
            logger.error(f"שגיאה בבדיקת API key: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def geocode_single_address() -> Dict:
        """גיאוקודינג כתובת בודדת"""
        try:
            data = request.get_json()
            
            if not data or 'address' not in data:
                return {
                    'success': False,
                    'error': 'חסרה כתובת'
                }
            
            service = GeocodingService()
            result = service.geocode_address(data['address'])
            
            return result
            
        except Exception as e:
            logger.error(f"שגיאה בגיאוקודינג כתובת בודדת: {e}")
            return {
                'success': False,
                'error': str(e)
            }

class DataHandlers:
    """📊 Handlers לניהול נתונים"""
    
    @staticmethod
    def reset_data() -> Dict:
        """איפוס נתונים"""
        try:
            service = DataService()
            result = service.reset_data()
            
            return result
            
        except Exception as e:
            logger.error(f"שגיאה באיפוס נתונים: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def reset_all_data() -> Dict:
        """איפוס כל הנתונים"""
        try:
            service = DataService()
            result = service.reset_all_data()
            
            return result
            
        except Exception as e:
            logger.error(f"שגיאה באיפוס כל הנתונים: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_statistics() -> Dict:
        """קבלת סטטיסטיקות"""
        try:
            service = DataService()
            result = service.get_statistics()
            
            return result
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת סטטיסטיקות: {e}")
            return {
                'success': False,
                'error': str(e)
            }


class SystemHandlers:
    """⚙️ Handlers למערכת"""
    
    @staticmethod
    def health_check() -> Dict:
        """בדיקת תקינות השרת"""
        try:
            return {
                'success': True,
                'status': 'healthy',
                'database_type': 'supabase',
                'message': 'השרת פועל עם SUPABASE',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"שגיאה בבדיקת תקינות: {e}")
            return {
                'success': False,
                'status': 'unhealthy',
                'error': str(e)
            }
    
    @staticmethod
    def test_connection() -> Dict:
        """בדיקת חיבור לבסיס הנתונים"""
        try:
            queries = AddressQueries()
            result = queries.test_connection()
            
            return {
                'success': True,
                'connection': 'healthy',
                'database_type': 'supabase',
                'message': 'החיבור לבסיס הנתונים תקין',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"שגיאה בבדיקת חיבור: {e}")
            return {
                'success': False,
                'connection': 'failed',
                'error': str(e)
            }
    
    @staticmethod
    def upload_addresses_file() -> Dict:
        """העלאת קובץ כתובות בפורמט טקסט מהפרונט-אנד"""
        try:
            # בדוק אם יש קובץ בבקשה
            if 'file' not in request.files:
                return {
                    'success': False,
                    'error': 'לא נשלח קובץ'
                }
            
            file = request.files['file']
            
            # בדוק אם נבחר קובץ
            if file.filename == '':
                return {
                    'success': False,
                    'error': 'לא נבחר קובץ'
                }
            
            # בדוק סוג הקובץ
            if not file.filename.lower().endswith(('.txt', '.csv')):
                return {
                    'success': False,
                    'error': 'רק קבצי טקסט (.txt) או CSV (.csv) מותרים'
                }
            
            # קרא את תוכן הקובץ
            try:
                # נסה לקרוא כ-UTF-8
                content = file.read().decode('utf-8')
            except UnicodeDecodeError:
                # אם נכשל, נסה קידודים אחרים
                file.seek(0)
                try:
                    content = file.read().decode('windows-1255')  # קידוד עברית בחלונות
                except UnicodeDecodeError:
                    file.seek(0)
                    try:
                        content = file.read().decode('iso-8859-8')  # קידוד עברית ישן
                    except UnicodeDecodeError:
                        return {
                            'success': False,
                            'error': 'בעיה בקריאת הקובץ - וודא שהוא בקידוד UTF-8'
                        }
            
            # חלק את התוכן לשורות והסר רווחים מיותרים
            addresses = [line.strip() for line in content.split('\n') if line.strip()]
            
            if not addresses:
                return {
                    'success': False,
                    'error': 'הקובץ ריק או לא מכיל כתובות'
                }
            
            logger.info(f"התקבל קובץ '{file.filename}' עם {len(addresses)} כתובות")
            
            # השתמש בגיאוקודינג המתקדם
            service = GeocodingService()
            result = service.batch_geocode_advanced(addresses)
            
            return {
                'success': True,
                'message': f'הקובץ {file.filename} עובד בהצלחה עם {len(addresses)} כתובות',
                'filename': file.filename,
                'addresses_count': len(addresses),
                'geocoding_result': result
            }
                
        except Exception as e:
            logger.error(f"שגיאה בהעלאת קובץ כתובות: {e}")
            return {
                'success': False,
                'error': str(e)
            }
