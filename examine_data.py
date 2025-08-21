import pandas as pd
from datetime import datetime

print("📂 Loading CSV files...")

# Load all CSVs into pandas dataframes
store_status = pd.read_csv('data/store_status.csv')
business_hours = pd.read_csv('data/menu_hours.csv')  
store_timezone = pd.read_csv('data/timezones.csv')   

# ------------------------------
# 1. STORE STATUS DATA
# ------------------------------
print("\n=== STORE STATUS DATA ===")
print(f"Shape (rows, columns): {store_status.shape}")
print("First 5 rows:")
print(store_status.head())

# check date range of status logs
print(f"Date range: {store_status['timestamp_utc'].min()} to {store_status['timestamp_utc'].max()}")
# unique stores present
print(f"Unique stores: {store_status['store_id'].nunique()}")
# how many active vs inactive
print("Status distribution:")
print(store_status['status'].value_counts())
print()

# ------------------------------
# 2. BUSINESS HOURS DATA
# ------------------------------
print("=== BUSINESS HOURS DATA ===")
print(f"Shape (rows, columns): {business_hours.shape}")
print("First 5 rows:")
print(business_hours.head())
print(f"Unique stores: {business_hours['store_id'].nunique()}")

# pick a random sample store and print its business hours
sample_store = business_hours['store_id'].iloc[0]
print("Sample business hours for one store:")
print(business_hours[business_hours['store_id'] == sample_store])
print()

# ------------------------------
# 3. STORE TIMEZONE DATA
# ------------------------------
print("=== TIMEZONE DATA ===")
print(f"Shape (rows, columns): {store_timezone.shape}")
print("First 5 rows:")
print(store_timezone.head())
print(f"Unique stores: {store_timezone['store_id'].nunique()}")
print("Timezone distribution:")
print(store_timezone['timezone_str'].value_counts())
print()

# ------------------------------
# 4. OVERLAP ANALYSIS
# ------------------------------
print("=== DATA OVERLAP ANALYSIS ===")

# get all store_ids in each dataset
status_stores = set(store_status['store_id'].unique())
hours_stores = set(business_hours['store_id'].unique())
timezone_stores = set(store_timezone['store_id'].unique())

print(f"Stores in status data: {len(status_stores)}")
print(f"Stores in business hours: {len(hours_stores)}")
print(f"Stores in timezone data: {len(timezone_stores)}")

# find stores which exist in all 3 datasets
common_all = status_stores & hours_stores & timezone_stores
print(f"Stores present in ALL three datasets: {len(common_all)}")

# print one example store if overlap exists
if len(common_all) > 0:
    print(f"✅ Sample store present in all datasets: {list(common_all)[0]}")
else:
    print("⚠️ WARNING: No stores present in all three datasets!")


