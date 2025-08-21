from datetime import datetime, timezone, timedelta
from sqlalchemy import and_, func
from typing import Dict, Tuple

from app.models import StoreStatus, BusinessHours, StoreTimezone
from app.database import SessionLocal


class UptimeCalculator:
    def __init__(self):
        # create db session
        self.session = SessionLocal()
        # cache timezone and business hours for stores so we don’t hit DB again and again
        self._timezone_cache = {}
        self._business_hours_cache = {}
    
    def __del__(self):
        # close db session when object is deleted
        if hasattr(self, 'session'):
            self.session.close()
    
    def get_current_timestamp(self) -> datetime:
        """
        Get the latest timestamp from StoreStatus table.
        We use this as the "current time" for calculations.
        """
        if not hasattr(self, '_current_timestamp'):
            self._current_timestamp = self.session.query(func.max(StoreStatus.timestamp_utc)).scalar()
        return self._current_timestamp or datetime.now(timezone.utc)
    
    def get_store_timezone(self, store_id: str) -> str:
        """
        Get timezone for a given store.
        If not found in DB, default to America/Chicago.
        """
        if store_id not in self._timezone_cache:
            timezone_record = self.session.query(StoreTimezone).filter(
                StoreTimezone.store_id == store_id
            ).first()
            self._timezone_cache[store_id] = timezone_record.timezone_str if timezone_record else "America/Chicago"
        
        return self._timezone_cache[store_id]
    
    def get_business_hours(self, store_id: str) -> Dict[int, Tuple[datetime.time, datetime.time]]:
        """
        Get business hours for a given store.
        If missing, assume store is open 24x7.
        """
        if store_id not in self._business_hours_cache:
            hours_records = self.session.query(BusinessHours).filter(
                BusinessHours.store_id == store_id
            ).all()
            
            if not hours_records:
                # store is open 24 hours for all 7 days
                from datetime import time
                self._business_hours_cache[store_id] = {i: (time(0, 0), time(23, 59, 59)) for i in range(7)}
            else:
                business_hours = {}
                for record in hours_records:
                    business_hours[record.day_of_week] = (
                        record.start_time_local, 
                        record.end_time_local
                    )
                self._business_hours_cache[store_id] = business_hours
        
        return self._business_hours_cache[store_id]
    
    def calculate_uptime_downtime_simple(self, store_id: str, hours_back: int) -> Dict[str, float]:
        """
        Calculate uptime/downtime for the past N hours.
        Simplified version: just count active vs inactive status records.
        """
        current_time = self.get_current_timestamp()
        start_time = current_time - timedelta(hours=hours_back)
        
        # fetch status data for this store within the time range
        status_records = self.session.query(StoreStatus).filter(
            and_(
                StoreStatus.store_id == store_id,
                StoreStatus.timestamp_utc >= start_time,
                StoreStatus.timestamp_utc <= current_time
            )
        ).order_by(StoreStatus.timestamp_utc).all()
        
        if not status_records:
            # if no records found, assume full downtime
            if hours_back == 1:
                return {'uptime': 0.0, 'downtime': 60.0}  # in minutes
            else:
                return {'uptime': 0.0, 'downtime': float(hours_back)}  # in hours
        
        # count how many records are active
        active_count = len([r for r in status_records if r.status == 'active'])
        total_count = len(status_records)
        
        if total_count == 0:
            uptime_ratio = 0
        else:
            uptime_ratio = active_count / total_count
        
        if hours_back == 1:
            # convert ratio into minutes
            uptime_minutes = uptime_ratio * 60
            downtime_minutes = (1 - uptime_ratio) * 60
            return {'uptime': round(uptime_minutes, 1), 'downtime': round(downtime_minutes, 1)}
        else:
            # convert ratio into hours
            uptime_hours = uptime_ratio * hours_back
            downtime_hours = (1 - uptime_ratio) * hours_back
            return {'uptime': round(uptime_hours, 2), 'downtime': round(downtime_hours, 2)}
    
    def generate_report_for_store(self, store_id: str) -> Dict:
        """
        Generate full uptime/downtime report for a store.
        Calculates last hour, last day, and last week stats.
        """
        try:
            last_hour = self.calculate_uptime_downtime_simple(store_id, 1)
            last_day = self.calculate_uptime_downtime_simple(store_id, 24)
            last_week = self.calculate_uptime_downtime_simple(store_id, 24 * 7)
            
            return {
                'store_id': store_id,
                'uptime_last_hour(in minutes)': last_hour['uptime'],
                'uptime_last_day(in hours)': last_day['uptime'],
                'uptime_last_week(in hours)': last_week['uptime'],
                'downtime_last_hour(in minutes)': last_hour['downtime'],
                'downtime_last_day(in hours)': last_day['downtime'],
                'downtime_last_week(in hours)': last_week['downtime']
            }
        except Exception as e:
            # if something fails, return zeroes so report can still be generated
            print(f"Error generating report for store {store_id}: {e}")
            return {
                'store_id': store_id,
                'uptime_last_hour(in minutes)': 0.0,
                'uptime_last_day(in hours)': 0.0,
                'uptime_last_week(in hours)': 0.0,
                'downtime_last_hour(in minutes)': 0.0,
                'downtime_last_day(in hours)': 0.0,
                'downtime_last_week(in hours)': 0.0
            }




