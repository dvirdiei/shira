# -*- coding: utf-8 -*-
"""
Database Connection Manager
מנהל חיבורים לSupabase
"""

import os
import logging
from supabase import create_client, Client
from typing import Optional

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """מנהל חיבור יחיד ל-Supabase"""
    
    _instance: Optional['DatabaseConnection'] = None
    _client: Optional[Client] = None
    
    def __new__(cls) -> 'DatabaseConnection':
        """Singleton pattern - חיבור יחיד בלבד"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """אתחול החיבור"""
        if self._client is None:
            self._initialize_connection()
    
    def _initialize_connection(self) -> None:
        """יצירת חיבור לSupabase"""
        try:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_SERVICE_KEY')
            
            if not url or not key:
                raise ValueError("חסרים פרטי חיבור ל-Supabase ב-.env")
            
            self._client = create_client(url, key)
            logger.info("✅ חיבור ל-Supabase הוקם בהצלחה")
            
        except Exception as e:
            logger.error(f"❌ שגיאה בחיבור ל-Supabase: {e}")
            raise
    
    @property
    def client(self) -> Client:
        """החזרת ה-client של Supabase"""
        if self._client is None:
            self._initialize_connection()
        return self._client
    
    def test_connection(self) -> bool:
        """בדיקת חיבור לSupabase"""
        try:
            # נסה לקרוא מטבלת addresses
            result = self.client.table('addresses').select("*").limit(1).execute()
            logger.info("✅ בדיקת חיבור הצליחה")
            return True
        except Exception as e:
            logger.error(f"❌ בדיקת חיבור נכשלה: {e}")
            return False
    
    def close_connection(self) -> None:
        """סגירת החיבור"""
        # Supabase client לא צריך סגירה מפורשת
        logger.info("🔌 חיבור Supabase נסגר")

# יצירת instance גלובלי
db_connection = DatabaseConnection()

def get_database_client() -> Client:
    """פונקציה עזר לקבלת ה-client"""
    return db_connection.client

def test_database_connection() -> bool:
    """פונקציה עזר לבדיקת חיבור"""
    return db_connection.test_connection()
