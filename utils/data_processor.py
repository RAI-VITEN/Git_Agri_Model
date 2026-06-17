"""
Data Processor for netCDF4 files
Handles parsing, validation, and extraction of meteorological data
"""

import xarray as xr
import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional


class NetCDFProcessor:
    """Process and validate netCDF4 meteorological files"""

    def __init__(self, filepath: str):
        """
        Initialize processor with netCDF file

        Args:
            filepath: Path to .nc file
        """
        self.filepath = filepath
        self.dataset = None
        self.parsed_data = None

    def load_file(self) -> bool:
        """Load and validate netCDF file"""
        try:
            self.dataset = xr.open_dataset(self.filepath)
            print(f"✓ Loaded netCDF file: {self.filepath}")
            return True
        except Exception as e:
            print(f"✗ Error loading file: {str(e)}")
            return False

    def validate_variables(self) -> bool:
        """Check if required variables exist"""
        required_vars = ["rainfall", "temperature"]
        available_vars = list(self.dataset.data_vars)

        missing = [v for v in required_vars if v not in available_vars]
        if missing:
            print(f"✗ Missing variables: {missing}")
            return False

        print(f"✓ Required variables found: {required_vars}")
        return True

    def get_spatial_bounds(self) -> Dict:
        """Extract spatial bounds from dataset"""
        coords = self.dataset.coords

        # Handle different coordinate naming conventions
        lat_names = ["latitude", "lat", "y"]
        lon_names = ["longitude", "lon", "x"]

        lat_var = next((n for n in lat_names if n in coords), None)
        lon_var = next((n for n in lon_names if n in coords), None)

        if not lat_var or not lon_var:
            return None

        lat = self.dataset[lat_var].values
        lon = self.dataset[lon_var].values

        return {
            "lat_min": float(np.min(lat)),
            "lat_max": float(np.max(lat)),
            "lon_min": float(np.min(lon)),
            "lon_max": float(np.max(lon)),
            "lat_var": lat_var,
            "lon_var": lon_var,
        }

    def extract_point_data(
        self, latitude: float, longitude: float
    ) -> Optional[Dict]:
        """
        Extract data for a specific point

        Args:
            latitude: Point latitude
            longitude: Point longitude

        Returns:
            Dictionary with extracted data or None if point out of bounds
        """
        try:
            bounds = self.get_spatial_bounds()
            if not bounds:
                return None

            # Select nearest point
            point_data = self.dataset.sel(
                {bounds["lat_var"]: latitude, bounds["lon_var"]: longitude},
                method="nearest",
            )

            rainfall = point_data["rainfall"].values
            temperature = point_data["temperature"].values

            return {
                "latitude": latitude,
                "longitude": longitude,
                "rainfall": self._process_array(rainfall),
                "temperature": self._process_array(temperature),
            }
        except Exception as e:
            print(f"✗ Error extracting point data: {str(e)}")
            return None

    def _process_array(self, arr: np.ndarray) -> Dict:
        """
        Process array to get statistics

        Args:
            arr: Input array

        Returns:
            Dictionary with min, max, mean, std
        """
        arr_flat = arr.flatten()
        arr_flat = arr_flat[~np.isnan(arr_flat)]

        return {
            "min": float(np.min(arr_flat)) if len(arr_flat) > 0 else None,
            "max": float(np.max(arr_flat)) if len(arr_flat) > 0 else None,
            "mean": float(np.mean(arr_flat)) if len(arr_flat) > 0 else None,
            "std": float(np.std(arr_flat)) if len(arr_flat) > 0 else None,
        }

    def get_summary_statistics(self) -> Dict:
        """Get summary statistics for all variables"""
        summary = {}

        for var_name in ["rainfall", "temperature"]:
            if var_name in self.dataset.data_vars:
                data = self.dataset[var_name].values
                summary[var_name] = self._process_array(data)

        return summary

    def close(self):
        """Close the dataset"""
        if self.dataset:
            self.dataset.close()

    def __enter__(self):
        self.load_file()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def parse_netcdf_for_region(
    filepath: str, latitude: float, longitude: float
) -> Optional[Dict]:
    """
    Convenience function to parse netCDF for a specific region

    Args:
        filepath: Path to .nc file
        latitude: Region latitude
        longitude: Region longitude

    Returns:
        Parsed data dictionary
    """
    with NetCDFProcessor(filepath) as processor:
        if not processor.load_file():
            return None

        if not processor.validate_variables():
            return None

        return processor.extract_point_data(latitude, longitude)


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        with NetCDFProcessor(filepath) as processor:
            if processor.load_file() and processor.validate_variables():
                print("\n📊 Data Summary:")
                print(processor.get_summary_statistics())
    else:
        print("Usage: python data_processor.py <path_to_netcdf_file>")
