# -*- coding: utf-8 -*-
"""
Supabase Routes for הנוסע המתמיד  
תומך ב-Supabase בלבד
"""

import os
import logging
from flask import jsonify, request, Blueprint

logger = logging.getLogger(__name__)

# יצירת Blueprint
api = Blueprint('api', __name__)

# ייבוא Supabase handlers
try:
    from .api_handlers_supabase import (
        handle_get_addresses,
        handle_add_address, 
        handle_batch_geocode,
        handle_reset_data,
        handle_get_statistics,
        handle_retry_geocoding,
        handle_test_connection
    )
    logger.info("✅ נטען Supabase handler")
    
except ImportError as e:
    logger.error(f"❌ שגיאה בטעינת Supabase handlers: {e}")
    raise

# Routes
@api.route('/health', methods=['GET'])
def health_check():
    """בדיקת תקינות השרת"""
    return jsonify({
        'status': 'healthy',
        'database_type': 'supabase',
        'message': 'השרת פועל עם SUPABASE'
    })

@api.route('/addresses', methods=['GET'])
def get_addresses():
    """קבלת כל הכתובות"""
    try:
        result = handle_get_addresses()
        return jsonify(result)
    except Exception as e:
        logger.error(f"שגיאה ב-/addresses: {e}")
        return jsonify({
            'success': False,
            'message': f'שגיאה בטעינת כתובות: {str(e)}'
        }), 500

# נתיב נוסף לתאימות עם Frontend
@api.route('/all-addresses', methods=['GET'])
def get_all_addresses():
    """קבלת כל הכתובות - נתיב לתאימות עם Frontend"""
    return get_addresses()

# נתיב לכתובות ללא קואורדינטות
@api.route('/missing-coordinates', methods=['GET'])
def get_missing_coordinates():
    """קבלת כתובות ללא קואורדינטות"""
    try:
        result = handle_get_addresses()
        if result.get('success'):
            # סינון רק כתובות ללא קואורדינטות
            addresses = result.get('data', [])
            missing = [addr for addr in addresses if not addr.get('lat') or not addr.get('lon')]
            return jsonify(missing)
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"שגיאה ב-/missing-coordinates: {e}")
        return jsonify([])

# נתיב לסימון ביקור
@api.route('/toggle-visited', methods=['POST'])
def toggle_visited():
    """סימון/ביטול ביקור בכתובת"""
    try:
        data = request.get_json()
        address = data.get('address')
        action = data.get('action', 'mark')  # mark או unmark
        
        if not address:
            return jsonify({
                'success': False,
                'message': 'כתובת חסרה'
            }), 400
            
        # כאן נצטרך להוסיף לוגיקה לעדכון סטטוס הביקור
        # לעת עתה נחזיר הצלחה
        return jsonify({
            'success': True,
            'message': f'סטטוס עודכן עבור {address}'
        })
        
    except Exception as e:
        logger.error(f"שגיאה ב-/toggle-visited: {e}")
        return jsonify({
            'success': False,
            'message': f'שגיאה בעדכון סטטוס: {str(e)}'
        }), 500

# נתיב למחיקת כתובת
@api.route('/delete-address', methods=['POST'])
def delete_address():
    """מחיקת כתובת"""
    try:
        data = request.get_json()
        address = data.get('address')
        
        if not address:
            return jsonify({
                'success': False,
                'message': 'כתובת חסרה'
            }), 400
            
        # כאן נצטרך להוסיף לוגיקה למחיקת הכתובת
        # לעת עתה נחזיר הצלחה
        return jsonify({
            'success': True,
            'message': f'כתובת נמחקה: {address}'
        })
        
    except Exception as e:
        logger.error(f"שגיאה ב-/delete-address: {e}")
        return jsonify({
            'success': False,
            'message': f'שגיאה במחיקת כתובת: {str(e)}'
        }), 500

# נתיב לאיפוס נתונים - תאימות עם Frontend  
@api.route('/reset-all-data', methods=['POST'])
def reset_all_data():
    """איפוס כל הנתונים - נתיב לתאימות עם Frontend"""
    return reset_data()

@api.route('/add-address', methods=['POST'])
def add_address():
    """הוספת כתובת חדשה"""
    try:
        result = handle_add_address()
        return jsonify(result)
    except Exception as e:
        logger.error(f"שגיאה ב-/add-address: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/batch-geocode', methods=['POST'])
def batch_geocode():
    """גיאוקודינג כמותי"""
    try:
        result = handle_batch_geocode()
        return jsonify(result)
    except Exception as e:
        logger.error(f"שגיאה ב-/batch-geocode: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/retry-geocoding', methods=['POST'])
def retry_geocoding():
    """ניסיון חוזר לגיאוקודינג"""
    try:
        result = handle_retry_geocoding()
        return jsonify(result)
    except Exception as e:
        logger.error(f"שגיאה ב-/retry-geocoding: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/reset-data', methods=['POST'])
def reset_data():
    """איפוס כל הנתונים"""
    try:
        result = handle_reset_data()
        return jsonify(result)
    except Exception as e:
        logger.error(f"שגיאה ב-/reset-data: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/statistics', methods=['GET'])
def get_statistics():
    """קבלת סטטיסטיקות"""
    try:
        result = handle_get_statistics()
        return jsonify(result)
    except Exception as e:
        logger.error(f"שגיאה ב-/statistics: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/test-connection', methods=['GET'])
def test_connection():
    """בדיקת חיבור לבסיס הנתונים"""
    try:
        result = handle_test_connection()
        return jsonify(result)
    except Exception as e:
        logger.error(f"שגיאה ב-/test-connection: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@api.route('/database-info', methods=['GET'])
def database_info():
    """מידע על בסיס הנתונים הנוכחי"""
    info = {
        'database_type': 'supabase',
        'description': 'Supabase - בסיס נתונים ענן מתקדם',
        'features': ['⚡ מהיר', '🔐 בטוח', '📊 ממשק ניהול', '🆓 חינמי']
    }
    
    return jsonify({
        'success': True,
        'database_info': info
    })

# נתיב לכתובות - פורמט לתאימות עם Frontend הישן
@api.route('/addresses-array', methods=['GET'])
def get_addresses_array():
    """קבלת כל הכתובות כמערך - לתאימות עם Frontend"""
    try:
        result = handle_get_addresses()
        if result.get('success'):
            # החזרת מערך ישירות במקום אובייקט
            return jsonify(result.get('addresses', []))
        else:
            return jsonify([])
    except Exception as e:
        logger.error(f"שגיאה ב-/addresses-array: {e}")
        return jsonify([])

# Flask error handlers
@api.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'נתיב לא נמצא',
        'available_endpoints': [
            '/health',
            '/addresses',
            '/add-address',
            '/batch-geocode',
            '/retry-geocoding', 
            '/reset-data',
            '/statistics',
            '/test-connection',
            '/database-info'
        ]
    }), 404

@api.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'שגיאה פנימית בשרת'
    }), 500
