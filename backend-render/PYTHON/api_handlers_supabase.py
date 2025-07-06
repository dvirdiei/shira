# -*- coding: utf-8 -*-
"""
API Handlers for Supabase - הנוסע המתמיד
טיפול בכל ה-API endpoints עם Supabase
"""

import logging
from flask import jsonify, request
from typing import Dict, List, Optional
from datetime import datetime

from .supabase_handler import get_supabase_handler

logger = logging.getLogger(__name__)

def handle_get_addresses() -> Dict:
    """קבלת כל הכתובות"""
    try:
        handler = get_supabase_handler()
        addresses = handler.get_all_addresses()
        
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

def handle_add_address() -> Dict:
    """הוספת כתובת בודדת"""
    try:
        data = request.get_json()
        
        if not data:
            return {
                'success': False,
                'error': 'לא נשלחו נתונים'
            }
        
        # אימות נתונים
        address = data.get('address', '').strip()
        city = data.get('city', '').strip()
        
        if not address:
            return {
                'success': False,
                'error': 'כתובת חובה'
            }
        
        # הכנת נתונים
        address_data = {
            'address': address,
            'city': city,
            'latitude': data.get('latitude'),
            'longitude': data.get('longitude'),
            'created_at': datetime.now().isoformat()
        }
        
        # הוספה לבסיס הנתונים
        handler = get_supabase_handler()
        result = handler.add_single_address(address_data)
        
        if result:
            return {
                'success': True,
                'message': 'כתובת נוספה בהצלחה',
                'address': result
            }
        else:
            return {
                'success': False,
                'error': 'לא ניתן להוסיף כתובת'
            }
            
    except Exception as e:
        logger.error(f"שגיאה בהוספת כתובת: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def handle_batch_geocode() -> Dict:
    """גיאוקודינג לכל הכתובות ללא קואורדינטות"""
    try:
        handler = get_supabase_handler()
        
        # קבלת כתובות ללא קואורדינטות
        addresses_to_geocode = handler.get_addresses_without_coordinates()
        
        if not addresses_to_geocode:
            return {
                'success': True,
                'message': 'כל הכתובות כבר עם קואורדינטות ✅',
                'geocoded_count': 0,
                'total_count': 0
            }
        
        # ייבוא geocoding handler (יצירה בהמשך)
        from .geocoding_handlers_supabase import geocode_addresses_batch
        
        # הרצת גיאוקודינג
        results = geocode_addresses_batch(addresses_to_geocode)
        
        return {
            'success': True,
            'message': f'גיאוקודינג הושלם ל-{results["success_count"]} כתובות',
            'geocoded_count': results['success_count'],
            'failed_count': results['failed_count'],
            'total_count': len(addresses_to_geocode)
        }
        
    except Exception as e:
        logger.error(f"שגיאה בגיאוקודינג: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def handle_reset_data() -> Dict:
    """איפוס כל הנתונים"""
    try:
        handler = get_supabase_handler()
        
        # מחיקת כל הנתונים
        if handler.delete_all_addresses():
            return {
                'success': True,
                'message': 'כל הנתונים נמחקו בהצלחה 🗑️'
            }
        else:
            return {
                'success': False,
                'error': 'לא ניתן למחוק נתונים'
            }
            
    except Exception as e:
        logger.error(f"שגיאה באיפוס נתונים: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def handle_get_statistics() -> Dict:
    """קבלת סטטיסטיקות"""
    try:
        handler = get_supabase_handler()
        stats = handler.get_statistics()
        
        return {
            'success': True,
            'statistics': stats
        }
        
    except Exception as e:
        logger.error(f"שגיאה בקבלת סטטיסטיקות: {e}")
        return {
            'success': False,
            'error': str(e),
            'statistics': {
                'total_addresses': 0,
                'geocoded_addresses': 0,
                'pending_geocoding': 0,
                'geocoded_percentage': 0
            }
        }

def handle_retry_geocoding() -> Dict:
    """ניסיון חוזר לגיאוקודינג כתובות שנכשלו"""
    try:
        handler = get_supabase_handler()
        
        # קבלת כתובות ללא קואורדינטות
        failed_addresses = handler.get_addresses_without_coordinates()
        
        if not failed_addresses:
            return {
                'success': True,
                'message': 'אין כתובות לניסיון חוזר',
                'retry_count': 0
            }
        
        # ייבוא geocoding handler
        from .geocoding_handlers_supabase import geocode_addresses_batch
        
        # ניסיון חוזר עם המתנה ארוכה יותר
        results = geocode_addresses_batch(failed_addresses, delay=2.0)
        
        return {
            'success': True,
            'message': f'ניסיון חוזר הושלם ל-{results["success_count"]} כתובות',
            'retry_count': results['success_count'],
            'failed_count': results['failed_count']
        }
        
    except Exception as e:
        logger.error(f"שגיאה בניסיון חוזר: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def handle_test_connection() -> Dict:
    """בדיקת חיבור ל-Supabase"""
    try:
        handler = get_supabase_handler()
        
        if handler.test_connection():
            return {
                'success': True,
                'message': 'חיבור ל-Supabase תקין ✅'
            }
        else:
            return {
                'success': False,
                'error': 'בעיה בחיבור ל-Supabase'
            }
            
    except Exception as e:
        logger.error(f"שגיאה בבדיקת חיבור: {e}")
        return {
            'success': False,
            'error': str(e)
        }
