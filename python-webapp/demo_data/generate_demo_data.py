"""
Generate realistic demo data for yield curve analysis
Creates sample data that mimics ECB yield curve structure
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set seed for reproducibility
np.random.seed(42)

# Date range: 2 years of daily data
start_date = datetime(2022, 1, 1)
end_date = datetime(2023, 12, 31)
dates = pd.date_range(start_date, end_date, freq='D')

# Maturities (all 32 ECB maturities)
maturities = [
    'SR_3M', 'SR_6M', 'SR_1Y', 'SR_2Y', 'SR_3Y', 'SR_4Y', 'SR_5Y',
    'SR_6Y', 'SR_7Y', 'SR_8Y', 'SR_9Y', 'SR_10Y', 'SR_11Y', 'SR_12Y',
    'SR_13Y', 'SR_14Y', 'SR_15Y', 'SR_16Y', 'SR_17Y', 'SR_18Y', 'SR_19Y',
    'SR_20Y', 'SR_21Y', 'SR_22Y', 'SR_23Y', 'SR_24Y', 'SR_25Y', 'SR_26Y',
    'SR_27Y', 'SR_28Y', 'SR_29Y', 'SR_30Y'
]

# Maturity values in years for modeling
maturity_years = [0.25, 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
                  16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30]

# Generate realistic yield curve data
n_days = len(dates)
n_maturities = len(maturities)

# Base yield curve (upward sloping)
base_curve = np.array([0.5 + 0.08 * np.log(1 + m) for m in maturity_years])

# Generate time-varying yields
yield_data = []

for day in range(n_days):
    # Time-varying factors
    t = day / n_days

    # Level shift (overall yield level changes)
    level_shift = 0.5 * np.sin(2 * np.pi * t * 3) + 0.3 * np.random.randn()

    # Slope change (yield curve steepness)
    slope_factor = 0.02 * np.cos(2 * np.pi * t * 2) + 0.01 * np.random.randn()
    slope_shift = np.array([slope_factor * m for m in maturity_years])

    # Curvature change (yield curve bending)
    curvature_factor = 0.01 * np.sin(2 * np.pi * t * 4) + 0.005 * np.random.randn()
    curvature_shift = np.array([curvature_factor * (m ** 2) * 0.01 for m in maturity_years])

    # Random noise
    noise = np.random.randn(n_maturities) * 0.05

    # Combine all factors
    daily_yields = base_curve + level_shift + slope_shift + curvature_shift + noise

    # Ensure yields are positive
    daily_yields = np.maximum(daily_yields, 0.01)

    yield_data.append(daily_yields)

# Create DataFrame
df = pd.DataFrame(yield_data, columns=maturities)
df.insert(0, 'Date', dates)

# Save to CSV
output_path = '/home/user/pca_spotrates/python-webapp/demo_data/sample_yield_curve.csv'
df.to_csv(output_path, index=False)

print(f"✅ Created demo data: {output_path}")
print(f"📊 Date range: {dates[0].strftime('%Y-%m-%d')} to {dates[-1].strftime('%Y-%m-%d')}")
print(f"📈 Observations: {len(df)}")
print(f"📉 Maturities: {len(maturities)}")
print(f"\nSample data (first 5 rows):")
print(df.head())
print(f"\nYield statistics:")
print(df[maturities].describe())
