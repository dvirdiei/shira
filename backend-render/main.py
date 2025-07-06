"""
Backend API - הנוסע המתמיד
Deployed on Render - supports Supabase only!
"""
import sys
import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS

# הגדרת לוגינג
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# בדיקה אם Supabase מוגדר
if os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_SERVICE_KEY'):
    print("🚀 Starting with Supabase!")
    from PYTHON.routes_supabase import api
    database_type = 'supabase'
else:
    print("❌ Supabase configuration missing!")
    print("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY")
    sys.exit(1)
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# הגדרת לוגינג
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# בדיקה אם Supabase מוגדר
if os.getenv('SUPABASE_URL') and os.getenv('SUPABASE_SERVICE_KEY'):
    print("� Starting with Supabase!")
    from PYTHON.routes_supabase import api
    database_type = 'supabase'
else:
    print("❌ Supabase configuration missing!")
    print("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY")
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

# רישום routes - Supabase בלבד
app.register_blueprint(api, url_prefix='/api')
print(f"✅ Supabase API routes registered")

@app.route('/health')
def health_check():
    """בדיקת תקינות השרת"""
    return jsonify({
        'status': 'healthy',
        'database_type': database_type,
        'message': f'Backend working with {database_type.upper()}'
    })

if __name__ == '__main__':
    # בסביבת פיתוח
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    # בסביבת production (Render)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
