"""
build_dataset.py
================
Builds the core analytical dataset by merging raw EIA power plant data with 
NOAA climate observations. Replaces the old physics-simulation pipeline.
"""

import pandas as pd
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
DATA_RAW = REPO_ROOT / "data" / "raw"
DATA_OUT = REPO_ROOT / "data" / "processed"

def run_pipeline():
    # 1. Load Data
    eia_path = DATA_RAW / "eia_power_plants" / "final_eia_powerplant_data_2021_2024.csv"
    noaa_path = DATA_RAW / "noaa_weather" / "noaa_gsoy_climate_clean.csv"
    
    print(">>> Loading raw datasets...")
    eia_df = pd.read_csv(eia_path)
    noaa_df = pd.read_csv(noaa_path)
    
    print(f"EIA rows: {len(eia_df):,} | NOAA rows: {len(noaa_df):,}")

    # 2. Merge Data
    print(">>> Merging datasets...")
    overlap = [c for c in noaa_df.columns if c in eia_df.columns and c not in ['nearest_station_id', 'year']]
    eia_df.drop(columns=overlap, inplace=True, errors='ignore')
    
    master_df = eia_df.merge(
        noaa_df,
        on=['nearest_station_id', 'year'],
        how='inner'
    )
    
    # 3. Apply Filters (replacing logic from old trim_data.py)
    print(">>> Applying quality filters...")
    trimmed_mask = (
        master_df['consumption_mg'].notna() &
        ((master_df['consumption_mg'] > 0) | (master_df['cooling_category'] == 'Dry-Hybrid')) &
        master_df['net_gen_mwh'].notna() &
        (master_df['net_gen_mwh'] > 0) &
        ~(master_df['consumption_mg'] > master_df['withdrawal_mg']) &
        (master_df['primary_fuel'] != 'PRG')
    )
    
    ml_df = master_df.loc[trimmed_mask].copy()
    
    # 4. Unit Conversions (MG to ML)
    print(">>> Converting units (MG to ML)...")
    ml_df['consumption_ML'] = ml_df['consumption_mg'] * 3.78541
    ml_df['withdrawal_ML']  = ml_df['withdrawal_mg'] * 3.78541
    ml_df['discharge_ML']   = ml_df['discharge_mg'] * 3.78541
    
    if 'state_water_intensity_gal_mwh' in ml_df.columns:
        ml_df['state_water_intensity_L_per_MWh'] = ml_df['state_water_intensity_gal_mwh'] * 3.78541
    
    # 5. Clean up relic simulation variables
    relics = ['T_oa_celsius', 'RH_oa_pct', 'P_oa_pa']
    ml_df.drop(columns=relics, inplace=True, errors='ignore')

    # Select final columns as expected by notebooks
    FINAL_COLS = [
        'plant_code', 'plant_name', 'year', 'state', 'net_gen_mwh', 
        'consumption_ML', 'withdrawal_ML', 'discharge_ML', 'facility_age_yrs', 
        'cooling_category', 'cooling_type_eia', 'n_cooling_systems', 'primary_fuel', 
        'LAT', 'LON', 'ashrae_zone', 'moisture_regime', 'ba_climate_zone', 'bws_raw', 
        'max_temp_f', 'min_temp_f', 'mean_temp_f', 'state_water_intensity_L_per_MWh', 
        'capacity_mw'
    ]
    
    final_cols = [c for c in FINAL_COLS if c in ml_df.columns]
    ml_df = ml_df[final_cols]
    
    # 6. Export
    out_path = DATA_OUT / "Preprocessed_Power_Plant_Data.csv"
    ml_df.to_csv(out_path, index=False)
    print(f"\nSUCCESS! Created dataset with {len(ml_df):,} rows and {len(ml_df.columns)} columns.")
    print(f"Saved to: {out_path}")

if __name__ == "__main__":
    run_pipeline()
