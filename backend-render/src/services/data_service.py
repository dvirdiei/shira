# -*- coding: utf-8 -*-
"""
📊 Data Service - הנוסע המתמיד
שירות ניהול נתונים - איפוס, סטטיסטיקות, ובדיקות
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

from ..database.queries import AddressQueries
from ..database.models import Address, AddressValidator, AddressFormatter

logger = logging.getLogger(__name__)

class DataService:
    """שירות ניהול נתונים"""
    
    def __init__(self):
        """אתחול השירות"""
        self.queries = AddressQueries()
        self.validator = AddressValidator()
        self.formatter = AddressFormatter()
    
    def get_statistics(self) -> Dict:
        """קבלת סטטיסטיקות מפורטות"""
        try:
            stats = {
                'success': True,
                'timestamp': datetime.now().isoformat(),
                'database_type': 'supabase',
                'data': {}
            }
            
            # סטטיסטיקות בסיסיות
            all_addresses = self.queries.get_all_addresses()
            stats['data']['total_addresses'] = len(all_addresses)
            
            # סטטיסטיקות לפי סטטוס
            visited_count = len([addr for addr in all_addresses if addr.get('visited', False)])
            stats['data']['visited_addresses'] = visited_count
            stats['data']['unvisited_addresses'] = len(all_addresses) - visited_count
            
            # סטטיסטיקות גיאוקודינג
            geocoded_count = len([addr for addr in all_addresses 
                                if addr.get('latitude') and addr.get('longitude')])
            stats['data']['geocoded_addresses'] = geocoded_count
            stats['data']['missing_coordinates'] = len(all_addresses) - geocoded_count
            
            # סטטיסטיקות לפי עיר
            cities = {}
            for addr in all_addresses:
                city = addr.get('city', 'לא ידוע')
                cities[city] = cities.get(city, 0) + 1
            stats['data']['cities'] = cities
            
            # סטטיסטיקות לפי שכונה
            neighborhoods = {}
            for addr in all_addresses:
                neighborhood = addr.get('neighborhood', 'לא ידוע')
                neighborhoods[neighborhood] = neighborhoods.get(neighborhood, 0) + 1
            stats['data']['neighborhoods'] = neighborhoods
            
            # סטטיסטיקות לפי מקור
            sources = {}
            for addr in all_addresses:
                source = addr.get('source', 'לא ידוע')
                sources[source] = sources.get(source, 0) + 1
            stats['data']['sources'] = sources
            
            # אחוזים
            if len(all_addresses) > 0:
                stats['data']['percentages'] = {
                    'visited': round((visited_count / len(all_addresses)) * 100, 2),
                    'geocoded': round((geocoded_count / len(all_addresses)) * 100, 2)
                }
            else:
                stats['data']['percentages'] = {
                    'visited': 0,
                    'geocoded': 0
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת סטטיסטיקות: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': {}
            }
    
    def reset_data(self) -> Dict:
        """איפוס נתונים חלקי - מחיקת כל הכתובות"""
        try:
            # קבל מספר הכתובות לפני המחיקה
            addresses_before = self.queries.get_all_addresses()
            count_before = len(addresses_before)
            
            # מחק את כל הכתובות
            success = self.queries.delete_all_addresses()
            
            if success:
                logger.info(f"נמחקו {count_before} כתובות")
                return {
                    'success': True,
                    'message': f'נמחקו {count_before} כתובות בהצלחה',
                    'deleted_count': count_before,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': 'לא ניתן למחוק כתובות',
                    'deleted_count': 0
                }
                
        except Exception as e:
            logger.error(f"שגיאה באיפוס נתונים: {e}")
            return {
                'success': False,
                'error': str(e),
                'deleted_count': 0
            }
    
    def reset_all_data(self) -> Dict:
        """איפוס כל הנתונים - מחיקה מלאה משתי הטבלאות"""
        try:
            from ..database.connection import get_database_client
            supabase = get_database_client()
            
            # קבל סטטיסטיקות לפני המחיקה
            stats_before = self.get_statistics()
            addresses_before = stats_before.get('data', {}).get('total_addresses', 0)
            
            # מחק מטבלת הכתובות הרגילות
            addresses_response = supabase.table('addresses').delete().neq('id', 0).execute()
            addresses_deleted = len(addresses_response.data) if addresses_response.data else 0
            
            # מחק מטבלת הכתובות החסרות
            missing_response = supabase.table('addresses_missing_coordinates').delete().neq('id', 0).execute()
            missing_deleted = len(missing_response.data) if missing_response.data else 0
            
            total_deleted = addresses_deleted + missing_deleted
            
            logger.info(f"אופסו כל הנתונים: {addresses_deleted} כתובות רגילות + {missing_deleted} כתובות חסרות = {total_deleted} סה\"כ")
            
            return {
                'success': True,
                'message': f'אופסו כל הנתונים בהצלחה: {total_deleted} כתובות (רגילות: {addresses_deleted}, חסרות: {missing_deleted})',
                'deleted_count': total_deleted,
                'addresses_deleted': addresses_deleted,
                'missing_deleted': missing_deleted,
                'timestamp': datetime.now().isoformat()
            }
                
        except Exception as e:
            logger.error(f"שגיאה באיפוס כל הנתונים: {e}")
            return {
                'success': False,
                'error': str(e),
                'deleted_count': 0
            }
    
    def backup_data(self) -> Dict:
        """יצירת גיבוי של הנתונים"""
        try:
            addresses = self.queries.get_all_addresses()
            
            backup_data = {
                'timestamp': datetime.now().isoformat(),
                'total_addresses': len(addresses),
                'addresses': addresses,
                'metadata': {
                    'database_type': 'supabase',
                    'backup_version': '1.0'
                }
            }
            
            return {
                'success': True,
                'backup_data': backup_data,
                'message': f'נוצר גיבוי של {len(addresses)} כתובות'
            }
            
        except Exception as e:
            logger.error(f"שגיאה ביצירת גיבוי: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def restore_data(self, backup_data: Dict) -> Dict:
        """שחזור נתונים מגיבוי"""
        try:
            addresses = backup_data.get('addresses', [])
            
            if not addresses:
                return {
                    'success': False,
                    'error': 'אין נתונים לשחזור'
                }
            
            # מחק נתונים קיימים
            self.queries.delete_all_addresses()
            
            # הוסף נתונים מהגיבוי
            restored_count = 0
            
            for addr in addresses:
                try:
                    success = self.queries.insert_address(addr)
                    if success:
                        restored_count += 1
                except Exception as e:
                    logger.error(f"שגיאה בשחזור כתובת: {e}")
                    continue
            
            return {
                'success': True,
                'message': f'שוחזרו {restored_count} כתובות מתוך {len(addresses)}',
                'restored_count': restored_count,
                'total_in_backup': len(addresses)
            }
            
        except Exception as e:
            logger.error(f"שגיאה בשחזור נתונים: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def validate_data_integrity(self) -> Dict:
        """בדיקת תקינות הנתונים"""
        try:
            addresses = self.queries.get_all_addresses()
            
            validation_results = {
                'success': True,
                'total_addresses': len(addresses),
                'issues': [],
                'warnings': [],
                'summary': {
                    'addresses_with_issues': 0,
                    'addresses_with_warnings': 0,
                    'healthy_addresses': 0
                }
            }
            
            for addr in addresses:
                issues = []
                warnings = []
                
                # בדיקות חובה
                if not addr.get('address') or not addr.get('address').strip():
                    issues.append('כתובת חסרה')
                
                if not addr.get('id'):
                    issues.append('מזהה חסר')
                
                # בדיקות אזהרה
                if not addr.get('city'):
                    warnings.append('עיר חסרה')
                
                if not addr.get('latitude') or not addr.get('longitude'):
                    warnings.append('קואורדינטות חסרות')
                
                if addr.get('latitude') and addr.get('longitude'):
                    # בדוק שהקואורדינטות בישראל
                    lat, lon = float(addr['latitude']), float(addr['longitude'])
                    if not (29.5 <= lat <= 33.5 and 34.0 <= lon <= 36.0):
                        warnings.append('קואורדינטות מחוץ לישראל')
                
                # עדכן סיכום
                if issues:
                    validation_results['issues'].append({
                        'address_id': addr.get('id'),
                        'address': addr.get('address'),
                        'issues': issues
                    })
                    validation_results['summary']['addresses_with_issues'] += 1
                
                if warnings:
                    validation_results['warnings'].append({
                        'address_id': addr.get('id'),
                        'address': addr.get('address'),
                        'warnings': warnings
                    })
                    validation_results['summary']['addresses_with_warnings'] += 1
                
                if not issues and not warnings:
                    validation_results['summary']['healthy_addresses'] += 1
            
            return validation_results
            
        except Exception as e:
            logger.error(f"שגיאה בבדיקת תקינות נתונים: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _initialize_basic_data(self):
        """אתחול נתונים בסיסיים"""
        try:
            # כתובות דוגמה לאתחול
            sample_addresses = [
                {
                    'address': 'כיכר צרפת, ירושלים',
                    'city': 'ירושלים',
                    'neighborhood': 'מרכז העיר',
                    'latitude': 31.7784,
                    'longitude': 35.2257,
                    'visited': False,
                    'source': 'system_init',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                },
                {
                    'address': 'תחנת אוטובוס מרכזית, ירושלים',
                    'city': 'ירושלים',
                    'neighborhood': 'מרכז העיר',
                    'latitude': 31.7875,
                    'longitude': 35.2016,
                    'visited': False,
                    'source': 'system_init',
                    'created_at': datetime.now(),
                    'updated_at': datetime.now()
                }
            ]
            
            for addr in sample_addresses:
                self.queries.insert_address(addr)
            
            logger.info("אותחלו נתונים בסיסיים")
            
        except Exception as e:
            logger.error(f"שגיאה באתחול נתונים בסיסיים: {e}")
