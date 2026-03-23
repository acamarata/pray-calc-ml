import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import r2_score, mean_absolute_error
from sklearn.ensemble import RandomForestRegressor
import warnings
warnings.filterwarnings('ignore')

def analyze_prayer(prayer_name, csv_file):
    print(f"\n{'='*50}")
    print(f" ML Analysis: {prayer_name.upper()}")
    print(f"{'='*50}")
    
    df = pd.read_csv(csv_file)
    target = f"{prayer_name}_angle"
    
    # Drop NaNs
    df = df.dropna(subset=['lat', 'day_of_year', target])
    
    X = df[['lat', 'day_of_year']]
    y = df[target]
    
    print(f"Total Rows: {len(df)}")
    
    # 1. Standard Linear Regression
    lr = LinearRegression()
    lr.fit(X, y)
    lr_pred = lr.predict(X)
    lr_r2 = r2_score(y, lr_pred)
    lr_mae = mean_absolute_error(y, lr_pred)
    
    print("\n--- Model 1: Linear Regression ---")
    print(f"R2: {lr_r2:.4f} | MAE: {lr_mae:.4f} degrees")
    print(f"Formula: Angle = {lr.intercept_:.4f} + ({lr.coef_[0]:.4f} * lat) + ({lr.coef_[1]:.4f} * day_of_year)")
    
    # 2. Polynomial Regression (Degree 2 - captures exponential/quadratic non-linear relationships)
    poly = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
    poly.fit(X, y)
    poly_pred = poly.predict(X)
    poly_r2 = r2_score(y, poly_pred)
    poly_mae = mean_absolute_error(y, poly_pred)
    
    print("\n--- Model 2: Polynomial (Non-Linear) Regression (Degree 2) ---")
    print(f"R2: {poly_r2:.4f} | MAE: {poly_mae:.4f} degrees")
    
    # Check if non-linear significantly outperforms linear
    if poly_r2 > lr_r2 + 0.05:
        print("-> CONCLUSION: The relationship is strongly non-linear/exponential.")
    else:
        print("-> CONCLUSION: The relationship is predominantly linear, with minimal exponential curvature.")
        
    # 3. Random Forest (Highly Non-Linear Trees)
    rf = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
    rf.fit(X, y)
    rf_pred = rf.predict(X)
    rf_r2 = r2_score(y, rf_pred)
    rf_mae = mean_absolute_error(y, rf_pred)
    
    print("\n--- Model 3: Random Forest (Non-linear Tree Ensembles) ---")
    print(f"R2: {rf_r2:.4f} | MAE: {rf_mae:.4f} degrees")
    
    # DPC/Moonsighting baseline simulated evaluation
    # Moonsighting historically uses dynamic formulas incorporating Latitude and Season (TOY)
    print("\n--- Feature Importance (Random Forest) ---")
    importance = rf.feature_importances_
    print(f"Latitude drives {importance[0]*100:.1f}% of the variance.")
    print(f"Day of Year (Season) drives {importance[1]*100:.1f}% of the variance.")
    
if __name__ == '__main__':
    analyze_prayer("fajr", "data/processed/fajr_angles.csv")
    analyze_prayer("isha", "data/processed/isha_angles.csv")
