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
        """קבלת כתובות בלי קואורדינטות"""
        try:
            service = AddressService()
            addresses = service.get_missing_coordinates()
            
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
    def add_single_address() -> Dict:
        """הוספת כתובת בודדת"""
        try:
            data = request.get_json()
            
            if not data:
                return {
                    'success': False,
                    'error': 'לא נשלחו נתונים'
                }
            
            service = AddressService()
            result = service.add_single_address(data)
            
            return result
            
        except Exception as e:
            logger.error(f"שגיאה בהוספת כתובת: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def toggle_visited() -> Dict:
        """החלפת סטטוס ביקור"""
        try:
            data = request.get_json()
            
            if not data or 'id' not in data:
                return {
                    'success': False,
                    'error': 'חסר מזהה כתובת'
                }
            
            service = AddressService()
            result = service.toggle_visited(data['id'])
            
            return result
            
        except Exception as e:
            logger.error(f"שגיאה בהחלפת סטטוס ביקור: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def delete_address() -> Dict:
        """מחיקת כתובת"""
        try:
            data = request.get_json()
            
            if not data or 'id' not in data:
                return {
                    'success': False,
                    'error': 'חסר מזהה כתובת'
                }
            
            service = AddressService()
            result = service.delete_address(data['id'])
            
            return result
            
        except Exception as e:
            logger.error(f"שגיאה במחיקת כתובת: {e}")
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
