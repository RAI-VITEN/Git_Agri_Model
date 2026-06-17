"""
Predictor module
Uses trained TensorFlow model to make crop suitability predictions
"""

import numpy as np
import pickle
import tensorflow as tf
from typing import Dict, Tuple
import os

MODEL_PATH = "models/crop_model.h5"
SCALER_PATH = "models/scaler.pkl"


class CropPredictor:
    """Predict crop suitability based on meteorological data"""

    def __init__(self):
        """Initialize predictor with trained model and scaler"""
        self.model = None
        self.scaler = None
        self.load_model()

    def load_model(self):
        """Load trained model and scaler"""
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {MODEL_PATH}. Run: python models/train_model.py")

        if not os.path.exists(SCALER_PATH):
            raise FileNotFoundError(f"Scaler not found at {SCALER_PATH}. Run: python models/train_model.py")

        self.model = tf.keras.models.load_model(MODEL_PATH)
        with open(SCALER_PATH, "rb") as f:
            self.scaler = pickle.load(f)

        print("✓ Model and scaler loaded successfully")

    def predict(
        self,
        rainfall: float,
        temperature: float,
        soil_moisture: float = 50,
        humidity: float = 70,
    ) -> Dict[str, float]:
        """
        Predict crop suitability

        Args:
            rainfall: Rainfall in mm
            temperature: Temperature in °C
            soil_moisture: Soil moisture percentage (default: 50)
            humidity: Humidity percentage (default: 70)

        Returns:
            Dictionary with predictions for maize and beans
        """
        # Create feature vector
        features = np.array(
            [
                rainfall,
                temperature,
                soil_moisture,
                humidity,
                rainfall / (temperature + 1),  # rainfall_temp_ratio
                soil_moisture * humidity / 100,  # moisture_index
            ]
        )

        # Normalize features
        features_scaled = self.scaler.transform([features])

        # Make prediction
        prediction = self.model.predict(features_scaled, verbose=0)[0]

        return {
            "maize_suitability": float(prediction[0]),
            "beans_suitability": float(prediction[1]),
        }

    def batch_predict(self, data_list: list) -> list:
        """
        Predict for multiple data points

        Args:
            data_list: List of dictionaries with rainfall, temperature, etc.

        Returns:
            List of predictions
        """
        predictions = []
        for data in data_list:
            pred = self.predict(
                rainfall=data.get("rainfall", 0),
                temperature=data.get("temperature", 20),
                soil_moisture=data.get("soil_moisture", 50),
                humidity=data.get("humidity", 70),
            )
            predictions.append(pred)
        return predictions


if __name__ == "__main__":
    # Example usage
    try:
        predictor = CropPredictor()

        # Test prediction
        print("\n🌾 Testing predictions:")
        result = predictor.predict(
            rainfall=800, temperature=22, soil_moisture=60, humidity=75
        )
        print(f"  Rainfall: 800mm, Temperature: 22°C")
        print(f"  Maize Suitability: {result['maize_suitability']:.3f}")
        print(f"  Beans Suitability: {result['beans_suitability']:.3f}")

    except FileNotFoundError as e:
        print(f"✗ {str(e)}")
