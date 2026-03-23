import pandas as pd
import numpy as np
from sklearn.linear_model import RidgeCV, LassoCV, LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error
import warnings
warnings.filterwarnings('ignore')

def find_perfect_formula(prayer_name, csv_file):
    print(f"\n{'='*60}")
    print(f" ALGEBRAIC FORMULA EXTRACTION: {prayer_name.upper()}")
    print(f"{'='*60}")
    
    df = pd.read_csv(csv_file)
    target = f"{prayer_name}_angle"
    df = df.dropna(subset=['lat', 'day_of_year', 'elevation_m', target])
    
    # Base readily available 'pray-calc' variables
    df['lat_abs'] = df['lat'].abs()
    df['lat_sq'] = df['lat'] ** 2
    df['elev_sqrt'] = np.sqrt(df['elevation_m'].abs())
    
    # Sine/Cosine for Day of Year (Seasonality cyclic mapping)
    # The longest twilight is around solstice, shortest around equinox,
    # so we use a 1-year frequency harmonic.
    df['doy_sin'] = np.sin(2 * np.pi * df['day_of_year'] / 365.25)
    df['doy_cos'] = np.cos(2 * np.pi * df['day_of_year'] / 365.25)
    
    # Interaction
    df['lat_x_season'] = df['lat_abs'] * df['doy_cos']
    
    features = ['lat_abs', 'lat_sq', 'elev_sqrt', 'doy_sin', 'doy_cos', 'lat_x_season']
    X = df[features]
    y = df[target]
    
    # 1. Standardize (just to see which features matter most)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Use Lasso to zero-out useless variables (Sparsity for a "clean formula")
    lasso = LassoCV(cv=5)
    lasso.fit(X_scaled, y)
    
    # Filter features that survived Lasso
    surviving_idx = [i for i, coef in enumerate(lasso.coef_) if abs(coef) > 0.001]
    if not surviving_idx: # Fallback if everything zeroed out
        surviving_idx = [0, 1]
    
    surviving_features = [features[i] for i in surviving_idx]
    
    # 2. Refit Linear Regression on strictly the surviving features natively (unscaled) for exact formula constants!
    X_clean = df[surviving_features]
    lr = LinearRegression()
    lr.fit(X_clean, y)
    
    y_pred = lr.predict(X_clean)
    r2 = r2_score(y, y_pred)
    mae = mean_absolute_error(y, y_pred)
    
    print(f"Algorithm Selected: Clean Sparse Polynomial")
    print(f"Targeting: Latitude, Seasonality Harmonics, Elevation")
    print(f"Mathematical Accuracy: MAE = {mae:.3f} degrees | R^2 = {r2:.4f}")
    
    print("\n--- THE PERFECT ALGEBRAIC FORMULA ---")
    
    formula = f"D0_base = {lr.intercept_:.4f}"
    for feat, coef in zip(surviving_features, lr.coef_):
        sign = "+" if coef >= 0 else "-"
        formula += f"\n          {sign} {abs(coef):.6f} * {feat}"
        
    print(formula)
    
    print("\n--- COPY-PASTE PYTHON IMPLEMENTATION ---")
    print(f"def get_{prayer_name}_angle(lat, day_of_year, elevation_m):")
    print(f"    import numpy as np")
    print(f"    import math")
    print(f"    lat_abs = abs(lat)")
    if 'lat_sq' in surviving_features:
        print(f"    lat_sq = lat ** 2")
    if 'elev_sqrt' in surviving_features:
        print(f"    elev_sqrt = math.sqrt(max(0, elevation_m))")
    if 'doy_sin' in surviving_features:
        print(f"    doy_sin = math.sin(2 * math.pi * day_of_year / 365.25)")
    if 'doy_cos' in surviving_features:
        print(f"    doy_cos = math.cos(2 * math.pi * day_of_year / 365.25)")
    if 'lat_x_season' in surviving_features:
        print(f"    lat_x_season = lat_abs * doy_cos")
        
    eq = f"    return {lr.intercept_:.4f}"
    for feat, coef in zip(surviving_features, lr.coef_):
        sign = "+" if coef >= 0 else "-"
        eq += f" {sign} ({abs(coef):.6f} * {feat})"
    print(eq)
    print("="*60)

if __name__ == '__main__':
    find_perfect_formula("fajr", "data/processed/fajr_angles.csv")
    find_perfect_formula("isha", "data/processed/isha_angles.csv")
