"""
Backend API Server for הנוסע המתמיד
Deployed on Render - serves data to Frontend on Replit
"""
from flask import Flask, render_template, jsonify
from flask_cors import CORS
from PYTHON.routes import register_routes
import os

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
        'version': '1.0',
        'status': 'online',
        'endpoints': [
            '/api/all-addresses',
            '/api/missing-coordinates', 
            '/api/toggle-visited',
            '/api/delete-address'
        ],
        'frontend': 'Connect from Replit Frontend',
        'message': 'Backend מוכן לשירות! 🚀'
    })

@app.route('/health')
def health_check():
    """בדיקת תקינות השרת"""
    return jsonify({
        'status': 'healthy',
        'message': 'Backend working properly'
    })

# רישום כל הנתבים
register_routes(app)

if __name__ == '__main__':
    # בסביבת פיתוח
    app.run(host='0.0.0.0', port=5000, debug=True)
else:
    # בסביבת production (Render)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
