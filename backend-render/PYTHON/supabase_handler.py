# -*- coding: utf-8 -*-
"""
Supabase Database Handler for הנוסע המתמיד
מטפל בכל פעולות בסיס הנתונים עם Supabase
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
from supabase import create_client, Client
import pandas as pd
from datetime import datetime

# הגדרת לוגינג
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseHandler:
    """מטפל בכל פעולות Supabase"""
    
    def __init__(self):
        """אתחול חיבור ל-Supabase"""
        self.url = os.getenv('SUPABASE_URL')
        self.key = os.getenv('SUPABASE_SERVICE_KEY')
        
        if not self.url or not self.key:
            raise ValueError("חסרים פרטי חיבור ל-Supabase ב-.env")
        
        try:
            self.supabase: Client = create_client(self.url, self.key)
            logger.info("חיבור ל-Supabase הצלח ✅")
        except Exception as e:
            logger.error(f"שגיאה בחיבור ל-Supabase: {e}")
            raise
    
    def test_connection(self) -> bool:
        """בדיקת חיבור ל-Supabase"""
        try:
            # נסה לקרוא מטבלת addresses (גם אם היא ריקה)
            result = self.supabase.table('addresses').select("*").limit(1).execute()
            logger.info("בדיקת חיבור הצליחה ✅")
            return True
        except Exception as e:
            logger.error(f"בדיקת חיבור נכשלה: {e}")
            return False
    
    def create_tables(self) -> bool:
        """יצירת הטבלאות הנדרשות"""
        try:
            # Supabase יוצר טבלאות דרך SQL
            # זה יעשה דרך ממשק הניהול או migration script
            logger.info("יצירת טבלאות - יש לעשות דרך Supabase Dashboard")
            return True
        except Exception as e:
            logger.error(f"שגיאה ביצירת טבלאות: {e}")
            return False
    
    def insert_addresses_batch(self, addresses: List[Dict]) -> bool:
        """הכנסת כתובות בקבוצות"""
        try:
            # Supabase מתמודד טוב עם batch inserts
            result = self.supabase.table('addresses').insert(addresses).execute()
            
            if result.data:
                logger.info(f"הוכנסו {len(result.data)} כתובות בהצלחה ✅")
                return True
            else:
                logger.error("לא הוכנסו כתובות")
                return False
                
        except Exception as e:
            logger.error(f"שגיאה בהכנסת כתובות: {e}")
            return False
    
    def get_all_addresses(self) -> List[Dict]:
        """קריאת כל הכתובות"""
        try:
            result = self.supabase.table('addresses').select("*").execute()
            
            if result.data:
                logger.info(f"נמצאו {len(result.data)} כתובות")
                return result.data
            else:
                logger.info("לא נמצאו כתובות")
                return []
                
        except Exception as e:
            logger.error(f"שגיאה בקריאת כתובות: {e}")
            return []
    
    def get_addresses_without_coordinates(self) -> List[Dict]:
        """קריאת כתובות ללא קואורדינטות"""
        try:
            result = self.supabase.table('addresses')\
                .select("*")\
                .is_('latitude', 'null')\
                .execute()
            
            if result.data:
                logger.info(f"נמצאו {len(result.data)} כתובות ללא קואורדינטות")
                return result.data
            else:
                logger.info("כל הכתובות כבר עם קואורדינטות ✅")
                return []
                
        except Exception as e:
            logger.error(f"שגיאה בחיפוש כתובות ללא קואורדינטות: {e}")
            return []
    
    def update_address_coordinates(self, address_id: int, latitude: float, longitude: float) -> bool:
        """עדכון קואורדינטות לכתובת"""
        try:
            result = self.supabase.table('addresses')\
                .update({
                    'latitude': latitude,
                    'longitude': longitude,
                    'geocoded_at': datetime.now().isoformat()
                })\
                .eq('id', address_id)\
                .execute()
            
            if result.data:
                return True
            else:
                logger.error(f"לא ניתן לעדכן כתובת {address_id}")
                return False
                
        except Exception as e:
            logger.error(f"שגיאה בעדכון קואורדינטות: {e}")
            return False
    
    def add_single_address(self, address_data: Dict) -> Optional[Dict]:
        """הוספת כתובת בודדת"""
        try:
            result = self.supabase.table('addresses').insert(address_data).execute()
            
            if result.data:
                logger.info(f"נוספה כתובת: {address_data.get('address', 'לא ידוע')}")
                return result.data[0]
            else:
                logger.error("לא ניתן להוסיף כתובת")
                return None
                
        except Exception as e:
            logger.error(f"שגיאה בהוספת כתובת: {e}")
            return None
    
    def delete_all_addresses(self) -> bool:
        """מחיקת כל הכתובות"""
        try:
            # קודם נספור כמה יש
            count_result = self.supabase.table('addresses').select("id").execute()
            count = len(count_result.data) if count_result.data else 0
            
            if count == 0:
                logger.info("אין כתובות למחיקה")
                return True
            
            # מחיקת הכל
            result = self.supabase.table('addresses').delete().neq('id', 0).execute()
            
            logger.info(f"נמחקו כל הכתובות ({count}) ✅")
            return True
            
        except Exception as e:
            logger.error(f"שגיאה במחיקת כתובות: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """קבלת סטטיסטיקות"""
        try:
            # ספירת כל הכתובות
            all_result = self.supabase.table('addresses').select("id").execute()
            total_addresses = len(all_result.data) if all_result.data else 0
            
            # ספירת כתובות עם קואורדינטות
            geocoded_result = self.supabase.table('addresses')\
                .select("id")\
                .not_.is_('latitude', 'null')\
                .execute()
            geocoded_addresses = len(geocoded_result.data) if geocoded_result.data else 0
            
            # חישוב אחוזים
            geocoded_percentage = (geocoded_addresses / total_addresses * 100) if total_addresses > 0 else 0
            
            stats = {
                'total_addresses': total_addresses,
                'geocoded_addresses': geocoded_addresses,
                'pending_geocoding': total_addresses - geocoded_addresses,
                'geocoded_percentage': round(geocoded_percentage, 1)
            }
            
            logger.info(f"סטטיסטיקות: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת סטטיסטיקות: {e}")
            return {
                'total_addresses': 0,
                'geocoded_addresses': 0,
                'pending_geocoding': 0,
                'geocoded_percentage': 0
            }

# יצירת instance גלובלי
supabase_handler = None

def get_supabase_handler() -> SupabaseHandler:
    """קבלת handler גלובלי"""
    global supabase_handler
    if supabase_handler is None:
        supabase_handler = SupabaseHandler()
    return supabase_handler

def test_supabase_connection() -> bool:
    """פונקציה לבדיקת חיבור מהירה"""
    try:
        handler = get_supabase_handler()
        return handler.test_connection()
    except Exception as e:
        logger.error(f"בדיקת חיבור נכשלה: {e}")
        return False
