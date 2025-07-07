# -*- coding: utf-8 -*-
"""
⏱️ Rate Limiter - הנוסע המתמיד
הגבלת קצב בקשות למניעת חריגה מגבולות API
"""

import time
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RateLimiter:
    """מגביל קצב בקשות"""
    
    def __init__(self, max_requests: int = 10, time_window: int = 60):
        """
        אתחול מגביל הקצב
        
        Args:
            max_requests: מספר מקסימלי של בקשות
            time_window: חלון זמן בשניות
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
        self.last_cleanup = time.time()
    
    def can_make_request(self) -> bool:
        """בדוק אם ניתן לבצע בקשה"""
        try:
            current_time = time.time()
            
            # נקה בקשות ישנות כל דקה
            if current_time - self.last_cleanup > 60:
                self._cleanup_old_requests()
                self.last_cleanup = current_time
            
            # הסר בקשות מחוץ לחלון הזמן
            cutoff_time = current_time - self.time_window
            self.requests = [req_time for req_time in self.requests if req_time > cutoff_time]
            
            # בדוק אם יש מקום לבקשה נוספת
            if len(self.requests) < self.max_requests:
                self.requests.append(current_time)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"שגיאה בבדיקת מגביל קצב: {e}")
            return True  # במקרה של שגיאה, אפשר את הבקשה
    
    def get_wait_time(self) -> float:
        """קבל זמן המתנה עד הבקשה הבאה"""
        try:
            if not self.requests:
                return 0.0
            
            current_time = time.time()
            oldest_request = min(self.requests)
            wait_time = self.time_window - (current_time - oldest_request)
            
            return max(0.0, wait_time)
            
        except Exception as e:
            logger.error(f"שגיאה בחישוב זמן המתנה: {e}")
            return 0.0
    
    def get_status(self) -> Dict:
        """קבל מצב מגביל הקצב"""
        try:
            current_time = time.time()
            
            # הסר בקשות ישנות
            cutoff_time = current_time - self.time_window
            active_requests = [req_time for req_time in self.requests if req_time > cutoff_time]
            
            return {
                'max_requests': self.max_requests,
                'time_window': self.time_window,
                'active_requests': len(active_requests),
                'remaining_requests': self.max_requests - len(active_requests),
                'wait_time': self.get_wait_time(),
                'can_make_request': len(active_requests) < self.max_requests
            }
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת מצב מגביל קצב: {e}")
            return {}
    
    def reset(self):
        """איפוס מגביל הקצב"""
        try:
            self.requests = []
            self.last_cleanup = time.time()
            logger.info("מגביל הקצב אופס")
            
        except Exception as e:
            logger.error(f"שגיאה באיפוס מגביל קצב: {e}")
    
    def _cleanup_old_requests(self):
        """נקה בקשות ישנות"""
        try:
            current_time = time.time()
            cutoff_time = current_time - self.time_window
            
            old_count = len(self.requests)
            self.requests = [req_time for req_time in self.requests if req_time > cutoff_time]
            new_count = len(self.requests)
            
            if old_count > new_count:
                logger.debug(f"נוקו {old_count - new_count} בקשות ישנות")
                
        except Exception as e:
            logger.error(f"שגיאה בניקוי בקשות ישנות: {e}")


class APIRateLimiter:
    """מגביל קצב מתקדם לבקשות API"""
    
    def __init__(self):
        """אתחול מגביל API"""
        self.limiters = {
            'geocoding': RateLimiter(max_requests=10, time_window=60),  # 10 בקשות לדקה
            'database': RateLimiter(max_requests=100, time_window=60),  # 100 בקשות לדקה
            'general': RateLimiter(max_requests=50, time_window=60)     # 50 בקשות לדקה
        }
    
    def can_make_request(self, api_type: str = 'general') -> bool:
        """בדוק אם ניתן לבצע בקשה מסוג מסוים"""
        try:
            limiter = self.limiters.get(api_type)
            if not limiter:
                # אם אין מגביל ספציפי, השתמש בכללי
                limiter = self.limiters['general']
            
            return limiter.can_make_request()
            
        except Exception as e:
            logger.error(f"שגיאה בבדיקת מגביל API: {e}")
            return True
    
    def get_wait_time(self, api_type: str = 'general') -> float:
        """קבל זמן המתנה לסוג API"""
        try:
            limiter = self.limiters.get(api_type)
            if not limiter:
                limiter = self.limiters['general']
            
            return limiter.get_wait_time()
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת זמן המתנה API: {e}")
            return 0.0
    
    def get_all_status(self) -> Dict:
        """קבל מצב כל מגבילי הקצב"""
        try:
            status = {}
            
            for api_type, limiter in self.limiters.items():
                status[api_type] = limiter.get_status()
            
            return status
            
        except Exception as e:
            logger.error(f"שגיאה בקבלת מצב כל המגבילים: {e}")
            return {}
    
    def reset_all(self):
        """איפוס כל מגבילי הקצב"""
        try:
            for limiter in self.limiters.values():
                limiter.reset()
            
            logger.info("כל מגבילי הקצב אופסו")
            
        except Exception as e:
            logger.error(f"שגיאה באיפוס כל המגבילים: {e}")


# אובייקט גלובלי למגביל קצב
rate_limiter = APIRateLimiter()
