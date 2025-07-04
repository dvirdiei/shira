"""
קובץ לניהול כל הנתבים (routes) של האפליקציה
"""
from flask import send_from_directory
from PYTHON.api_handlers import (
    get_addresses_handler,
    get_manual_addresses_handler, 
    get_all_addresses_handler,
    get_missing_coordinates_handler,
    mark_visited_handler,
    toggle_visit_status_handler,
    delete_address_handler,
    reset_all_data_handler
)
from PYTHON.geocoding_handlers import (
    add_address_handler,
    batch_geocode_handler,
    retry_geocoding_handler
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

    @app.route('/api/toggle-visited', methods=['POST'])
    def toggle_visited():
        """מעדכן או מבטל את סטטוס הביקור של כתובת"""
        return toggle_visit_status_handler(app.root_path)

    @app.route('/api/delete-address', methods=['POST'])
    def delete_address():
        """מוחק כתובת ומעביר לקובץ deleted_addresses.csv"""
        return delete_address_handler(app.root_path)

    # === נתבי גיאוקודינג והוספת כתובות ===
    
    @app.route('/api/add-address', methods=['POST'])
    def add_address():
        """מוסיף כתובת חדשה עם חיפוש קואורדינטות אוטומטי"""
        return add_address_handler(app.root_path)
    
    @app.route('/api/batch-geocode', methods=['POST'])
    def batch_geocode():
        """מעבד כמה כתובות בבת אחת עם גיאוקודינג"""
        return batch_geocode_handler(app.root_path)
    
    @app.route('/api/retry-geocoding', methods=['POST'])
    def retry_geocoding():
        """מנסה שוב לחפש קואורדינטות עבור כתובות שלא נמצאו"""
        return retry_geocoding_handler(app.root_path)
    
    @app.route('/api/reset-all-data', methods=['POST'])
    def reset_all_data():
        """מוחק את כל הנתונים מכל הקבצים"""
        return reset_all_data_handler(app.root_path)
