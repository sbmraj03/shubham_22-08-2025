import pandas as pd
from datetime import datetime, timezone
import os
import math
from sqlalchemy.orm import sessionmaker

from app.database import engine
from app.uptime_calculator import UptimeCalculator


def generate_report():
    """
    Function to generate uptime and downtime report for stores.

    Steps followed:
    1. Get store ids from database.
    2. For each store, calculate uptime and downtime using UptimeCalculator.
    3. Store the result in a dataframe.
    4. Save the result as CSV in reports folder.
    """
    print("🔄 Starting report generation...")
    start_time = datetime.now() # store start time

    # create reports folder if not present
    os.makedirs("reports", exist_ok=True)

    # create a db session
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # get distinct store ids from status, business_hours and timezone tables
        stores_query = session.execute("""
            SELECT DISTINCT ss.store_id 
            FROM store_status ss
            JOIN business_hours bh ON ss.store_id = bh.store_id
            JOIN store_timezone st ON ss.store_id = st.store_id
            ORDER BY ss.store_id
        """).fetchall()

        # extract only the ids
        store_ids = [row[0] for row in stores_query]
        print(f"📋 Found {len(store_ids)} stores to process")

        # create calculator object
        calculator = UptimeCalculator()
        report_data = []

        batch_size = 50
        num_batch = math.ceil(len(store_ids) / batch_size)

        # loop through the stores in batches of 50
        for i in range(0, len(store_ids), batch_size):
            batch = store_ids[i:i + batch_size]
            print(f"🔄 Processing Batch {i // batch_size + 1}: {num_batch}")

            # calculate report for each store in this batch
            for store_id in batch:
                store_report = calculator.generate_report_for_store(store_id)
                report_data.append(store_report)

            print(f"✅ Processed {min(i + batch_size, len(store_ids))}/{len(store_ids)} stores")


        # convert list of reports to dataframe
        df = pd.DataFrame(report_data)

        # add timestamp in filename so that each report is unique
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"reports/store_report_{timestamp}.csv"

        # save dataframe to csv
        df.to_csv(filename, index=False)

        # print some summary to check if results look okay
        print(f"\nSummary:")
        print(f"Total stores: {len(df)}")
        print(f"Avg uptime (last hour): {df['uptime_last_hour(in minutes)'].mean():.1f} min")
        print(f"Avg uptime (last day): {df['uptime_last_day(in hours)'].mean():.1f} hrs")
        print(f"Avg uptime (last week): {df['uptime_last_week(in hours)'].mean():.1f} hrs")
        print(f"Stores with 0 uptime last hour: {len(df[df['uptime_last_hour(in minutes)'] == 0])}")
        print(f"Report saved -> {filename}")

        end_time = datetime.now() # store end time
        
        print("\n====================================================\n")
        print(f"\n📊 Report generated in {(end_time - start_time)} sec")
        print("\n=====================================================\n")
        
        return filename

    except Exception as e:
        # print error if something fails
        print(f"❌ Error generating report: {e}")
        raise

    finally:
        # close db session
        session.close()


if __name__ == "__main__":
    generate_report()











