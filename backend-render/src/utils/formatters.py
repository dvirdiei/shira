# -*- coding: utf-8 -*-
"""
📋 Data Formatters - הנוסע המתמיד
פורמט נתונים לצורכים שונים
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class DataFormatter:
    """פורמט נתונים כלליים"""
    
    @staticmethod
    def format_address_for_display(address: Dict) -> Dict:
        """פורמט כתובת לתצוגה"""
        try:
            return {
                'id': address.get('id'),
                'address': address.get('address', ''),
                'city': address.get('city', 'ירושלים'),
                'neighborhood': address.get('neighborhood', 'לא ידוע'),
                'visited': address.get('visited', False),
                'has_coordinates': bool(address.get('latitude') and address.get('longitude')),
                'display_name': DataFormatter._create_display_name(address)
            }
            
        except Exception as e:
            logger.error(f"שגיאה בפורמט כתובת לתצוגה: {e}")
            return {}
    
    @staticmethod
    def format_address_for_map(address: Dict) -> Dict:
        """פורמט כתובת למפה"""
        try:
            latitude = address.get('latitude')
            longitude = address.get('longitude')
            
            if not latitude or not longitude:
                return None
            
            return {
                'id': address.get('id'),
                'address': address.get('address', ''),
                'city': address.get('city', 'ירושלים'),
                'neighborhood': address.get('neighborhood', 'לא ידוע'),
                'latitude': float(latitude),
                'longitude': float(longitude),
                'visited': address.get('visited', False),
                'marker_color': 'green' if address.get('visited') else 'red',
                'popup_text': DataFormatter._create_popup_text(address)
            }
            
        except Exception as e:
            logger.error(f"שגיאה בפורמט כתובת למפה: {e}")
            return None
    
    @staticmethod
    def format_address_for_export(address: Dict) -> Dict:
        """פורמט כתובת לייצוא"""
        try:
            return {
                'מזהה': address.get('id'),
                'כתובת': address.get('address', ''),
                'עיר': address.get('city', 'ירושלים'),
                'שכונה': address.get('neighborhood', 'לא ידוע'),
                'קו רוחב': address.get('latitude', ''),
                'קו אורך': address.get('longitude', ''),
                'בוקר': 'כן' if address.get('visited') else 'לא',
                'מקור': address.get('source', ''),
                'נוצר': DataFormatter._format_datetime(address.get('created_at')),
                'עודכן': DataFormatter._format_datetime(address.get('updated_at'))
            }
            
        except Exception as e:
            logger.error(f"שגיאה בפורמט כתובת לייצוא: {e}")
            return {}
    
    @staticmethod
    def format_statistics_for_display(stats: Dict) -> Dict:
        """פורמט סטטיסטיקות לתצוגה"""
        try:
            data = stats.get('data', {})
            
            return {
                'סה"כ כתובות': data.get('total_addresses', 0),
                'כתובות שבוקרו': data.get('visited_addresses', 0),
                'כתובות שלא בוקרו': data.get('unvisited_addresses', 0),
                'עם קואורדינטות': data.get('geocoded_addresses', 0),
                'בלי קואורדינטות': data.get('missing_coordinates', 0),
                'אחוז ביקורים': f"{data.get('percentages', {}).get('visited', 0)}%",
                'אחוז גיאוקודינג': f"{data.get('percentages', {}).get('geocoded', 0)}%",
                'עריםים': data.get('cities', {}),
                'שכונות': data.get('neighborhoods', {}),
                'מקורות': data.get('sources', {}),
                'זמן עדכון': DataFormatter._format_datetime(stats.get('timestamp'))
            }
            
        except Exception as e:
            logger.error(f"שגיאה בפורמט סטטיסטיקות: {e}")
            return {}
    
    @staticmethod
    def format_coordinates(latitude: Optional[float], longitude: Optional[float]) -> str:
        """פורמט קואורדינטות לתצוגה"""
        try:
            if latitude is None or longitude is None:
                return 'לא זמין'
            
            return f"{latitude:.6f}, {longitude:.6f}"
            
        except Exception as e:
            logger.error(f"שגיאה בפורמט קואורדינטות: {e}")
            return 'שגיאה'
    
    @staticmethod
    def format_address_list_for_frontend(addresses: List[Dict]) -> List[Dict]:
        """פורמט רשימת כתובות לפרונטאנד"""
        try:
            formatted_addresses = []
            
            for address in addresses:
                formatted = DataFormatter.format_address_for_display(address)
                if formatted:
                    formatted_addresses.append(formatted)
            
            return formatted_addresses
            
        except Exception as e:
            logger.error(f"שגיאה בפורמט רשימת כתובות: {e}")
            return []
    
    @staticmethod
    def format_geocoding_results(results: Dict) -> Dict:
        """פורמט תוצאות גיאוקודינג"""
        try:
            return {
                'הצלחה': results.get('success', False),
                'סה"כ כתובות': results.get('total', 0),
                'נוספו בהצלחה': len(results.get('added', [])),
                'נכשלו': len(results.get('failed', [])),
                'עם קואורדינטות': results.get('summary', {}).get('geocoded', 0),
                'בלי קואורדינטות': results.get('summary', {}).get('not_geocoded', 0),
                'כתובות שנוספו': [
                    {
                        'כתובת': addr.get('address'),
                        'קואורדינטות': addr.get('geocoded', False)
                    }
                    for addr in results.get('added', [])
                ],
                'כתובות שנכשלו': [
                    {
                        'כתובת': addr.get('address'),
                        'שגיאה': addr.get('error')
                    }
                    for addr in results.get('failed', [])
                ]
            }
            
        except Exception as e:
            logger.error(f"שגיאה בפורמט תוצאות גיאוקודינג: {e}")
            return {}
    
    @staticmethod
    def _create_display_name(address: Dict) -> str:
        """יצור שם תצוגה לכתובת"""
        try:
            parts = []
            
            if address.get('address'):
                parts.append(address['address'])
            
            if address.get('neighborhood') and address.get('neighborhood') != 'לא ידוע':
                parts.append(address['neighborhood'])
            
            if address.get('city') and address.get('city') != 'ירושלים':
                parts.append(address['city'])
            
            return ', '.join(parts)
            
        except Exception as e:
            logger.error(f"שגיאה ביצירת שם תצוגה: {e}")
            return address.get('address', '')
    
    @staticmethod
    def _create_popup_text(address: Dict) -> str:
        """יצור טקסט לפופאפ במפה"""
        try:
            parts = []
            
            if address.get('address'):
                parts.append(f"🏠 {address['address']}")
            
            if address.get('neighborhood') and address.get('neighborhood') != 'לא ידוע':
                parts.append(f"🏘️ {address['neighborhood']}")
            
            if address.get('city'):
                parts.append(f"🏙️ {address['city']}")
            
            if address.get('visited'):
                parts.append("✅ בוקר")
            else:
                parts.append("⏳ לא בוקר")
            
            return '\n'.join(parts)
            
        except Exception as e:
            logger.error(f"שגיאה ביצירת טקסט פופאפ: {e}")
            return address.get('address', '')
    
    @staticmethod
    def _format_datetime(dt: Any) -> str:
        """פורמט תאריך ושעה"""
        try:
            if dt is None:
                return 'לא זמין'
            
            if isinstance(dt, str):
                # נסה לפרס מחרוזת ISO
                dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
            
            if isinstance(dt, datetime):
                return dt.strftime('%d/%m/%Y %H:%M')
            
            return str(dt)
            
        except Exception as e:
            logger.error(f"שגיאה בפורמט תאריך: {e}")
            return 'שגיאה'
