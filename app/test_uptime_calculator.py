from app.uptime_calculator import UptimeCalculator
from app.database import SessionLocal

def test_uptime_calculator():
    """
    Simple test script for UptimeCalculator.
    This script checks:
    1. If we can fetch a valid store ID with complete data.
    2. If timezone and business hours are loading properly.
    3. If uptime report is being generated without errors.
    """
    print("🧪 Testing Uptime Calculator...")
    
    # create object of calculator
    calculator = UptimeCalculator()
    
    # get current timestamp from dataset
    current_time = calculator.get_current_timestamp()
    print(f"Using current time from data: {current_time}")
        
    session = SessionLocal()
    
    # find a sample store that has entries in all 3 tables
    sample_store = session.execute("""
        SELECT ss.store_id 
        FROM store_status ss
        JOIN business_hours bh ON ss.store_id = bh.store_id
        JOIN store_timezone st ON ss.store_id = st.store_id
        LIMIT 1
    """).fetchone()
    
    if sample_store:
        store_id = sample_store[0]
        print(f"\n✅ Found store to test: {store_id}")
        
        # test timezone fetch
        timezone_str = calculator.get_store_timezone(store_id)
        print(f"Store timezone: {timezone_str}")
        
        # test business hours fetch
        business_hours = calculator.get_business_hours(store_id)
        print(f"Business hours: {business_hours}")
        
        # test uptime calculation
        print("\n=== UPTIME CALCULATIONS ===")
        report = calculator.generate_report_for_store(store_id)
        
        # print all keys and values from report
        for key, value in report.items():
            print(f"{key}: {value}")
            
    else:
        print("❌ No store found with complete data!")
    
    session.close()

if __name__ == "__main__":
    # run the test
    test_uptime_calculator()
