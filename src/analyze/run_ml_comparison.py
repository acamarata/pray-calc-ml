import pandas as pd
import numpy as np
import warnings
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from scipy.optimize import curve_fit

warnings.filterwarnings("ignore")

def exp_func(x, a, b, c):
    return a * np.exp(b * x) + c

def eval_algorithms(df, name):
    print(f"\n==========================================")
    print(f"       {name.upper()} ML PATTERN ANALYSIS       ")
    print(f"==========================================")
    print(f"Total verified observations: {len(df)}")
    
    # Check column name for angle
    angle_col = f"{name.lower()}_angle"
    if angle_col not in df.columns:
        print(f"Error: {angle_col} not found in columns")
        return
        
    df['doy'] = df['day_of_year']
    df['lat_abs'] = df['lat'].abs()
    
    # Missing value cleaning just in case
    df = df.dropna(subset=[angle_col, 'doy', 'lat_abs'])
    
    # 1. Seasonality Feature Engineering (Sin/Cos mapping of Time of Year)
    df['doy_sin'] = np.sin(2 * np.pi * df['doy'] / 365)
    df['doy_cos'] = np.cos(2 * np.pi * df['doy'] / 365)
    
    X_lat = df[['lat_abs']].values
    X_all = df[['lat_abs', 'doy_sin', 'doy_cos']].values
    y = df[angle_col].values
    
    # --- A. BASELINE FIXED ALGORITHM (ISNA/MWL style: 15° or 18°) ---
    print("\n[A] STATIC ALGORITHM BENCHMARKS (15° vs 18°)")
    mae_15 = mean_absolute_error(y, np.full_like(y, 15.0))
    mae_18 = mean_absolute_error(y, np.full_like(y, 18.0))
    print(f"   Fixed 15° Error (MAE): {mae_15:.3f}°")
    print(f"   Fixed 18° Error (MAE): {mae_18:.3f}°")

    # --- B. LATITUDE ONLY (Linear vs Exponential) ---
    print("\n[B] LATITUDE PATTERNS (Equator distance vs Angle)")
    
    # Linear Latitude
    lr_lat = LinearRegression().fit(X_lat, y)
    y_pred_lat_lin = lr_lat.predict(X_lat)
    print(f"   Linear Latitude Fit      : R2={r2_score(y, y_pred_lat_lin):.3f}, MAE={mean_absolute_error(y, y_pred_lat_lin):.3f}°")
    print(f"   -> Coefficient: {lr_lat.coef_[0]:.4f} degrees per 1° latitude move")
    
    # Exponential Latitude
    try:
        # We model the depression angle dropping exponentially toward the poles
        popt, _ = curve_fit(exp_func, df['lat_abs'], y, p0=[-1, 0.05, 18], maxfev=5000)
        y_pred_lat_exp = exp_func(df['lat_abs'], *popt)
        r2_exp = r2_score(y, y_pred_lat_exp)
        mae_exp = mean_absolute_error(y, y_pred_lat_exp)
        print(f"   Exponential Latitude Fit : R2={r2_exp:.3f}, MAE={mae_exp:.3f}°")
    except Exception as e:
        print(f"   Exponential Fit failed: {e}")

    # --- C. TIME OF YEAR (SEASONALITY) IMPACT ---
    print("\n[C] TIME OF YEAR (SEASONAL) CORRELATIONS")
    lr_all = LinearRegression().fit(X_all, y)
    y_pred_all = lr_all.predict(X_all)
    print(f"   Combined Model (Lat + Seasonality): R2={r2_score(y, y_pred_all):.3f}, MAE={mean_absolute_error(y, y_pred_all):.3f}°")
    
    # Feature Importance
    print(f"   -> Lat Importance   : {abs(lr_all.coef_[0]):.4f}")
    print(f"   -> TOY (Season) Sine: {abs(lr_all.coef_[1]):.4f} amplitude")
    
    # --- D. DYNAMIC ALGORITHM COMPARISON ---
    high_lat_mask = df['lat_abs'] > 40
    if sum(high_lat_mask) > 0:
        high_lat_mean = df[high_lat_mask][angle_col].mean()
        low_lat_mean = df[~high_lat_mask][angle_col].mean()
        print(f"\n[D] ALGORITHMIC COMPARISON")
        print(f"   Mean empirical angle at >40° Lat  : {high_lat_mean:.2f}°")
        print(f"   Mean empirical angle at <=40° Lat : {low_lat_mean:.2f}°")
        shift = low_lat_mean - high_lat_mean
        print(f"   Shift detected: {shift:.2f}° absolute reduction when moving towards poles.")
        if shift > 0.5:
            print("   => Matches Moonsighting/DPC dynamic logic (angles drop significantly at higher latitudes).")
        else:
            print("   => Does NOT strongly match Moonsighting dynamic logic.")

if __name__ == '__main__':
    try:
        fajr_df = pd.read_csv('data/processed/fajr_angles.csv')
        eval_algorithms(fajr_df, 'Fajr')
    except Exception as e:
        print("Missing Fajr dataset:", e)
        
    try:
        isha_df = pd.read_csv('data/processed/isha_angles.csv')
        eval_algorithms(isha_df, 'Isha')
    except Exception as e:
        print("Missing Isha dataset:", e)
