"""
קובץ לניהול כל הנתבים (routes) של האפליקציה
"""
from flask import send_from_directory
from PYTHON.api_handlers import (
    get_addresses_handler,
    get_manual_addresses_handler, 
    get_all_addresses_handler,
    get_missing_coordinates_handler,
    mark_visited_handler
)
import os

def register_routes(app):
    """רושם את כל הנתבים באפליקציה"""
    
    @app.route('/ToHtml/<path:filename>')
    def serve_tohtml_files(filename):
        """מגיש קבצים מתיקיית ToHtml"""
        tohtml_dir = os.path.join(app.root_path, 'ToHtml')
        return send_from_directory(tohtml_dir, filename)

    @app.route('/api/addresses')
    def get_addresses():
        """מחזיר את כל הכתובות עם קואורדינטות מהקובץ CSV"""
        return get_addresses_handler(app.root_path)

    @app.route('/api/manual-addresses')
    def get_manual_addresses():
        """מחזיר כתובות שנוספו באופן ידני"""
        return get_manual_addresses_handler(app.root_path)

    @app.route('/api/all-addresses')
    def get_all_addresses():
        """מחזיר את כל הכתובות - גם מגיאוקודינג וגם ידניות"""
        return get_all_addresses_handler(app.root_path)

    @app.route('/api/missing-coordinates')
    def get_missing_coordinates():
        """מחזיר כתובות ללא קואורדינטות"""
        return get_missing_coordinates_handler(app.root_path)

    @app.route('/api/mark-visited', methods=['POST'])
    def mark_visited():
        """מעדכן את סטטוס הביקור של כתובת"""
        return mark_visited_handler(app.root_path)
