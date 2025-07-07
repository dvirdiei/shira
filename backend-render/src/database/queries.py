# -*- coding: utf-8 -*-
"""
Database Queries
שאילתות מובנות לבסיס הנתונים
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime

from .connection import get_database_client
from .models import Address, AddressFormatter

logger = logging.getLogger(__name__)

class AddressQueries:
    """מחלקה לשאילתות כתובות"""
    
    def __init__(self):
        self.client = get_database_client()
    
    def get_all_addresses(self) -> List[Address]:
        """קבלת כל הכתובות"""
        try:
            result = self.client.table('addresses').select("*").execute()
            
            if result.data:
                addresses = []
                for row in result.data:
                    # התאמת שמות עמודות
                    address_data = {
                        'id': row.get('id'),
                        'address': row.get('address', ''),
                        'city': row.get('city', 'ירושלים'),
                        'neighborhood': row.get('neighborhood', row.get('city', 'לא ידוע')),
                        'latitude': row.get('latitude'),
                        'longitude': row.get('longitude'),
                        'visited': row.get('visited', False),
                        'source': row.get('source', row.get('source_file', 'manual')),
                        'source_file': row.get('source_file'),
                        'created_at': row.get('created_at'),
                        'updated_at': row.get('updated_at')
                    }
                    addresses.append(Address.from_dict(address_data))
                
                logger.info(f"✅ נמצאו {len(addresses)} כתובות")
                return addresses
            else:
                logger.info("ℹ️ לא נמצאו כתובות")
                return []
                
        except Exception as e:
            logger.error(f"❌ שגיאה בקריאת כתובות: {e}")
            return []
    
    def get_addresses_without_coordinates(self) -> List[Address]:
        """קבלת כתובות ללא קואורדינטות"""
        try:
            result = self.client.table('addresses').select("*").or_("latitude.is.null,longitude.is.null").execute()
            
            addresses = []
            if result.data:
                for row in result.data:
                    address_data = self._format_row_to_address_data(row)
                    addresses.append(Address.from_dict(address_data))
                
                logger.info(f"✅ נמצאו {len(addresses)} כתובות ללא קואורדינטות")
            
            return addresses
            
        except Exception as e:
            logger.error(f"❌ שגיאה בקריאת כתובות ללא קואורדינטות: {e}")
            return []
    
    def insert_address(self, address: Address) -> Optional[Address]:
        """הוספת כתובת בודדת"""
        try:
            insert_data = {
                'address': address.address,
                'city': address.city,
                'neighborhood': address.neighborhood,
                'latitude': address.latitude,
                'longitude': address.longitude,
                'visited': address.visited,
                'source': address.source,
                'source_file': address.source_file
            }
            
            # הסרת שדות None
            insert_data = {k: v for k, v in insert_data.items() if v is not None}
            
            result = self.client.table('addresses').insert(insert_data).execute()
            
            if result.data:
                new_address_data = self._format_row_to_address_data(result.data[0])
                logger.info(f"✅ כתובת נוספה: {address.address}")
                return Address.from_dict(new_address_data)
            else:
                logger.error(f"❌ לא ניתן להוסיף כתובת: {address.address}")
                return None
                
        except Exception as e:
            logger.error(f"❌ שגיאה בהוספת כתובת: {e}")
            return None
    
    def insert_addresses_batch(self, addresses: List[Address]) -> bool:
        """הוספת כתובות בבת אחת"""
        try:
            insert_data = []
            for address in addresses:
                row_data = {
                    'address': address.address,
                    'city': address.city,
                    'neighborhood': address.neighborhood,
                    'latitude': address.latitude,
                    'longitude': address.longitude,
                    'visited': address.visited,
                    'source': address.source,
                    'source_file': address.source_file
                }
                # הסרת שדות None
                row_data = {k: v for k, v in row_data.items() if v is not None}
                insert_data.append(row_data)
            
            result = self.client.table('addresses').insert(insert_data).execute()
            
            if result.data:
                logger.info(f"✅ הוכנסו {len(result.data)} כתובות בהצלחה")
                return True
            else:
                logger.error("❌ לא הוכנסו כתובות")
                return False
                
        except Exception as e:
            logger.error(f"❌ שגיאה בהכנסת כתובות: {e}")
            return False
    
    def get_address_by_id(self, address_id: int) -> Optional[Dict]:
        """קבלת כתובת לפי מזהה"""
        try:
            result = self.client.table('addresses').select("*").eq('id', address_id).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת כתובת לפי מזהה {address_id}: {e}")
            return None
    
    def get_missing_coordinates(self) -> List[Dict]:
        """קבלת כתובות בלי קואורדינטות"""
        try:
            result = self.client.table('addresses').select("*").or_('latitude.is.null,longitude.is.null').execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת כתובות ללא קואורדינטות: {e}")
            return []
    
    def get_addresses_by_city(self, city: str) -> List[Dict]:
        """קבלת כתובות לפי עיר"""
        try:
            result = self.client.table('addresses').select("*").eq('city', city).execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת כתובות לפי עיר {city}: {e}")
            return []
    
    def get_addresses_by_neighborhood(self, neighborhood: str) -> List[Dict]:
        """קבלת כתובות לפי שכונה"""
        try:
            result = self.client.table('addresses').select("*").eq('neighborhood', neighborhood).execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת כתובות לפי שכונה {neighborhood}: {e}")
            return []
    
    def search_addresses(self, query: str) -> List[Dict]:
        """חיפוש כתובות"""
        try:
            result = self.client.table('addresses').select("*").or_(
                f'address.ilike.%{query}%,'
                f'city.ilike.%{query}%,'
                f'neighborhood.ilike.%{query}%'
            ).execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"שגיאה בחיפוש כתובות עם השאילתה {query}: {e}")
            return []
    
    def update_visited_status(self, address_id: int, visited: bool) -> bool:
        """עדכון סטטוס ביקור"""
        try:
            updates = {
                'visited': visited,
                'updated_at': datetime.now().isoformat()
            }
            result = self.client.table('addresses').update(updates).eq('id', address_id).execute()
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"שגיאה בעדכון סטטוס ביקור {address_id}: {e}")
            return False
    
    def update_coordinates(self, address_id: int, latitude: float, longitude: float) -> bool:
        """עדכון קואורדינטות"""
        try:
            updates = {
                'latitude': latitude,
                'longitude': longitude,
                'updated_at': datetime.now().isoformat()
            }
            result = self.client.table('addresses').update(updates).eq('id', address_id).execute()
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"שגיאה בעדכון קואורדינטות {address_id}: {e}")
            return False
    
    def delete_all_addresses(self) -> bool:
        """מחיקת כל הכתובות"""
        try:
            result = self.client.table('addresses').delete().neq('id', 0).execute()
            return True
            
        except Exception as e:
            logger.error(f"שגיאה במחיקת כל הכתובות: {e}")
            return False
    
    def address_exists(self, address: str) -> bool:
        """בדיקה אם כתובת כבר קיימת"""
        try:
            result = self.client.table('addresses').select('id').eq('address', address).execute()
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"שגיאה בבדיקת קיום כתובת {address}: {e}")
            return False
    
    def _format_row_to_address_data(self, row: Dict) -> Dict:
        """המרת שורה מהDB למבנה Address"""
        return {
            'id': row.get('id'),
            'address': row.get('address', ''),
            'city': row.get('city', 'ירושלים'),
            'neighborhood': row.get('neighborhood', row.get('city', 'לא ידוע')),
            'latitude': row.get('latitude'),
            'longitude': row.get('longitude'),
            'visited': row.get('visited', False),
            'source': row.get('source', row.get('source_file', 'manual')),
            'source_file': row.get('source_file'),
            'created_at': row.get('created_at'),
            'updated_at': row.get('updated_at')
        }
