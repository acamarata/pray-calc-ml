"""
Processor for the Madrid Zenodo SQM dataset (Record 4633001).

This script reads data/raw/massive_sqm/SQM_evol.csv, representing 10 years of
continuous minute-by-minute Sky Quality Meter readings in Madrid, Spain.

We apply the BRIN inflection-point detection algorithm:
- Fajr: Moment of steepest SQM decline in the pre-dawn window.
- Isha: Moment SQM reaches within 0.5 mag of the dark-night baseline.

Output: data/raw/raw_sightings/madrid_sqm_10yr.csv
"""

import math
from pathlib import Path
from datetime import datetime, timezone, timedelta
import pandas as pd
import ephem

# Madrid UCM Observatory from paper metadata
LAT = 40.45 
LNG = -3.73
ELEVATION_M = 640
UTC_OFFSET = 1.0  # Winter UTC+1, though data is in UTC so we just use this for local labeling

RAW_CSV = Path("data/raw/massive_sqm/SQM_evol.csv")
OUT_FILE = Path("data/raw/raw_sightings/madrid_sqm_10yr.csv")

MIN_DARK_SKY_MPSAS = 18.0
MAX_MOON_ALT = 5.0

def get_solar_altitude(utc_dt: datetime) -> float:
    obs = ephem.Observer()
    obs.lat = str(LAT)
    obs.lon = str(LNG)
    obs.elevation = ELEVATION_M
    obs.pressure = 1013.25
    obs.temp = 15.0
    if utc_dt.tzinfo is not None:
        utc_dt = utc_dt.replace(tzinfo=None)
    obs.date = ephem.Date(utc_dt)
    sun = ephem.Sun(obs)
    return math.degrees(float(sun.alt))

def process_madrid_data():
    if not RAW_CSV.exists():
        print(f"File not found: {RAW_CSV}")
        return

    print("Loading Madrid SQM dataset. This may take a minute...")
    # Format: Time(UTC);Magnitude
    df = pd.read_csv(RAW_CSV, sep=';', usecols=['Time(UTC)', 'Magnitude'])
    df['utc_dt'] = pd.to_datetime(df['Time(UTC)']).dt.tz_localize(timezone.utc)
    df = df.rename(columns={'Magnitude': 'mpsas'})
    
    # Filter bad data
    df = df[df['mpsas'] > 0]
    df = df.sort_values('utc_dt').reset_index(drop=True)

    print(f"Loaded {len(df)} rows. Processing nights...")
    
    # Identify unique local calendar dates in the dataset
    df['local_date'] = (df['utc_dt'] + timedelta(hours=UTC_OFFSET)).dt.date
    unique_dates = df['local_date'].unique()
    
    records = []
    
    obs = ephem.Observer()
    obs.lat = str(LAT)
    obs.lon = str(LNG)
    obs.elevation = ELEVATION_M
    obs.pressure = 1013.25
    obs.temp = 15.0

    print(f"Found {len(unique_dates)} nights to process.")
    for local_date in unique_dates:
        # Midnight UTC for the given local date
        noon_utc = datetime(local_date.year, local_date.month, local_date.day, 12, 0, tzinfo=timezone.utc) - timedelta(hours=UTC_OFFSET)
        
        obs.date = ephem.Date(noon_utc.replace(tzinfo=None))
        try:
            sunset_utc = obs.next_setting(ephem.Sun()).datetime().replace(tzinfo=timezone.utc)
            sunrise_utc = obs.next_rising(ephem.Sun()).datetime().replace(tzinfo=timezone.utc)
        except ephem.AlwaysUpError:
            continue
        except ephem.NeverUpError:
            continue

        # FAJR
        window_start = sunrise_utc - timedelta(hours=5)
        window_end = sunrise_utc - timedelta(minutes=10)
        predawn = df[(df['utc_dt'] >= window_start) & (df['utc_dt'] <= window_end)].copy()
        
        if len(predawn) >= 30:
            predawn['sun_alt'] = [get_solar_altitude(dt) for dt in predawn['utc_dt']]
            predawn = predawn[predawn['sun_alt'] < -5.0]
            
            early = predawn[predawn['sun_alt'] < -18.0]
            if early.empty: 
                early = predawn[predawn['sun_alt'] < -16.0]
            if not early.empty and early['mpsas'].max() >= MIN_DARK_SKY_MPSAS:
                predawn['mpsas_smooth'] = predawn['mpsas'].rolling(window=5, center=True, min_periods=3).mean()
                predawn['dmpsas'] = predawn['mpsas_smooth'].diff()
                
                active = predawn[(predawn['sun_alt'] >= -25.0) & (predawn['sun_alt'] <= -5.0)]
                if len(active) >= 10:
                    steepest_idx = active['dmpsas'].idxmin()
                    if not pd.isna(steepest_idx):
                        dawn_row = predawn.loc[steepest_idx]
                        depression_angle = -dawn_row['sun_alt']
                        
                        if 10.0 <= depression_angle <= 22.0:
                            local_time = dawn_row['utc_dt'] + timedelta(hours=UTC_OFFSET)
                            records.append({
                                "prayer": "fajr",
                                "date_local": local_time.strftime("%Y-%m-%d"),
                                "time_local": local_time.strftime("%H:%M"),
                                "utc_offset": UTC_OFFSET,
                                "lat": LAT,
                                "lng": LNG,
                                "elevation_m": ELEVATION_M,
                                "source": "Madrid Zenodo SQM (10-year)",
                                "notes": f"SQM inflection point Fajr detection; Madrid UCM Observatory; dark-sky baseline>={MIN_DARK_SKY_MPSAS}"
                            })

        # ISHA
        window_end_isha = sunset_utc + timedelta(hours=5)
        evening = df[(df['utc_dt'] >= sunset_utc) & (df['utc_dt'] <= window_end_isha)].copy()
        
        if len(evening) >= 30:
            evening['sun_alt'] = [get_solar_altitude(dt) for dt in evening['utc_dt']]
            evening = evening[evening['sun_alt'] < 0]
            
            deep_night = evening[(evening['utc_dt'] >= sunset_utc + timedelta(hours=2)) & 
                               (evening['utc_dt'] <= sunset_utc + timedelta(hours=6)) &
                               (evening['sun_alt'] < -18.0)]
                               
            if len(deep_night) >= 10:
                dark_baseline = deep_night['mpsas'].median()
                if dark_baseline >= MIN_DARK_SKY_MPSAS:
                    evening['mpsas_smooth'] = evening['mpsas'].rolling(window=5, center=True, min_periods=3).mean()
                    threshold = dark_baseline - 0.5
                    
                    reached = evening[(evening['mpsas_smooth'] >= threshold) & (evening['sun_alt'] < -12.0)]
                    if not reached.empty:
                        isha_row = reached.iloc[0]
                        depression_angle = -isha_row['sun_alt']
                        
                        if 12.0 <= depression_angle <= 22.0:
                            local_time = isha_row['utc_dt'] + timedelta(hours=UTC_OFFSET)
                            records.append({
                                "prayer": "isha",
                                "date_local": local_time.strftime("%Y-%m-%d"),
                                "time_local": local_time.strftime("%H:%M"),
                                "utc_offset": UTC_OFFSET,
                                "lat": LAT,
                                "lng": LNG,
                                "elevation_m": ELEVATION_M,
                                "source": "Madrid Zenodo SQM (10-year)",
                                "notes": f"SQM threshold Isha detection (Shafaq Abyad); dark-sky baseline={dark_baseline:.2f}"
                            })

    out_df = pd.DataFrame(records)
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    out_df.to_csv(OUT_FILE, index=False)
    print(f"Successfully processed {len(records)} Fajr/Isha observations to {OUT_FILE}.")

if __name__ == "__main__":
    process_madrid_data()
