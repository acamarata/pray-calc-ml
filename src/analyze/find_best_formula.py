import pandas as pd
import numpy as np
import warnings
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.pipeline import make_pipeline

warnings.filterwarnings("ignore")

def find_best_formula(df, name):
    print(f"\n=======================================================")
    print(f"   {name.upper()} EXHAUSTIVE ML FORMULA SEARCH   ")
    print(f"=======================================================")
    
    # Filter missing values
    angle_col = f"{name.lower()}_angle"
    df = df.dropna(subset=[angle_col, 'lat', 'day_of_year', 'elevation_m'])
    
    # Target and Features restricted to Mobile-App-Available variables
    y = df[angle_col].values
    
    # Features
    lat_abs = df['lat'].abs().values
    elev = df['elevation_m'].values
    doy = df['day_of_year'].values
    doy_sin = np.sin(2 * np.pi * doy / 365.25)
    doy_cos = np.cos(2 * np.pi * doy / 365.25)
    
    X = np.column_stack((lat_abs, doy_sin, doy_cos, elev))
    feature_names = ['Lat', 'Season_Sin', 'Season_Cos', 'Elevation']
    
    print(f"Dataset Size: {len(y)} verified rows")
    print(f"Base Average (15° model): MAE = {mean_absolute_error(y, np.full_like(y, 15.0)):.3f}°\n")
    
    # --- 1. RANDOM FOREST (The Black Box Upper Bound) ---
    # This tells us the ABSOLUTE maximum achievable accuracy if we had a perfect infinite formula
    rf = RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf.fit(X, y)
    rf_preds = rf.predict(X)
    print(f"[1] Random Forest (Non-Linear Black Box)")
    print(f"    R2 = {r2_score(y, rf_preds):.4f} | MAE = {mean_absolute_error(y, rf_preds):.4f}°")
    print(f"    Feature Importance: Lat={rf.feature_importances_[0]:.2f}, Season_Sin={rf.feature_importances_[1]:.2f}, Season_Cos={rf.feature_importances_[2]:.2f}, Elev={rf.feature_importances_[3]:.2f}\n")
    
    # --- 2. GRADIENT BOOSTING (Sequential Error Correction) ---
    gb = GradientBoostingRegressor(n_estimators=100, learning_rate=0.1, max_depth=5, random_state=42)
    gb.fit(X, y)
    gb_preds = gb.predict(X)
    print(f"[2] Gradient Boosting (XGBoost logic)")
    print(f"    R2 = {r2_score(y, gb_preds):.4f} | MAE = {mean_absolute_error(y, gb_preds):.4f}°\n")
    
    # --- 3. POLYNOMIAL REGRESSION (Degree 2) - The "Clean Formula" ---
    # This gives us a highly complex mathematical equation we can actually deploy in a mobile app
    poly2 = PolynomialFeatures(degree=2, include_bias=False)
    X_poly2 = poly2.fit_transform(X)
    lr2 = Ridge(alpha=1.0).fit(X_poly2, y)
    poly2_preds = lr2.predict(X_poly2)
    
    print(f"[3] 2nd Degree Polynomial Formula (Clean Math Equation)")
    print(f"    R2 = {r2_score(y, poly2_preds):.4f} | MAE = {mean_absolute_error(y, poly2_preds):.4f}°")
    
    # --- 4. POLYNOMIAL REGRESSION (Degree 3) - The "Advanced Clean Formula" ---
    poly3 = PolynomialFeatures(degree=3, include_bias=False)
    X_poly3 = poly3.fit_transform(X)
    lr3 = Ridge(alpha=5.0).fit(X_poly3, y)
    poly3_preds = lr3.predict(X_poly3)
    
    print(f"[4] 3rd Degree Polynomial Formula (Advanced Math Equation)")
    print(f"    R2 = {r2_score(y, poly3_preds):.4f} | MAE = {mean_absolute_error(y, poly3_preds):.4f}°\n")
    
    # Output the BEST mathematical formula (We'll use Degree 2 for brevity and readability)
    print(f"--- BEST EXTRACTABLE EQUATION (Polynomial Degree 2) ---")
    intercept = lr2.intercept_
    coefs = lr2.coef_
    poly_names = poly2.get_feature_names_out(feature_names)
    
    equation_str = f"Angle = {intercept:.4f}\n"
    for name, c in zip(poly_names, coefs):
        if abs(c) > 0.0001:  # Only show meaningful weights
            sign = "+" if c > 0 else "-"
            # Format nicely
            name = name.replace(" ", " * ")
            equation_str += f"        {sign} {abs(c):.4f} * ({name})\n"
            
    print(equation_str)

if __name__ == '__main__':
    try:
        fajr_df = pd.read_csv('data/processed/fajr_angles.csv')
        find_best_formula(fajr_df, 'Fajr')
    except Exception as e:
        print("Error Fajr:", e)
        
    try:
        isha_df = pd.read_csv('data/processed/isha_angles.csv')
        find_best_formula(isha_df, 'Isha')
    except Exception as e:
        print("Error Isha:", e)
