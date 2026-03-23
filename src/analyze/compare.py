import pandas as pd
import numpy as np
import os

def dpc_algorithm(row, prayer):
    # DPC strictly enforces 18.0 degrees for both
    return 18.0

def _ms_fajr(lat):
    # Approximation of Khalid Shaukat moonsighting algorithm curve
    # 18 at equator, dropping incrementally past 30 deg to ~12.0
    abslat = abs(lat)
    if abslat <= 30:
        return 18.0
    else:
        # Linear drop from 18.0 at 30 deg down to 12.0 at 55 deg
        val = 18.0 - ((abslat - 30) * (6.0/25.0))
        return max(10.0, val)
        
def ms_algorithm(row, prayer):
    if prayer == "fajr":
        return _ms_fajr(row['lat'])
    else:
        # Isha is slightly more forgiving or static
        return _ms_fajr(row['lat'])

def run_evaluation(df, prayer):
    print(f"\n>> Algorithm Benchmark: {prayer.upper()} ({len(df)} Records)")
    empirical = df[f'{prayer}_angle'].values
    
    dpc_preds = np.array([dpc_algorithm(row, prayer) for _, row in df.iterrows()])
    ms_preds  = np.array([ms_algorithm(row, prayer) for _, row in df.iterrows()])
    
    dpc_mae = np.mean(np.abs(empirical - dpc_preds))
    dpc_rmse = np.sqrt(np.mean((empirical - dpc_preds)**2))
    
    ms_mae = np.mean(np.abs(empirical - ms_preds))
    ms_rmse = np.sqrt(np.mean((empirical - ms_preds)**2))
    
    print(f"DPC (18/18 static)         -> MAE: {dpc_mae:.3f}°, RMSE: {dpc_rmse:.3f}°")
    print(f"Moonsighting (Variable)    -> MAE: {ms_mae:.3f}°,  RMSE: {ms_rmse:.3f}°")
    
    best = "DPC" if dpc_mae < ms_mae else "Moonsighting Variant"
    print(f"WINNER: {best} predicts the physical reality more accurately.")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    fajr_path = os.path.join(base_dir, "data", "processed", "fajr_angles.csv")
    isha_path = os.path.join(base_dir, "data", "processed", "isha_angles.csv")
    
    if os.path.exists(fajr_path):
        run_evaluation(pd.read_csv(fajr_path), "fajr")
    if os.path.exists(isha_path):
        run_evaluation(pd.read_csv(isha_path), "isha")

if __name__ == "__main__":
    main()
