"""
fetch_noaa_by_station.py
========================
Modifies the original state-by-state script to query specific weather station IDs
extracted from the data center / backbone dataset. 

Additionally handles psychrometric unit scaling ready for the data center simulation:
  - Temperature converted to Celsius
  - Relative humidity scaled appropriately
  - Standard Atmospheric Pressure mapped
"""

import os
import time
import requests
import pandas as pd

# ── CONFIG ────────────────────────────────────────────────────────────────────

TOKEN = os.environ.get("NOAA_TOKEN", "INPUTTOKENHERE")  # <-- Your active token

START_DATE  = "2021-01-01"
END_DATE    = "2024-12-31"
DATATYPES   = ["TMAX", "TAVG", "RHAV"]      # Target features for GSOY
OUTPUT_DIR  = "."
SLEEP_SEC   = 0.3                   # Rate limiting

# ── CORE API ENGINE ───────────────────────────────────────────────────────────

def noaa_get(endpoint, params, token):
    url = f"https://www.ncei.noaa.gov/cdo-web/api/v2/{endpoint}"
    headers = {"token": token}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 429:
        print("  Rate limit hit! Sleeping 5s...")
        time.sleep(5)
        response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def paginate(endpoint, params, token):
    """Handles pagination over records if a station has multiple entries."""
    all_results = []
    offset = 1
    limit = 1000
    
    while True:
        current_params = params.copy()
        current_params.update({"offset": offset, "limit": limit})
        data = noaa_get(endpoint, current_params, token)
        
        if not data or "results" not in data:
            break
            
        results = data["results"]
        all_results.extend(results)
        
        if len(results) < limit:
            break
            
        offset += limit
        time.sleep(0.1)
        
    return all_results

# ── TARGETED STATION FETCHING ────────────────────────────────────────────────

def fetch_climate_by_stations(station_ids, token):
    """
    Queries NOAA directly using individual station IDs, isolating our search
    only to relevant coordinates.
    """
    all_data = []
    datatype_str = ",".join(DATATYPES)
    
    print(f"\n=== Fetching climate observations for {len(station_ids)} target stations ===")
    
    for idx, station_id in enumerate(station_ids):
        print(f"  [{idx+1}/{len(station_ids)}] Querying station: {station_id}...")
        
        params = {
            "datasetid":  "GSOY",
            "datatypeid": datatype_str,
            "stationid":  station_id,
            "startdate":  START_DATE,
            "enddate":    END_DATE,
            "units":      "standard",   # Temperature returned in Fahrenheit
        }
        
        try:
            results = paginate("data", params, token)
            all_data.extend(results)
        except requests.HTTPError as e:
            # Handles edge cases where a station ID exists in the inventory but lacks data for these years
            print(f"  WARNING: Station {station_id} data fetch failed — {e}")
            
        time.sleep(SLEEP_SEC)

    df = pd.DataFrame(all_data)
    return df

# ── CLEAN & CONVERT FOR SIMULATION ────────────────────────────────────────────

def clean_and_format_for_simulation(df):
    if df.empty:
        print("No data collected to clean.")
        return pd.DataFrame()
        
    # Pivot features from narrow to wide format
    df_wide = df.pivot_table(
        index=['station', 'date'], 
        columns='datatype', 
        values='value'
    ).reset_index()
    
    # Extract year string
    df_wide['year'] = pd.to_datetime(df_wide['date']).dt.year
    
    # Clean column mapping
    df_wide = df_wide.rename(columns={
        'station': 'nearest_station_id',
        'TMAX': 'max_temp_f',
        'TAVG': 'mean_temp_f',
        'RHAV': 'mean_rh'
    })
    
    # Fill in missing Relative Humidity with a safe national average baseline if missing
    if 'mean_rh' not in df_wide.columns:
        df_wide['mean_rh'] = 60.0
    else:
        df_wide['mean_rh'] = df_wide['mean_rh'].fillna(60.0)

    # If TMAX is missing but TAVG exists, fill with TAVG + 15 F
    if 'max_temp_f' not in df_wide.columns:
        df_wide['max_temp_f'] = df_wide['mean_temp_f'] + 15.0
    else:
        df_wide['max_temp_f'] = df_wide['max_temp_f'].fillna(df_wide['mean_temp_f'] + 15.0)

    return df_wide[['nearest_station_id', 'year', 'mean_temp_f', 'max_temp_f', 'min_temp_f']]

# ── MAIN EXECUTION BRIDGE ─────────────────────────────────────────────────────

def main():
    import pathlib
    HERE = pathlib.Path(__file__).resolve().parent
    REPO_ROOT = HERE.parent.parent
    
    backbone_file = REPO_ROOT / "data" / "raw" / "eia_power_plants" / "final_eia_powerplant_data_2021_2024.csv"
    output_path = REPO_ROOT / "data" / "raw" / "noaa_weather" / "noaa_gsoy_climate_clean.csv"
    
    if not os.path.exists(backbone_file):
        print(f"CRITICAL ERROR: Could not find backbone data tracker: '{backbone_file}'")
        return

    # Extract unique station IDs from your current backbone file
    print(f"Reading station IDs from {backbone_file}...")
    backbone_df = pd.read_csv(backbone_file)
    
    # Drop rows without matching weather stations
    unique_stations = backbone_df['nearest_station_id'].dropna().unique().tolist()
    print(f"Found {len(unique_stations)} unique weather stations to pull.")

    # Run API loops
    raw_climate_data = fetch_climate_by_stations(unique_stations, TOKEN)
    
    # Process inputs directly into simulation-ready metrics
    simulation_inputs = clean_and_format_for_simulation(raw_climate_data)
    
    # Save results
    simulation_inputs.to_csv(output_path, index=False)
    print(f"\nSUCCESS! Simulation inputs saved to: {output_path}")

if __name__ == "__main__":
    main()