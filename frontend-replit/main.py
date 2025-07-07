#!/usr/bin/env python3
"""
שרת סטטי פשוט עבור הפרונט אנד ב-Replit
מגיש את קבצי HTML, CSS, JavaScript
"""

import http.server
import socketserver
import os
import sys
from urllib.parse import urlparse

# הגדרת פורט ברירת מחדל - עם fallback לפורטים אחרים
DEFAULT_PORT = int(os.environ.get('PORT', 3000))
FALLBACK_PORTS = [3000, 3001, 3002, 8000, 8080, 5000, 4000]

def find_available_port():
    """מוצא פורט זמין"""
    import socket
    
    for port in FALLBACK_PORTS:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                print(f"✅ פורט {port} זמין")
                return port
        except OSError:
            print(f"❌ פורט {port} תפוס")
            continue
    
    # אם כל הפורטים תפוסים, תן לmערכת לבחור
    print("🔍 מחפש פורט זמין אוטומטית...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    מטפל HTTP מותאם שמוסיף headers נכונים ומטפל בנתיבים
    """
    
    def end_headers(self):
        """הוספת headers אבטחה ו-CORS"""
        # CORS headers לחיבור עם הבאק אנד
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        
        # Security headers
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('X-XSS-Protection', '1; mode=block')
        
        # Cache headers לקבצים סטטיים
        if self.path.endswith(('.css', '.js', '.png', '.jpg', '.ico')):
            self.send_header('Cache-Control', 'public, max-age=86400')  # יום אחד
        else:
            self.send_header('Cache-Control', 'no-cache')
        
        super().end_headers()
    
    def do_GET(self):
        """טיפול בבקשות GET"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        # אם מבקשים נתיב שאינו קובץ, הפנה ל-index.html בתיקיית src
        if path == '/' or not os.path.exists(path.lstrip('/')):
            self.path = '/src/index.html'
        
        return super().do_GET()
    
    def do_OPTIONS(self):
        """טיפול בבקשות OPTIONS (preflight)"""
        self.send_response(200)
        self.end_headers()
    
    def log_message(self, format, *args):
        """לוג מותאם עם צבעים"""
        timestamp = self.log_date_time_string()
        sys.stdout.write(f"🌐 [{timestamp}] {format % args}\n")

def main():
    """פונקציה ראשית להפעלת השרת"""
    try:
        # שינוי לתיקיית העבודה הנכונה (אם נדרש)
        if os.path.exists('frontend-replit'):
            os.chdir('frontend-replit')
            print("📁 עבר לתיקיית frontend-replit")
        
        # מציאת פורט זמין
        PORT = find_available_port()
        
        # יצירת השרת
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print("=" * 60)
            print("🚀 הנוסע המתמיד - שרת פרונט אנד")
            print("=" * 60)
            print(f"🌐 השרת פועל על פורט: {PORT}")
            print(f"🔗 כתובת: http://localhost:{PORT}")
            print("📱 מותאם לטלפון נייד")
            print("🔄 חיבור לבאק אנד: https://shira-bf24.onrender.com")
            print("=" * 60)
            print("📋 קבצים זמינים:")
            
            # הצגת קבצים זמינים
            for root, dirs, files in os.walk('.'):
                for file in files:
                    if file.endswith(('.html', '.css', '.js')):
                        filepath = os.path.join(root, file).replace('\\', '/')
                        print(f"   📄 {filepath}")
            
            print("=" * 60)
            print("⚡ השרת מוכן! לחץ Ctrl+C לעצירה")
            print("=" * 60)
            
            # הפעלת השרת
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n" + "=" * 40)
        print("🛑 השרת נעצר על ידי המשתמש")
        print("👋 להתראות!")
        print("=" * 40)
    except OSError as e:
        if e.errno == 98:  # Address already in use
            print("❌ שגיאה: כל הפורטים תפוסים")
            print("💡 נסה לעצור תהליכים אחרים או לרענן את Replit")
        else:
            print(f"❌ שגיאת מערכת: {e}")
    except Exception as e:
        print(f"❌ שגיאה כללית: {e}")

if __name__ == "__main__":
    main()
