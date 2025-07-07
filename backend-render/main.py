"""
🚀 Backend API - הנוסע המתמיד
Deployed on Render - supports Supabase only!
מבנה חדש מאורגן עם שכבות: API, Services, Database, Utils
"""
import sys
import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# טעינת משתני סביבה מקובץ .env
load_dotenv()

# הגדרת לוגינג
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# בדיקה אם Supabase מוגדר
if os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_SERVICE_KEY'):
    logger.info("🚀 Starting with Supabase!")
    # Import the new organized API
    from src.api.routes import api
    database_type = 'supabase'
else:
    logger.error("❌ Supabase configuration missing!")
    logger.error("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY")
    sys.exit(1)

# יצירת אפליקציית Flask
app = Flask(__name__)

# הפעלת CORS לחיבור עם Frontend ב-Replit
CORS(app, origins=['*'])  # בproduction כדאי להגביל לדומיין ספציפי

# הגדרת headers לכל תגובה
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

@app.route('/')
def home():
    """דף הבית של ה-Backend API"""
    return jsonify({
        'service': 'הנוסע המתמיד Backend API',
        'version': '2.0',
        'status': 'online',
        'database_type': database_type,
        'endpoints': [
            '/api/health',
            '/api/addresses',
            '/api/addresses-array',
            '/api/all-addresses',
            '/api/missing-coordinates',
            '/api/add-address',
            '/api/batch-geocode',
            '/api/toggle-visited',
            '/api/delete-address',
            '/api/reset-data',
            '/api/reset-all-data',
            '/api/statistics',
            '/api/test-connection'
        ],
        'description': f'API Server running with {database_type.upper()} database'
    })

# רישום routes - מבנה חדש מאורגן
app.register_blueprint(api, url_prefix='/api')
logger.info("✅ New organized API routes registered")

@app.route('/health')
def health_check():
    """בדיקת תקינות השרת"""
    return jsonify({
        'status': 'healthy',
        'database_type': database_type,
        'message': f'Backend working with {database_type.upper()}',
        'version': '2.0 - Organized Structure'
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = not os.environ.get('RENDER')  # debug רק בפיתוח
    
    logger.info(f"🚀 Starting Flask server on port {port}")
    logger.info(f"📊 Database: {database_type.upper()}")
    logger.info(f"🌐 Environment: {'Production' if os.getenv('RENDER') else 'Development'}")
    logger.info(f"🏗️ Architecture: Organized Backend Structure v2.0")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
