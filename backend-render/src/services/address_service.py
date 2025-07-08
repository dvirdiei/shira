# -*- coding: utf-8 -*-
"""
🏠 Address Service - הנוסע המתמיד
שירות ניהול כתובות - לוגיקה עסקית מלאה
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

from ..database.queries import AddressQueries
from ..database.models import Address, AddressValidator, AddressFormatter
from ..database.connection import get_database_client
from ..utils.validators import DataValidator

logger = logging.getLogger(__name__)

class AddressService:
    """שירות ניהול כתובות"""
    
    def __init__(self):
        """אתחול השירות"""
        self.queries = AddressQueries()
        self.validator = AddressValidator()
        self.formatter = AddressFormatter()
        self.supabase = get_database_client()
    
    def get_all_addresses(self) -> List[Dict]:
        """קבלת כל הכתובות"""
        try:
            addresses = self.queries.get_all_addresses()
            return [self.formatter.format_address(addr) for addr in addresses]
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת כתובות: {e}")
            raise
    
    def get_addresses_array(self) -> List[str]:
        """קבלת כתובות כמערך פשוט"""
        try:
            addresses = self.queries.get_all_addresses()
            return [addr.get('address', '') for addr in addresses if addr.get('address')]
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת מערך כתובות: {e}")
            raise
    
    def get_all_addresses_detailed(self) -> List[Dict]:
        """קבלת כל הכתובות עם מידע מפורט"""
        try:
            addresses = self.queries.get_all_addresses()
            detailed_addresses = []
            
            for addr in addresses:
                formatted = self.formatter.format_address_detailed(addr)
                detailed_addresses.append(formatted)
            
            return detailed_addresses
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת כתובות מפורטות: {e}")
            raise
    
    def get_missing_coordinates(self) -> List[Dict]:
        """קבלת כתובות בלי קואורדינטות"""
        try:
            addresses = self.queries.get_missing_coordinates()
            return [self.formatter.format_address(addr) for addr in addresses]
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת כתובות ללא קואורדינטות: {e}")
            raise
    
    def add_single_address(self, data: Dict) -> Dict:
        """הוספת כתובת בודדת"""
        try:
            # אימות נתונים
            if not self.validator.validate_address_data(data):
                return {
                    'success': False,
                    'error': 'נתונים לא תקינים'
                }
            
            # יצירת אובייקט כתובת
            address = Address(
                address=data.get('address', '').strip(),
                city=data.get('city', 'ירושלים').strip(),
                neighborhood=data.get('neighborhood', 'לא ידוע'),
                latitude=data.get('latitude'),
                longitude=data.get('longitude'),
                visited=data.get('visited', False),
                source=data.get('source', 'manual'),
                source_file=data.get('source_file'),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            # הוספה לבסיס הנתונים
            result = self.queries.insert_address(address.to_dict())
            
            if result:
                return {
                    'success': True,
                    'message': 'כתובת נוספה בהצלחה',
                    'address': self.formatter.format_address(result)
                }
            else:
                return {
                    'success': False,
                    'error': 'לא ניתן להוסיף כתובת'
                }
                
        except Exception as e:
            logger.error(f"שגיאה בהוספת כתובת: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def toggle_visited(self, address_id: int, table_type: str = 'addresses') -> Dict:
        """החלפת סטטוס ביקור בשתי הטבלאות"""
        try:
            from ..database.connection import get_database_client
            supabase = get_database_client()
            
            # קביעת הטבלה
            table_name = 'addresses' if table_type == 'addresses' else 'addresses_missing_coordinates'
            
            # קבלת הכתובת הנוכחית
            response = supabase.table(table_name).select('*').eq('id', address_id).execute()
            
            if not response.data:
                return {
                    'success': False,
                    'error': 'כתובת לא נמצאה'
                }
            
            current_address = response.data[0]
            
            # החלפת הסטטוס
            new_visited = not current_address.get('visited', False)
            
            # עדכון בבסיס הנתונים
            update_response = supabase.table(table_name).update({
                'visited': new_visited
            }).eq('id', address_id).execute()
            
            if update_response.data:
                return {
                    'success': True,
                    'message': f'סטטוס ביקור עודכן ל-{"ביקר" if new_visited else "לא ביקר"}',
                    'visited': new_visited
                }
            else:
                return {
                    'success': False,
                    'error': 'לא ניתן לעדכן סטטוס'
                }
                
        except Exception as e:
            logger.error(f"שגיאה בהחלפת סטטוס ביקור: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def delete_address(self, address_id: int, table_type: str = 'addresses') -> Dict:
        """מחיקת כתובת משתי הטבלאות"""
        try:
            from ..database.connection import get_database_client
            supabase = get_database_client()
            
            # קביעת הטבלה
            table_name = 'addresses' if table_type == 'addresses' else 'addresses_missing_coordinates'
            
            # בדיקה שהכתובת קיימת
            response = supabase.table(table_name).select('*').eq('id', address_id).execute()
            
            if not response.data:
                return {
                    'success': False,
                    'error': 'כתובת לא נמצאה'
                }
            
            # מחיקה מבסיס הנתונים
            delete_response = supabase.table(table_name).delete().eq('id', address_id).execute()
            
            if delete_response.data:
                return {
                    'success': True,
                    'message': 'כתובת נמחקה בהצלחה'
                }
            else:
                return {
                    'success': False,
                    'error': 'לא ניתן למחוק כתובת'
                }
                
        except Exception as e:
            logger.error(f"שגיאה במחיקת כתובת: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_addresses_by_city(self, city: str) -> List[Dict]:
        """קבלת כתובות לפי עיר"""
        try:
            addresses = self.queries.get_addresses_by_city(city)
            return [self.formatter.format_address(addr) for addr in addresses]
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת כתובות לפי עיר: {e}")
            raise
    
    def get_addresses_by_neighborhood(self, neighborhood: str) -> List[Dict]:
        """קבלת כתובות לפי שכונה"""
        try:
            addresses = self.queries.get_addresses_by_neighborhood(neighborhood)
            return [self.formatter.format_address(addr) for addr in addresses]
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת כתובות לפי שכונה: {e}")
            raise
    
    def search_addresses(self, query: str) -> List[Dict]:
        """חיפוש כתובות"""
        try:
            addresses = self.queries.search_addresses(query)
            return [self.formatter.format_address(addr) for addr in addresses]
            
        except Exception as e:
            logger.error(f"שגיאה בחיפוש כתובות: {e}")
            raise
            
            return {
                'success': True,
                'addresses': formatted_addresses,
                'count': len(formatted_addresses)
            }
            
        except Exception as e:
            logger.error(f"❌ שגיאה בקבלת כתובות: {e}")
            return {
                'success': False,
                'error': str(e),
                'addresses': []
            }
    
    def get_addresses_array(self) -> List[Dict]:
        """קבלת כתובות כמערך ישירות - לתאימות עם Frontend"""
        try:
            addresses = self.queries.get_all_addresses()
            return [
                AddressFormatter.format_for_frontend(addr) 
                for addr in addresses
            ]
            
        except Exception as e:
            logger.error(f"❌ שגיאה בקבלת מערך כתובות: {e}")
            return []
    
    def get_missing_coordinates(self) -> List[Dict]:
        """קבלת כתובות ללא קואורדינטות"""
        try:
            addresses = self.queries.get_addresses_without_coordinates()
            return [
                AddressFormatter.format_for_frontend(addr) 
                for addr in addresses
            ]
            
        except Exception as e:
            logger.error(f"❌ שגיאה בקבלת כתובות ללא קואורדינטות: {e}")
            return []
    
    def add_single_address(self, address_data: Dict) -> Dict:
        """הוספת כתובת בודדת"""
        try:
            # אימות נתונים בסיסי
            address_text = address_data.get('address', '').strip()
            if not self.validator.validate_address_text(address_text):
                return {
                    'success': False,
                    'error': 'כתובת לא תקינה או חסרה'
                }
            
            # יצירת אובייקט כתובת
            address = Address(
                address=address_text,
                city=address_data.get('city', 'ירושלים'),
                neighborhood=address_data.get('neighborhood', 'לא ידוע'),
                latitude=address_data.get('latitude'),
                longitude=address_data.get('longitude'),
                visited=address_data.get('visited', False),
                source=address_data.get('source', 'manual'),
                source_file=address_data.get('source_file')
            )
            
            # הוספה לבסיס הנתונים
            result = self.queries.insert_address(address)
            
            if result:
                return {
                    'success': True,
                    'message': 'כתובת נוספה בהצלחה',
                    'data': AddressFormatter.format_for_frontend(result)
                }
            else:
                return {
                    'success': False,
                    'error': 'לא ניתן להוסיף כתובת'
                }
                
        except Exception as e:
            logger.error(f"❌ שגיאה בהוספת כתובת: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def add_addresses_batch(self, addresses_data: List[Dict]) -> Dict:
        """הוספת כתובות בבת אחת"""
        try:
            if not addresses_data or not isinstance(addresses_data, list):
                return {
                    'success': False,
                    'error': 'רשימת כתובות ריקה או לא תקינה'
                }
            
            # הכנת רשימת כתובות
            addresses = []
            for addr_item in addresses_data:
                if isinstance(addr_item, dict) and 'address' in addr_item:
                    address_text = addr_item['address'].strip()
                elif isinstance(addr_item, str):
                    address_text = addr_item.strip()
                else:
                    continue
                
                if self.validator.validate_address_text(address_text):
                    address = Address(
                        address=address_text,
                        city=addr_item.get('city', 'ירושלים') if isinstance(addr_item, dict) else 'ירושלים',
                        neighborhood=addr_item.get('neighborhood', 'לא ידוע') if isinstance(addr_item, dict) else 'לא ידוע',
                        visited=False,
                        source='file_upload'
                    )
                    addresses.append(address)
            
            if not addresses:
                return {
                    'success': False,
                    'error': 'לא נמצאו כתובות תקינות'
                }
            
            # הוספה לבסיס הנתונים
            success = self.queries.insert_addresses_batch(addresses)
            
            if success:
                return {
                    'success': True,
                    'message': f'נוספו {len(addresses)} כתובות בהצלחה',
                    'summary': {
                        'found': len(addresses),
                        'not_found': len(addresses_data) - len(addresses),
                        'total': len(addresses_data)
                    },
                    'added_count': len(addresses)
                }
            else:
                return {
                    'success': False,
                    'error': 'לא ניתן להוסיף כתובות לבסיס הנתונים'
                }
                
        except Exception as e:
            logger.error(f"❌ שגיאה בהוספת כתובות: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def toggle_visited_status(self, address_text: str, action: str) -> Dict:
        """עדכון סטטוס ביקור"""
        try:
            if not address_text or not address_text.strip():
                return {
                    'success': False,
                    'message': 'כתובת חסרה'
                }
            
            visited = True if action == 'mark' else False
            success = self.queries.update_visited_status(address_text, visited)
            
            if success:
                return {
                    'success': True,
                    'message': f'כתובת {"סומנה כביקור" if visited else "הוסר הסימון"} בהצלחה'
                }
            else:
                return {
                    'success': False,
                    'message': 'לא ניתן לעדכן את הסטטוס'
                }
                
        except Exception as e:
            logger.error(f"❌ שגיאה בעדכון סטטוס ביקור: {e}")
            return {
                'success': False,
                'message': f'שגיאה בעדכון סטטוס: {str(e)}'
            }
    
    def reset_all_data(self) -> Dict:
        """איפוס כל הנתונים"""
        try:
            success = self.queries.delete_all_addresses()
            
            if success:
                return {
                    'success': True,
                    'message': 'כל הנתונים נמחקו בהצלחה 🗑️'
                }
            else:
                return {
                    'success': False,
                    'error': 'לא ניתן למחוק נתונים'
                }
                
        except Exception as e:
            logger.error(f"❌ שגיאה באיפוס נתונים: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_statistics(self) -> Dict:
        """קבלת סטטיסטיקות"""
        try:
            stats = self.queries.get_statistics()
            return {
                'success': True,
                'statistics': stats
            }
            
        except Exception as e:
            logger.error(f"❌ שגיאה בקבלת סטטיסטיקות: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def find_address_by_name(self, address_name: str, table_type: str = 'addresses') -> Optional[Dict]:
        """חיפוש כתובת לפי שם"""
        try:
            from ..database.connection import get_database_client
            supabase = get_database_client()
            
            table_name = 'addresses' if table_type == 'addresses' else 'addresses_missing_coordinates'
            
            # חיפוש בטבלה הרלוונטית
            response = supabase.table(table_name).select('*').eq('address', address_name).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ שגיאה בחיפוש כתובת {address_name}: {e}")
            return None
