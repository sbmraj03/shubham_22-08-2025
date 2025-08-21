import pandas as pd
from datetime import datetime, timezone
from sqlalchemy.orm import sessionmaker
from sqlalchemy import insert   
from app.database import engine, create_tables
from app.models import StoreStatus, BusinessHours, StoreTimezone
import pytz


def parse_timestamp(timestamp_str):
    """Parse timestamp string to datetime object with proper timezone"""
    # Some rows have " UTC" suffix, remove it if present
    timestamp_str = timestamp_str.replace(' UTC', '')
    # Convert string into datetime object
    dt = datetime.fromisoformat(timestamp_str)
    # If datetime has no timezone info, make it UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def parse_time(time_str):
    """Parse time string (HH:MM:SS) to Python time object"""
    return datetime.strptime(time_str, '%H:%M:%S').time()


def load_store_status():
    """Load store status data from CSV and insert into DB"""
    print("Loading store status data...")
    
    # Using chunks because file is large -> prevents memory issues
    chunk_size = 20000
    total_rows = 0
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Read CSV in chunks
        for chunk_df in pd.read_csv('data/store_status.csv', chunksize=chunk_size):
            records = []
            
            # Prepare records for bulk insert
            for _, row in chunk_df.iterrows():
                records.append({
                    "store_id": row['store_id'],
                    "status": row['status'],
                    "timestamp_utc": parse_timestamp(row['timestamp_utc'])
                })
            
            # Bulk insert into DB (faster than one-by-one)
            session.execute(insert(StoreStatus), records)
            session.commit()
            
            total_rows += len(records)
            print(f"Loaded {total_rows} store status records...")
            
    except Exception as e:
        print(f"Error loading store status: {e}")
        session.rollback()
    finally:
        session.close()
    
    print(f"✅ Store status loading complete! Total: {total_rows} records")


def load_business_hours():
    """Load business hours data from CSV and insert into DB"""
    print("Loading business hours data...")
    
    df = pd.read_csv('data/menu_hours.csv')
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        records = []
        # Convert each row into BusinessHours object
        for _, row in df.iterrows():
            record = BusinessHours(
                store_id=row['store_id'],
                day_of_week=row['dayOfWeek'],
                start_time_local=parse_time(row['start_time_local']),
                end_time_local=parse_time(row['end_time_local'])
            )
            records.append(record)
        
        # Save all objects in bulk
        session.bulk_save_objects(records)
        session.commit()
        print(f"✅ Business hours loading complete! Total: {len(records)} records")
        
    except Exception as e:
        print(f"Error loading business hours: {e}")
        session.rollback()
    finally:
        session.close()


def load_store_timezones():
    """Load store timezone data from CSV and insert into DB"""
    print("Loading store timezone data...")
    
    df = pd.read_csv('data/timezones.csv')
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        records = []
        # Convert each row into StoreTimezone object
        for _, row in df.iterrows():
            record = StoreTimezone(
                store_id=row['store_id'],
                timezone_str=row['timezone_str']
            )
            records.append(record)
        
        # Save all objects in bulk
        session.bulk_save_objects(records)
        session.commit()
        print(f"✅ Store timezones loading complete! Total: {len(records)} records")
        
    except Exception as e:
        print(f"Error loading store timezones: {e}")
        session.rollback()
    finally:
        session.close()


def verify_data_loaded():
    """Check if data was inserted correctly"""
    print("\n=== VERIFYING DATA LOADED ===")
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Count records from all 3 tables
        status_count = session.query(StoreStatus).count()
        hours_count = session.query(BusinessHours).count()
        timezone_count = session.query(StoreTimezone).count()
        
        print(f"Store Status records: {status_count:,}")
        print(f"Business Hours records: {hours_count:,}")
        print(f"Store Timezone records: {timezone_count:,}")
        
        # Print first record from each table for checking
        print("\nSample Store Status record:")
        sample_status = session.query(StoreStatus).first()
        if sample_status:
            print(f"  Store ID: {sample_status.store_id}")
            print(f"  Status: {sample_status.status}")
            print(f"  Timestamp: {sample_status.timestamp_utc}")
        
        print("\nSample Business Hours record:")
        sample_hours = session.query(BusinessHours).first()
        if sample_hours:
            print(f"  Store ID: {sample_hours.store_id}")
            print(f"  Day: {sample_hours.day_of_week} (0=Monday)")
            print(f"  Hours: {sample_hours.start_time_local} - {sample_hours.end_time_local}")
            
    finally:
        session.close()


if __name__ == "__main__":
    # Create tables before inserting data
    print("Creating database tables...")
    create_tables()
    
    print("Starting data loading process...")
    load_store_timezones()    # Load smallest file first
    load_business_hours()     # Load business hours second
    load_store_status()       # Load large status file last
    
    # Verify record counts
    verify_data_loaded()
    print("\n🎉 All data loading complete!")
