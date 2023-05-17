from pyGarminAPI.garmin_api import generate_signature, get_daily_summary_health
from datetime import datetime, timedelta

# Generate the signature
signatures = generate_signature()
signature = signatures['signature'][0]

# Fetch daily summary health data for a specific date range
start_date = datetime(2023, 4, 15)
end_date = start_date + timedelta(days=5)
current_date = start_date

while current_date <= end_date:
    # Generate strings for the current date and the next day
    start_date_str = current_date.strftime('%Y-%m-%d %H:%M:%S')
    end_day_str = (current_date + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    
    # Retrieve daily summary health data for the current date range
    daily_summary = get_daily_summary_health(signature, start_date_str, end_day_str)
    
    # Print the results
    print(f"Date Range: {start_date_str} - {end_day_str}")
    print(daily_summary)
    
    # Increment the current date by one day
    current_date += timedelta(days=1)