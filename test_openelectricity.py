import os
import sys
from datetime import datetime, timedelta
import pandas as pd
from openelectricity import OEClient
from openelectricity.types import MarketMetric

# Try to load env variables from .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Retrieve API key
api_key = os.getenv("OPENELECTRICITY_API_KEY")

if not api_key or api_key == "YOUR_API_KEY_HERE":
    print("=" * 60)
    print("ERROR: Please set your OPENELECTRICITY_API_KEY in the .env file.")
    print("You can generate a free API key at: https://platform.openelectricity.org.au")
    print("=" * 60)
    sys.exit(1)

print("Initializing Open Electricity client...")
try:
    with OEClient(api_key=api_key) as client:
        # Fetch the last 2 days of data
        date_start = datetime.utcnow() - timedelta(days=2)
        print(f"Fetching market data (network: NEM, metrics: PRICE & DEMAND, start: {date_start.strftime('%Y-%m-%d')})...")
        
        # Get market data for National Electricity Market
        response = client.get_market(
            network_code="NEM",
            metrics=[MarketMetric.PRICE, MarketMetric.DEMAND],
            interval="1h",
            date_start=date_start,
            primary_grouping="network_region"
        )
        
        print("Parsing market response data manually...")
        records = []
        for series in response.data:
            metric_name = series.metric
            for result in series.results:
                region_id = result.name.split('_')[-1]
                for dp in result.data:
                    dt, val = dp.root
                    records.append({
                        'interval': dt,
                        'region_id': region_id,
                        'metric': metric_name,
                        'value': val
                    })
        
        df_all = pd.DataFrame(records)
        print(f"Constructed flat DataFrame. Total raw records: {len(df_all)}")
        
        # Pivot to make metrics (price, demand) separate columns
        print("Pivoting DataFrame to separate price and demand metrics...")
        df_pivoted = df_all.pivot(index=['interval', 'region_id'], columns='metric', values='value').reset_index()
        
        # Filter for Victoria (VIC1)
        print("Filtering data for region: VIC1...")
        df_vic = df_pivoted[df_pivoted['region_id'] == "VIC1"]
        
        output_file = "vic_electricity_data.csv"
        df_vic.to_csv(output_file, index=False)
        print(f"SUCCESS: Saved Victoria data to '{output_file}' ({len(df_vic)} rows).")
        
except Exception as e:
    print(f"\nAn error occurred during API execution: {e}")
    print("Please double check your API key and network connection.")
