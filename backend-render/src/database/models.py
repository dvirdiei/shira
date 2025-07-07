# -*- coding: utf-8 -*-
"""
Database Models
מודלים של הטבלאות בבסיס הנתונים
"""

from typing import Dict, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict

@dataclass
class Address:
    """מודל כתובת"""
    address: str
    city: str = 'ירושלים'
    neighborhood: str = 'לא ידוע'
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    visited: bool = False
    source: str = 'manual'
    source_file: Optional[str] = None
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        """המרה למילון"""
        data = asdict(self)
        # המרת datetime לstring אם צריך
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.updated_at:
            data['updated_at'] = self.updated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Address':
        """יצירה ממילון"""
        # נקה שדות None או ריקים
        clean_data = {k: v for k, v in data.items() if v is not None}
        return cls(**clean_data)
    
    def has_coordinates(self) -> bool:
        """בדיקה אם יש קואורדינטות"""
        return self.latitude is not None and self.longitude is not None
    
    def is_valid(self) -> bool:
        """בדיקת תקינות"""
        return bool(self.address and self.address.strip())

class AddressValidator:
    """מחלקה לאימות כתובות"""
    
    @staticmethod
    def validate_address_text(address: str) -> bool:
        """אימות טקסט כתובת"""
        if not address or not isinstance(address, str):
            return False
        return len(address.strip()) >= 3
    
    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> bool:
        """אימות קואורדינטות"""
        if lat is None or lon is None:
            return False
        # בדיקה שהקואורדינטות באזור ישראל
        return 29.0 <= lat <= 33.5 and 34.0 <= lon <= 36.0
    
    @staticmethod
    def validate_source(source: str) -> bool:
        """אימות מקור הכתובת"""
        valid_sources = ['manual', 'file_upload', 'geocoded', 'demo', 'manual_corrected']
        return source in valid_sources

class AddressFormatter:
    """מחלקה לעיצוב כתובות"""
    
    @staticmethod
    def format_for_frontend(address: Address) -> Dict:
        """עיצוב לFrontend"""
        return {
            'address': address.address,
            'city': address.city,
            'neighborhood': address.neighborhood,
            'lat': address.latitude,
            'lon': address.longitude,
            'visited': address.visited,
            'source': address.source,
            'id': address.id,
            'created_at': address.created_at.isoformat() if address.created_at else None
        }
    
    @staticmethod
    def format_for_map(addresses: List[Address]) -> List[Dict]:
        """עיצוב לתצוגה במפה"""
        return [
            AddressFormatter.format_for_frontend(addr) 
            for addr in addresses 
            if addr.has_coordinates()
        ]
    
    @staticmethod
    def format_address_detailed(address: Dict) -> Dict:
        """פורמט כתובת מפורט למפה ותצוגה מלאה"""
        try:
            return {
                'id': address.get('id'),
                'address': address.get('address', ''),
                'city': address.get('city', 'ירושלים'),
                'neighborhood': address.get('neighborhood', 'לא ידוע'),
                'latitude': address.get('latitude'),
                'longitude': address.get('longitude'),
                'visited': address.get('visited', False),
                'source': address.get('source', 'manual'),
                'source_file': address.get('source_file'),
                'created_at': address.get('created_at'),
                'updated_at': address.get('updated_at'),
                'has_coordinates': bool(address.get('latitude') and address.get('longitude')),
                'display_name': AddressFormatter._create_display_name(address),
                'coordinates_text': AddressFormatter._format_coordinates(
                    address.get('latitude'), 
                    address.get('longitude')
                ),
                'status_text': 'בוקר' if address.get('visited') else 'לא בוקר',
                'marker_color': 'green' if address.get('visited') else 'red'
            }
            
        except Exception as e:
            logger.error(f"שגיאה בפורמט כתובת מפורט: {e}")
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
    def _format_coordinates(latitude: Optional[float], longitude: Optional[float]) -> str:
        """פורמט קואורדינטות לתצוגה"""
        try:
            if latitude is None or longitude is None:
                return 'לא זמין'
            
            return f"{latitude:.6f}, {longitude:.6f}"
            
        except Exception as e:
            logger.error(f"שגיאה בפורמט קואורדינטות: {e}")
            return 'שגיאה'
