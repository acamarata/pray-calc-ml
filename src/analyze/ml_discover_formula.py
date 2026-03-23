import pandas as pd
import numpy as np
from scipy.optimize import curve_fit
import os

# ---------------------------------------------------------
# Candidate Biological/Astronomical Formula Definitions
# x is a 2D array: x[0] = abs(lat), x[1] = elevation, x[2] = doy
# ---------------------------------------------------------

def eq1_static(x, a):
    return np.full_like(x[0], a)

def eq2_lin_lat(x, a, b):
    return a + b * x[0]

def eq3_quad_lat(x, a, b, c):
    return a + b * x[0] + c * (x[0]**2)

def eq4_lat_season(x, a, b, c, d):
    # c is amplitude, d is phase shift
    return a + b * x[0] + c * np.cos(2 * np.pi * (x[2] - d) / 365.25)

def eq5_elev_lat_season(x, a, b, c, d, e):
    return a + b * x[0] + c * x[1] + d * np.cos(2 * np.pi * (x[2] - e) / 365.25)

def eq6_lat_dependent_season(x, a, b, c, d):
    # Amplitude of season scales with latitude
    return a + b * x[0] + c * x[0] * np.cos(2 * np.pi * (x[2] - d) / 365.25)

def eq7_the_beautiful_match(x, a, b, c, d, e, f):
    # The ultimate clean parametric equation
    # Base + A*Lat + B*Lat^2 + C*Elev + D*Lat*Season + E*Season
    lat = x[0]
    elev = x[1]
    season = np.cos(2 * np.pi * (x[2] - f) / 365.25)
    return a + b * lat + c * (lat**2) + d * elev + e * lat * season

# Map functions to their string representations for readable output
FORMULAS = [
    ("Static Baseline", eq1_static, ["Base"]),
    ("Linear Latitude", eq2_lin_lat, ["Base", "Lat_Coeff"]),
    ("Quadratic Latitude", eq3_quad_lat, ["Base", "Lat_Coeff", "Lat2_Coeff"]),
    ("Latitude + Season", eq4_lat_season, ["Base", "Lat_Coeff", "Season_Amp", "Phase_Shift"]),
    ("Elevation + Lat + Season", eq5_elev_lat_season, ["Base", "Lat_Coeff", "Elev_Coeff", "Season_Amp", "Phase_Shift"]),
    ("Lat-Dependent Season", eq6_lat_dependent_season, ["Base", "Lat_Coeff", "Season_Lat_Scale", "Phase_Shift"]),
    ("The Beautiful Match", eq7_the_beautiful_match, ["Base", "Lat_C", "Lat2_C", "Elev_C", "LatXSeason_C", "Phase_Shift"])
]

def analyze_formula(df, prayer):
    print(f"\n{'='*70}\n[ {prayer.upper()} ALGORITHM DISCOVERY ] - {len(df)} Records\n{'='*70}")
    
    # Prepare input vectors
    lat_arr = np.abs(df['lat'].values)
    elev_arr = df['elevation_m'].values
    doy_arr = df['day_of_year'].values
    y = df[f'{prayer}_angle'].values
    
    x = np.vstack((lat_arr, elev_arr, doy_arr))
    
    best_mae = float('inf')
    best_name = None
    best_params = None
    best_popt = None
    best_func = None
    
    for name, func, param_names in FORMULAS:
        # Initial guess (15.0 for base, 0 for others)
        p0 = [15.0] + [0.0] * (len(param_names)-1)
        # Bounding Phase_Shift safely if it exists (usually the last param if 'Phase_Shift' is there)
        bounds = (-np.inf, np.inf)
        
        try:
            popt, pcov = curve_fit(func, x, y, p0=p0, maxfev=10000)
            
            y_pred = func(x, *popt)
            mae = np.mean(np.abs(y - y_pred))
            rmse = np.sqrt(np.mean((y - y_pred)**2))
            
            print(f"--- {name} ---")
            print(f"MAE: {mae:.4f}° | RMSE: {rmse:.4f}°")
            params_str = ", ".join([f"{n}={v:.5f}" for n, v in zip(param_names, popt)])
            print(f"Parameters: {params_str}")
            print()
            
            if mae < best_mae:
                best_mae = mae
                best_name = name
                best_params = params_str
                best_popt = popt
                best_func = func
                
        except Exception as e:
            print(f"Failed to fit {name}: {e}")
            
    print(f"\n>> 🏆 WINNING FORMULA FOR {prayer.upper()}: {best_name}")
    print(f">> BEST MAE: {best_mae:.4f}°")
    print(f">> CONSTANTS: {best_params}")
    
    # Construct the human-readable clean mathematical equation
    if best_name == "The Beautiful Match":
        a, b, c, d, e, f = best_popt
        eq_str = (
            f"Angle = {a:.4f} "
            f"{'+' if b>=0 else '-'} {abs(b):.5f} * abs(Lat) "
            f"{'+' if c>=0 else '-'} {abs(c):.5f} * Lat² "
            f"{'+' if d>=0 else '-'} {abs(d):.5f} * Elevation "
            f"{'+' if e>=0 else '-'} {abs(e):.5f} * abs(Lat) * cos(2π * (DayOfYear - {f:.1f}) / 365)"
        )
        print(f"\n✨ THE CLEAN FORMULA ✨\n{eq_str}\n")
    elif best_name == "Lat-Dependent Season":
        a, b, c, d = best_popt
        eq_str = (
            f"Angle = {a:.4f} "
            f"{'+' if b>=0 else '-'} {abs(b):.5f} * abs(Lat) "
            f"{'+' if c>=0 else '-'} {abs(c):.5f} * abs(Lat) * cos(2π * (DayOfYear - {d:.1f}) / 365)"
        )
        print(f"\n✨ THE CLEAN FORMULA ✨\n{eq_str}\n")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    fajr_path = os.path.join(base_dir, "data", "processed", "fajr_angles.csv")
    isha_path = os.path.join(base_dir, "data", "processed", "isha_angles.csv")
    
    # 1. Clean outliers aggressively to find the mathematically purest underlying signal
    # We will filter out angles < 10 and > 22 for absolute pure signal matching
    if os.path.exists(fajr_path):
        df = pd.read_csv(fajr_path)
        df_clean = df[(df['fajr_angle'] >= 10.0) & (df['fajr_angle'] <= 20.0)]
        analyze_formula(df_clean, "fajr")
        
    if os.path.exists(isha_path):
        df = pd.read_csv(isha_path)
        df_clean = df[(df['isha_angle'] >= 11.0) & (df['isha_angle'] <= 21.0)]
        analyze_formula(df_clean, "isha")

if __name__ == "__main__":
    main()
