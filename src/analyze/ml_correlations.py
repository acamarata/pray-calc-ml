import pandas as pd
import numpy as np
import os
import sys

def evaluate_models(df, prayer):
    print(f"\n{'='*50}\nML Feature Discovery: {prayer.upper()} ({len(df)} records)\n{'='*50}")
    
    if len(df) == 0:
        return
        
    df['sin_toy'] = np.sin(2 * np.pi * df['day_of_year'] / 365.25)
    df['cos_toy'] = np.cos(2 * np.pi * df['day_of_year'] / 365.25)
    
    # 1. Correlation Matrix
    cols = ['lat', 'elevation_m', 'day_of_year', 'sin_toy', 'cos_toy', f'{prayer}_angle']
    corr = df[cols].corr()
    print("\n--- Pearson Correlation Matrix ---")
    print(corr[f'{prayer}_angle'].sort_values(ascending=False).to_string())
    
    # 2. Linear vs Polynomial (Exponential/Curved) Evaluation
    # Testing Latitude relationship
    lat_val = df['lat'].values
    angle_val = df[f'{prayer}_angle'].values
    
    # Linear Fit: y = ax + b
    p_lin = np.polyfit(lat_val, angle_val, 1)
    y_lin = np.polyval(p_lin, lat_val)
    ss_res_lin = np.sum((angle_val - y_lin) ** 2)
    ss_tot = np.sum((angle_val - np.mean(angle_val)) ** 2)
    r2_lin = 1 - (ss_res_lin / ss_tot)
    
    # Polynomial Fit (Degree 3): y = ax^3 + bx^2 + cx + d
    p_poly = np.polyfit(lat_val, angle_val, 3)
    y_poly = np.polyval(p_poly, lat_val)
    ss_res_poly = np.sum((angle_val - y_poly) ** 2)
    r2_poly = 1 - (ss_res_poly / ss_tot)
    
    print("\n--- Linear vs Exponential (Polynomial) Latitude Dependency ---")
    print(f"Linear Fit R²:     {r2_lin:.4f}")
    print(f"Polynomial Fit R²: {r2_poly:.4f}")
    if r2_poly > r2_lin + 0.05:
        print(">> OBSERVATION: The relationship with Latitude is highly EXPONENTIAL/NON-LINEAR.")
    else:
        print(">> OBSERVATION: The relationship with Latitude is mostly LINEAR or very weak overall.")
        
    # 3. Monthly / Seasonal Aggregation
    df['month'] = pd.to_datetime(df['date']).dt.month
    monthly_mean = df.groupby('month')[f'{prayer}_angle'].mean()
    print("\n--- Seasonal (Time of Year) Impact ---")
    print("Mean Angle by Month:")
    print(monthly_mean.to_string())
    season_variance = monthly_mean.max() - monthly_mean.min()
    print(f">> OBSERVATION: Seasonal fluctuation variance is {season_variance:.2f}°")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    fajr_path = os.path.join(base_dir, "data", "processed", "fajr_angles.csv")
    isha_path = os.path.join(base_dir, "data", "processed", "isha_angles.csv")
    
    try:
        fajr_df = pd.read_csv(fajr_path)
        evaluate_models(fajr_df, "fajr")
    except Exception as e:
        print(f"Fajr parse error: {e}")
        
    try:
        isha_df = pd.read_csv(isha_path)
        evaluate_models(isha_df, "isha")
    except Exception as e:
        print(f"Isha parse error: {e}")

if __name__ == "__main__":
    main()
