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
    
    def create_tables_if_not_exist(self) -> bool:
        """יצירת הטבלאות אם הן לא קיימות"""
        try:
            # בדיקה אם הטבלאות קיימות (Supabase יוצר אותן אוטומטית אם מוגדרות)
            logger.info("🏗️ בודק/יוצר טבלאות נדרשות...")
            
            # בדיקת טבלת addresses (כתובות עם קואורדינטות)
            result_addresses = self.client.table('addresses').select("*").limit(1).execute()
            logger.info("✅ טבלת addresses קיימת")
            
            # בדיקת טבלת addresses_missing_coordinates (כתובות ללא קואורדינטות)
            result_missing = self.client.table('addresses_missing_coordinates').select("*").limit(1).execute()
            logger.info("✅ טבלת addresses_missing_coordinates קיימת")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ שגיאה ביצירת/בדיקת טבלאות: {e}")
            return False
    
    def insert_address_with_coordinates(self, address: str, lat: float, lon: float, 
                                      neighborhood: str = None, source: str = 'geocoded') -> bool:
        """הוספת כתובת עם קואורדינטות לטבלת addresses"""
        try:
            data = {
                'address': address,
                'lat': lat,
                'lon': lon,
                'neighborhood': neighborhood,
                'visited': False,
                'source': source
            }
            
            result = self.client.table('addresses').insert(data).execute()
            logger.info(f"✅ כתובת נוספה עם קואורדינטות: {address}")
            return True
            
        except Exception as e:
            logger.error(f"❌ שגיאה בהוספת כתובת עם קואורדינטות: {e}")
            return False
    
    def insert_address_without_coordinates(self, address: str, reason: str = 'geocoding_failed') -> bool:
        """הוספת כתובת ללא קואורדינטות לטבלת addresses_missing_coordinates"""
        try:
            data = {
                'address': address,
                'reason': reason,
                'manual_coordinates_needed': True,
                'manual_coordinates_added': False,
                'manual_lat': None,
                'manual_lon': None,
                'manual_neighborhood': None,
                'attempts': 1
            }
            
            result = self.client.table('addresses_missing_coordinates').insert(data).execute()
            logger.info(f"✅ כתובת נוספה ללא קואורדינטות: {address}")
            return True
            
        except Exception as e:
            logger.error(f"❌ שגיאה בהוספת כתובת ללא קואורדינטות: {e}")
            return False
    
    def get_all_addresses_with_coordinates(self) -> list:
        """קבלת כל הכתובות עם קואורדינטות"""
        try:
            result = self.client.table('addresses').select("*").execute()
            logger.info(f"✅ נטענו {len(result.data)} כתובות עם קואורדינטות")
            return result.data
            
        except Exception as e:
            logger.error(f"❌ שגיאה בטעינת כתובות עם קואורדינטות: {e}")
            return []
    
    def get_all_addresses_without_coordinates(self) -> list:
        """קבלת כל הכתובות ללא קואורדינטות"""
        try:
            result = self.client.table('addresses_missing_coordinates').select("*").execute()
            logger.info(f"✅ נטענו {len(result.data)} כתובות ללא קואורדינטות")
            return result.data
            
        except Exception as e:
            logger.error(f"❌ שגיאה בטעינת כתובות ללא קואורדינטות: {e}")
            return []
    
    def move_address_to_coordinates_table(self, missing_id: int, lat: float, lon: float, 
                                        neighborhood: str = None) -> bool:
        """העברת כתובת מטבלת ללא קואורדינטות לטבלת עם קואורדינטות"""
        try:
            # קבלת הכתובת מטבלת ה-missing
            missing_result = self.client.table('addresses_missing_coordinates')\
                .select("*").eq('id', missing_id).execute()
            
            if not missing_result.data:
                logger.error(f"❌ לא נמצאה כתובת עם ID: {missing_id}")
                return False
            
            missing_address = missing_result.data[0]
            
            # הוספה לטבלת addresses
            success = self.insert_address_with_coordinates(
                address=missing_address['address'],
                lat=lat,
                lon=lon,
                neighborhood=neighborhood,
                source='manual'
            )
            
            if success:
                # מחיקה מטבלת ה-missing
                self.client.table('addresses_missing_coordinates')\
                    .delete().eq('id', missing_id).execute()
                logger.info(f"✅ כתובת הועברה בהצלחה: {missing_address['address']}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ שגיאה בהעברת כתובת: {e}")
            return False
    
    def update_address_coordinates(self, address_id: int, lat: float, lon: float, 
                                 neighborhood: str = None) -> bool:
        """עדכון קואורדינטות לכתובת קיימת"""
        try:
            data = {
                'lat': lat,
                'lon': lon,
                'source': 'manual_corrected'
            }
            
            if neighborhood:
                data['neighborhood'] = neighborhood
            
            result = self.client.table('addresses')\
                .update(data).eq('id', address_id).execute()
            
            logger.info(f"✅ קואורדינטות עודכנו לכתובת ID: {address_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ שגיאה בעדכון קואורדינטות: {e}")
            return False
    
    def check_address_exists(self, address: str) -> tuple[bool, str]:
        """בדיקה אם כתובת קיימת באחת מהטבלאות"""
        try:
            # בדיקה בטבלת addresses
            result_with_coords = self.client.table('addresses')\
                .select("*").eq('address', address).execute()
            
            if result_with_coords.data:
                return True, 'with_coordinates'
            
            # בדיקה בטבלת addresses_missing_coordinates
            result_without_coords = self.client.table('addresses_missing_coordinates')\
                .select("*").eq('address', address).execute()
            
            if result_without_coords.data:
                return True, 'without_coordinates'
            
            return False, 'not_found'
            
        except Exception as e:
            logger.error(f"❌ שגיאה בבדיקת קיום כתובת: {e}")
            return False, 'error'
    
    def add_manual_coordinates_to_missing(self, missing_id: int, lat: float, lon: float, 
                                        neighborhood: str = None, added_by: str = None) -> bool:
        """הוספת קואורדינטות ידניות לכתובת בטבלת missing_coordinates"""
        try:
            data = {
                'manual_lat': lat,
                'manual_lon': lon,
                'manual_neighborhood': neighborhood,
                'manual_coordinates_added': True,
                'manual_coordinates_needed': False,
                'manual_added_by': added_by,
                'manual_added_at': 'now()'
            }
            
            result = self.client.table('addresses_missing_coordinates')\
                .update(data).eq('id', missing_id).execute()
            
            logger.info(f"✅ קואורדינטות ידניות נוספו לכתובת ID: {missing_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ שגיאה בהוספת קואורדינטות ידניות: {e}")
            return False
    
    def get_addresses_with_manual_coordinates(self) -> list:
        """קבלת כתובות מטבלת missing_coordinates שיש להן קואורדינטות ידניות"""
        try:
            result = self.client.table('addresses_missing_coordinates')\
                .select("*")\
                .eq('manual_coordinates_added', True)\
                .not_.is_('manual_lat', 'null')\
                .not_.is_('manual_lon', 'null')\
                .execute()
            
            logger.info(f"✅ נטענו {len(result.data)} כתובות עם קואורדינטות ידניות")
            return result.data
            
        except Exception as e:
            logger.error(f"❌ שגיאה בטעינת כתובות עם קואורדינטות ידניות: {e}")
            return []
    
    def get_addresses_needing_manual_coordinates(self) -> list:
        """קבלת כתובות שצריכות קואורדינטות ידניות"""
        try:
            result = self.client.table('addresses_missing_coordinates')\
                .select("*")\
                .eq('manual_coordinates_needed', True)\
                .eq('manual_coordinates_added', False)\
                .execute()
            
            logger.info(f"✅ נטענו {len(result.data)} כתובות שצריכות קואורדינטות ידניות")
            return result.data
            
        except Exception as e:
            logger.error(f"❌ שגיאה בטעינת כתובות שצריכות קואורדינטות ידניות: {e}")
            return []
    
    def get_all_addresses_for_map(self) -> list:
        """קבלת כל הכתובות עם קואורדינטות למפה (משתי הטבלאות)"""
        try:
            # כתובות רגילות
            regular_addresses = self.get_all_addresses_with_coordinates()
            
            # כתובות עם קואורדינטות ידניות
            manual_addresses = self.get_addresses_with_manual_coordinates()
            
            # המרת כתובות ידניות לפורמט אחיד
            formatted_manual = []
            for addr in manual_addresses:
                formatted_manual.append({
                    'id': f"manual_{addr['id']}",
                    'address': addr['address'],
                    'lat': addr['manual_lat'],
                    'lon': addr['manual_lon'],
                    'neighborhood': addr['manual_neighborhood'],
                    'visited': False,
                    'source': 'manual',
                    'created_at': addr['created_at'],
                    'updated_at': addr['updated_at']
                })
            
            all_addresses = regular_addresses + formatted_manual
            logger.info(f"✅ נטענו {len(all_addresses)} כתובות למפה ({len(regular_addresses)} רגילות + {len(formatted_manual)} ידניות)")
            return all_addresses
            
        except Exception as e:
            logger.error(f"❌ שגיאה בטעינת כל הכתובות למפה: {e}")
            return []
    
    def process_new_address(self, address: str, geocoding_service) -> tuple[bool, str]:
        """עיבוד כתובת חדשה - נסיון geocoding והכנסה לטבלה המתאימה"""
        try:
            # בדיקה אם הכתובת כבר קיימת
            exists, location = self.check_address_exists(address)
            if exists:
                logger.info(f"🔄 כתובת כבר קיימת: {address} ב-{location}")
                return False, f"כתובת כבר קיימת ב-{location}"
            
            # ניסיון geocoding
            coords = geocoding_service.geocode_address(address)
            
            if coords and coords.get('lat') and coords.get('lon'):
                # הצלחה - הוספה לטבלת addresses
                success = self.insert_address_with_coordinates(
                    address=address,
                    lat=coords['lat'],
                    lon=coords['lon'],
                    neighborhood=coords.get('neighborhood'),
                    source='geocoded'
                )
                
                if success:
                    logger.info(f"✅ כתובת נוספה בהצלחה עם קואורדינטות: {address}")
                    return True, "נוספה עם קואורדינטות"
                else:
                    return False, "שגיאה בהוספה לטבלה"
            else:
                # כישלון - הוספה לטבלת missing_coordinates
                success = self.insert_address_without_coordinates(
                    address=address,
                    reason='geocoding_failed'
                )
                
                if success:
                    logger.info(f"⚠️ כתובת נוספה ללא קואורדינטות: {address}")
                    return True, "נוספה ללא קואורדינטות - דרושה הזנה ידנית"
                else:
                    return False, "שגיאה בהוספה לטבלה"
                    
        except Exception as e:
            logger.error(f"❌ שגיאה בעיבוד כתובת חדשה: {e}")
            return False, f"שגיאה: {str(e)}"

# יצירת instance גלובלי
db_connection = DatabaseConnection()

def get_database_client() -> Client:
    """פונקציה עזר לקבלת ה-client"""
    return db_connection.client

def test_database_connection() -> bool:
    """פונקציה עזר לבדיקת חיבור"""
    return db_connection.test_connection()

# פונקציות נוחות לעבודה עם הטבלאות החדשות
def add_address_with_coordinates(address: str, lat: float, lon: float, 
                               neighborhood: str = None, source: str = 'geocoded') -> bool:
    """הוספת כתובת עם קואורדינטות"""
    return db_connection.insert_address_with_coordinates(address, lat, lon, neighborhood, source)

def add_address_without_coordinates(address: str, reason: str = 'geocoding_failed') -> bool:
    """הוספת כתובת ללא קואורדינטות"""
    return db_connection.insert_address_without_coordinates(address, reason)

def get_addresses_with_coordinates() -> list:
    """קבלת כל הכתובות עם קואורדינטות"""
    return db_connection.get_all_addresses_with_coordinates()

def get_addresses_without_coordinates() -> list:
    """קבלת כל הכתובות ללא קואורדינטות"""
    return db_connection.get_all_addresses_without_coordinates()

def move_missing_to_coordinates(missing_id: int, lat: float, lon: float, 
                              neighborhood: str = None) -> bool:
    """העברת כתובת מטבלת ללא קואורדינטות לטבלת עם קואורדינטות"""
    return db_connection.move_address_to_coordinates_table(missing_id, lat, lon, neighborhood)

def check_if_address_exists(address: str) -> tuple[bool, str]:
    """בדיקה אם כתובת קיימת"""
    return db_connection.check_address_exists(address)

# פונקציות נוחות חדשות לקואורדינטות ידניות
def add_manual_coordinates(missing_id: int, lat: float, lon: float, 
                          neighborhood: str = None, added_by: str = None) -> bool:
    """הוספת קואורדינטות ידניות לכתובת"""
    return db_connection.add_manual_coordinates_to_missing(missing_id, lat, lon, neighborhood, added_by)

def get_addresses_with_manual_coordinates() -> list:
    """קבלת כתובות עם קואורדינטות ידניות"""
    return db_connection.get_addresses_with_manual_coordinates()

def get_addresses_needing_manual_coordinates() -> list:
    """קבלת כתובות שצריכות קואורדינטות ידניות"""
    return db_connection.get_addresses_needing_manual_coordinates()

def get_all_addresses_for_map() -> list:
    """קבלת כל הכתובות למפה (משתי הטבלאות)"""
    return db_connection.get_all_addresses_for_map()

def process_new_address(address: str, geocoding_service) -> tuple[bool, str]:
    """עיבוד כתובת חדשה עם geocoding אוטומטי"""
    return db_connection.process_new_address(address, geocoding_service)
