# -*- coding: utf-8 -*-
"""
🛠️ System Helpers - הנוסע המתמיד
פונקציות עזר כלליות למערכת
"""

import os
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)

class SystemHelpers:
    """פונקציות עזר למערכת"""
    
    @staticmethod
    def get_environment_info() -> Dict:
        """קבל מידע על סביבת העבודה"""
        try:
            return {
                'is_production': bool(os.getenv('RENDER')),
                'is_development': not bool(os.getenv('RENDER')),
                'database_type': 'supabase',
                'python_version': os.sys.version,
                'environment_variables': {
                    'SUPABASE_URL': bool(os.getenv('SUPABASE_URL')),
                    'SUPABASE_SERVICE_KEY': bool(os.getenv('SUPABASE_SERVICE_KEY')),
                    'PORT': os.getenv('PORT', '5000'),
                    'RENDER': bool(os.getenv('RENDER'))
                }
            }
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת מידע סביבה: {e}")
            return {}
    
    @staticmethod
    def generate_unique_id(prefix: str = '') -> str:
        """יצור מזהה יחיד"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_part = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]
            
            if prefix:
                return f"{prefix}_{timestamp}_{unique_part}"
            else:
                return f"{timestamp}_{unique_part}"
                
        except Exception as e:
            logger.error(f"שגיאה ביצירת מזהה יחיד: {e}")
            return str(datetime.now().timestamp())
    
    @staticmethod
    def safe_json_parse(json_string: str) -> Optional[Dict]:
        """פרס JSON בצורה בטוחה"""
        try:
            if not json_string:
                return None
            
            return json.loads(json_string)
            
        except json.JSONDecodeError as e:
            logger.error(f"שגיאה בפרס JSON: {e}")
            return None
        except Exception as e:
            logger.error(f"שגיאה כללית בפרס JSON: {e}")
            return None
    
    @staticmethod
    def safe_json_stringify(data: Any) -> str:
        """המר לJSON בצורה בטוחה"""
        try:
            return json.dumps(data, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"שגיאה בהמרה לJSON: {e}")
            return str(data)
    
    @staticmethod
    def clean_string(text: str) -> str:
        """נקה מחרוזת מתווים לא רצויים"""
        try:
            if not text:
                return ''
            
            # הסר רווחים מיותרים
            text = text.strip()
            
            # הסר תווים מיוחדים
            text = ''.join(char for char in text if char.isprintable())
            
            # הסר רווחים כפולים
            while '  ' in text:
                text = text.replace('  ', ' ')
            
            return text
            
        except Exception as e:
            logger.error(f"שגיאה בניקוי מחרוזת: {e}")
            return str(text)
    
    @staticmethod
    def format_error_message(error: Exception, context: str = '') -> str:
        """פורמט הודעת שגיאה"""
        try:
            error_type = type(error).__name__
            error_message = str(error)
            
            if context:
                return f"[{context}] {error_type}: {error_message}"
            else:
                return f"{error_type}: {error_message}"
                
        except Exception as e:
            logger.error(f"שגיאה בפורמט הודעת שגיאה: {e}")
            return str(error)
    
    @staticmethod
    def log_function_call(func_name: str, params: Dict = None, level: str = 'INFO'):
        """רשום קריאה לפונקציה"""
        try:
            message = f"🔧 {func_name}"
            
            if params:
                # הסתר מידע רגיש
                safe_params = SystemHelpers._sanitize_params(params)
                message += f" - {safe_params}"
            
            if level.upper() == 'DEBUG':
                logger.debug(message)
            elif level.upper() == 'INFO':
                logger.info(message)
            elif level.upper() == 'WARNING':
                logger.warning(message)
            elif level.upper() == 'ERROR':
                logger.error(message)
                
        except Exception as e:
            logger.error(f"שגיאה ברישום קריאה: {e}")
    
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """חשב מרחק בין שתי נקודות גיאוגרפיות (קילומטרים)"""
        try:
            import math
            
            # המרה לרדיאנים
            lat1_rad = math.radians(lat1)
            lon1_rad = math.radians(lon1)
            lat2_rad = math.radians(lat2)
            lon2_rad = math.radians(lon2)
            
            # נוסחת Haversine
            dlat = lat2_rad - lat1_rad
            dlon = lon2_rad - lon1_rad
            
            a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            
            # רדיוס כדור הארץ בקילומטרים
            earth_radius = 6371
            
            return earth_radius * c
            
        except Exception as e:
            logger.error(f"שגיאה בחישוב מרחק: {e}")
            return 0.0
    
    @staticmethod
    def get_file_info(file_path: str) -> Dict:
        """קבל מידע על קובץ"""
        try:
            if not os.path.exists(file_path):
                return {
                    'exists': False,
                    'error': 'קובץ לא קיים'
                }
            
            stat = os.stat(file_path)
            
            return {
                'exists': True,
                'size': stat.st_size,
                'size_mb': round(stat.st_size / (1024 * 1024), 2),
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'is_file': os.path.isfile(file_path),
                'is_directory': os.path.isdir(file_path),
                'readable': os.access(file_path, os.R_OK),
                'writable': os.access(file_path, os.W_OK)
            }
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת מידע קובץ: {e}")
            return {
                'exists': False,
                'error': str(e)
            }
    
    @staticmethod
    def create_backup_filename(original_name: str) -> str:
        """יצור שם קובץ גיבוי"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            if '.' in original_name:
                name, ext = original_name.rsplit('.', 1)
                return f"{name}_backup_{timestamp}.{ext}"
            else:
                return f"{original_name}_backup_{timestamp}"
                
        except Exception as e:
            logger.error(f"שגיאה ביצירת שם קובץ גיבוי: {e}")
            return f"{original_name}_backup"
    
    @staticmethod
    def _sanitize_params(params: Dict) -> Dict:
        """נקה פרמטרים ממידע רגיש"""
        try:
            sanitized = {}
            sensitive_keys = ['password', 'token', 'key', 'secret']
            
            for key, value in params.items():
                if any(sensitive in key.lower() for sensitive in sensitive_keys):
                    sanitized[key] = '***'
                else:
                    sanitized[key] = value
            
            return sanitized
            
        except Exception as e:
            logger.error(f"שגיאה בניקוי פרמטרים: {e}")
            return params


class PerformanceMonitor:
    """מוניטור ביצועים"""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.operation_name = None
    
    def start(self, operation_name: str):
        """התחל מדידה"""
        self.operation_name = operation_name
        self.start_time = datetime.now()
        logger.debug(f"🚀 התחלת מדידה: {operation_name}")
    
    def end(self):
        """סיום מדידה"""
        if not self.start_time:
            logger.warning("מדידה לא התחילה")
            return 0
        
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        logger.info(f"⏱️ {self.operation_name}: {duration:.3f} שניות")
        return duration
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end()
