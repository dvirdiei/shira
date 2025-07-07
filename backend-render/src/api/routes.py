# -*- coding: utf-8 -*-
"""
🛣️ API Routes - הנוסע המתמיד
כל ה-endpoints מוגדרים כאן בצורה מסודרת
"""

import os
import logging
from flask import jsonify, request, Blueprint

# Import handlers
from .handlers import (
    AddressHandlers,
    GeocodingHandlers,
    DataHandlers,
    SystemHandlers
)

logger = logging.getLogger(__name__)

# יצירת Blueprint
api = Blueprint('api', __name__)

# ===== SYSTEM ROUTES =====
@api.route('/health', methods=['GET'])
def health_check():
    """בדיקת תקינות השרת"""
    return SystemHandlers.health_check()

@api.route('/test-connection', methods=['GET'])
def test_connection():
    """בדיקת חיבור לבסיס הנתונים"""
    return SystemHandlers.test_connection()

# ===== ADDRESS ROUTES =====
@api.route('/addresses', methods=['GET'])
def get_addresses():
    """קבלת כל הכתובות"""
    return AddressHandlers.get_all_addresses()

@api.route('/addresses-array', methods=['GET'])
def get_addresses_array():
    """קבלת כתובות כמערך"""
    return AddressHandlers.get_addresses_array()

@api.route('/all-addresses', methods=['GET'])
def get_all_addresses():
    """קבלת כל הכתובות עם מידע מלא"""
    return AddressHandlers.get_all_addresses_detailed()

@api.route('/missing-coordinates', methods=['GET'])
def get_missing_coordinates():
    """קבלת כתובות בלי קואורדינטות"""
    return AddressHandlers.get_missing_coordinates()

@api.route('/add-address', methods=['POST'])
def add_address():
    """הוספת כתובת בודדת"""
    return AddressHandlers.add_single_address()

@api.route('/toggle-visited', methods=['POST'])
def toggle_visited():
    """החלפת סטטוס ביקור"""
    return AddressHandlers.toggle_visited()

@api.route('/delete-address', methods=['POST'])
def delete_address():
    """מחיקת כתובת"""
    return AddressHandlers.delete_address()

# ===== GEOCODING ROUTES =====
@api.route('/batch-geocode', methods=['POST'])
def batch_geocode():
    """הוספת כתובות בבת אחת עם גיאוקודינג"""
    return GeocodingHandlers.batch_geocode()

@api.route('/retry-geocoding', methods=['POST'])
def retry_geocoding():
    """ניסיון חוזר לגיאוקודינג"""
    return GeocodingHandlers.retry_geocoding()

# ===== DATA MANAGEMENT ROUTES =====
@api.route('/reset-data', methods=['POST'])
def reset_data():
    """איפוס נתונים"""
    return DataHandlers.reset_data()

@api.route('/reset-all-data', methods=['POST'])
def reset_all_data():
    """איפוס כל הנתונים"""
    return DataHandlers.reset_all_data()

@api.route('/statistics', methods=['GET'])
def get_statistics():
    """קבלת סטטיסטיקות"""
    return DataHandlers.get_statistics()

# ===== ERROR HANDLERS =====
@api.errorhandler(404)
def not_found(error):
    """טיפול בנתיב לא קיים"""
    return jsonify({
        'success': False,
        'error': 'נתיב לא קיים',
        'message': 'הנתיב המבוקש לא נמצא'
    }), 404

@api.errorhandler(500)
def internal_error(error):
    """טיפול בשגיאה פנימית"""
    logger.error(f"שגיאה פנימית: {error}")
    return jsonify({
        'success': False,
        'error': 'שגיאה פנימית בשרת',
        'message': 'אירעה שגיאה בשרת'
    }), 500

@api.errorhandler(400)
def bad_request(error):
    """טיפול בבקשה לא תקינה"""
    return jsonify({
        'success': False,
        'error': 'בקשה לא תקינה',
        'message': 'הבקשה אינה תקינה'
    }), 400

# ===== INFO ROUTE =====
@api.route('/info', methods=['GET'])
def api_info():
    """מידע על ה-API"""
    return jsonify({
        'service': 'הנוסע המתמיד Backend API',
        'version': '2.0',
        'database_type': 'supabase',
        'endpoints': [
            # System
            '/api/health',
            '/api/test-connection',
            '/api/info',
            
            # Addresses
            '/api/addresses',
            '/api/addresses-array',
            '/api/all-addresses',
            '/api/missing-coordinates',
            '/api/add-address',
            '/api/toggle-visited',
            '/api/delete-address',
            
            # Geocoding
            '/api/batch-geocode',
            '/api/retry-geocoding',
            
            # Data Management
            '/api/reset-data',
            '/api/reset-all-data',
            '/api/statistics'
        ],
        'description': 'API Server running with Supabase database'
    })
