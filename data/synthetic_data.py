"""
Synthetic Data Generator for Agricultural Dashboard
Generates realistic meteorological and crop data for training the TensorFlow model
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json

# Set random seed for reproducibility
np.random.seed(42)

# Kenya constituencies (sample of major ones)
CONSTITUENCIES = {
    "Nyeri Central": {"lat": -0.42, "lon": 36.95, "id": 1},
    "Kiambaa": {"lat": -0.36, "lon": 36.82, "id": 2},
    "Mukurweini": {"lat": -0.64, "lon": 36.93, "id": 3},
    "Nairobi Central": {"lat": -1.29, "lon": 36.81, "id": 4},
    "Kasarani": {"lat": -1.21, "lon": 36.90, "id": 5},
    "Makadara": {"lat": -1.32, "lon": 36.87, "id": 6},
    "Kajiado Central": {"lat": -2.00, "lon": 36.77, "id": 7},
    "Kajiado East": {"lat": -2.10, "lon": 36.98, "id": 8},
    "Nakuru Town East": {"lat": -0.35, "lon": 36.06, "id": 9},
    "Nakuru Town West": {"lat": -0.37, "lon": 36.04, "id": 10},
    "Kericho": {"lat": -0.36, "lon": 35.28, "id": 11},
    "Kisii Central": {"lat": -0.68, "lon": 34.78, "id": 12},
    "Homabay": {"lat": -0.53, "lon": 34.46, "id": 13},
    "Kisumu Central": {"lat": -0.10, "lon": 34.76, "id": 14},
    "Eldoret East": {"lat": 0.52, "lon": 35.27, "id": 15},
}

# Crop characteristics (rainfall mm, temperature °C ranges)
CROP_REQUIREMENTS = {
    "maize": {
        "rainfall_min": 500,
        "rainfall_max": 1200,
        "rainfall_optimal": 850,
        "temp_min": 15,
        "temp_max": 32,
        "temp_optimal": 24,
        "growing_days": 120,
    },
    "beans": {
        "rainfall_min": 400,
        "rainfall_max": 1000,
        "rainfall_optimal": 700,
        "temp_min": 16,
        "temp_max": 28,
        "temp_optimal": 22,
        "growing_days": 90,
    },
}


def generate_meteorological_data(n_samples=1000):
    """Generate synthetic meteorological data"""
    data = []

    for _ in range(n_samples):
        # Random constituency
        constituency = np.random.choice(list(CONSTITUENCIES.keys()))
        const_info = CONSTITUENCIES[constituency]

        # Seasonal variation (simulate monthly patterns)
        month = np.random.randint(1, 13)
        year = np.random.randint(2020, 2025)

        # Temperature (seasonal variation)
        base_temp = 20 + 8 * np.sin(2 * np.pi * month / 12)
        temperature = base_temp + np.random.normal(0, 2)

        # Rainfall (bimodal distribution in Kenya - March-May, October-December)
        if month in [3, 4, 5, 10, 11, 12]:
            base_rainfall = np.random.normal(100, 30)
        else:
            base_rainfall = np.random.normal(40, 15)
        rainfall = max(0, base_rainfall + np.random.normal(0, 20))

        # Soil moisture (correlated with rainfall)
        soil_moisture = min(100, (rainfall / 100) * 50 + np.random.normal(0, 5))

        data.append(
            {
                "constituency": constituency,
                "latitude": const_info["lat"],
                "longitude": const_info["lon"],
                "date": datetime(year, month, 1) + timedelta(days=np.random.randint(0, 28)),
                "rainfall": round(rainfall, 2),
                "temperature": round(temperature, 2),
                "soil_moisture": round(max(0, soil_moisture), 2),
                "humidity": round(np.random.uniform(40, 95), 2),
            }
        )

    return pd.DataFrame(data)


def calculate_crop_suitability(row, crop):
    """Calculate crop suitability score (0-1) based on conditions"""
    reqs = CROP_REQUIREMENTS[crop]

    # Rainfall suitability
    if reqs["rainfall_min"] <= row["rainfall"] <= reqs["rainfall_max"]:
        rainfall_score = 1.0
    elif row["rainfall"] < reqs["rainfall_min"]:
        rainfall_score = row["rainfall"] / reqs["rainfall_min"]
    else:
        rainfall_score = (reqs["rainfall_max"] - row["rainfall"]) / (
            reqs["rainfall_max"] - reqs["rainfall_min"]
        )
    rainfall_score = max(0, min(1, rainfall_score))

    # Temperature suitability
    if reqs["temp_min"] <= row["temperature"] <= reqs["temp_max"]:
        temp_score = 1.0
    elif row["temperature"] < reqs["temp_min"]:
        temp_score = row["temperature"] / reqs["temp_min"]
    else:
        temp_score = (reqs["temp_max"] - row["temperature"]) / (
            reqs["temp_max"] - reqs["temp_min"]
        )
    temp_score = max(0, min(1, temp_score))

    # Soil moisture impact
    soil_score = min(1, row["soil_moisture"] / 60)

    # Combined suitability (weighted average)
    suitability = (rainfall_score * 0.4 + temp_score * 0.4 + soil_score * 0.2)
    return round(suitability, 3)


def determine_planting_date(row, crop):
    """Determine optimal planting date based on conditions"""
    # Simple heuristic: plant during rainy season when conditions are favorable
    month = row["date"].month
    suitability = calculate_crop_suitability(row, crop)

    if suitability > 0.7:
        # Favorable conditions
        return "Optimal - Plant immediately"
    elif suitability > 0.5:
        return "Favorable - Plant within 1-2 weeks"
    elif month in [2, 3, 4, 9, 10, 11]:
        return "Wait for rain - Expected soon"
    else:
        return "Not recommended - Wait for next season"


def generate_training_dataset(n_samples=1000):
    """Generate complete training dataset with labels"""
    met_data = generate_meteorological_data(n_samples)

    # Add crop suitability scores
    met_data["maize_suitability"] = met_data.apply(
        lambda row: calculate_crop_suitability(row, "maize"), axis=1
    )
    met_data["beans_suitability"] = met_data.apply(
        lambda row: calculate_crop_suitability(row, "beans"), axis=1
    )

    # Add planting recommendations
    met_data["maize_planting_date"] = met_data.apply(
        lambda row: determine_planting_date(row, "maize"), axis=1
    )
    met_data["beans_planting_date"] = met_data.apply(
        lambda row: determine_planting_date(row, "beans"), axis=1
    )

    return met_data


def save_training_data(df, filepath="data/training_data.csv"):
    """Save training data to CSV"""
    df.to_csv(filepath, index=False)
    print(f"✓ Training data saved to {filepath}")
    print(f"  Total samples: {len(df)}")
    print(f"  Columns: {list(df.columns)}")


def generate_sample_netcdf_data(filepath="data/sample_meteorological.nc"):
    """Generate a sample netCDF file for testing"""
    try:
        import xarray as xr

        # Create sample data for a single constituency
        lat = np.linspace(-1.25, -1.30, 10)
        lon = np.linspace(36.80, 36.90, 10)
        time = pd.date_range("2024-01-01", periods=30, freq="D")

        # Create data variables
        rainfall = np.random.uniform(0, 100, size=(len(time), len(lat), len(lon)))
        temperature = np.random.uniform(18, 26, size=(len(time), len(lat), len(lon)))

        # Create xarray Dataset
        ds = xr.Dataset(
            {
                "rainfall": (["time", "latitude", "longitude"], rainfall),
                "temperature": (["time", "latitude", "longitude"], temperature),
            },
            coords={
                "time": time,
                "latitude": lat,
                "longitude": lon,
            },
        )

        ds.to_netcdf(filepath)
        print(f"✓ Sample netCDF file saved to {filepath}")
    except ImportError:
        print("⚠ xarray not installed. Skipping sample netCDF generation.")


if __name__ == "__main__":
    print("🌾 Generating synthetic agricultural dataset...\n")

    # Generate training data
    training_data = generate_training_dataset(n_samples=1000)

    # Save to CSV
    save_training_data(training_data)

    # Generate sample netCDF file
    generate_sample_netcdf_data()

    print("\n✓ Dataset generation complete!")
    print("\nSample data:")
    print(training_data.head())
