"""
TensorFlow model training script
Trains a neural network to predict crop suitability and planting dates
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import pickle
import os

# Configuration
MODEL_PATH = "models/crop_model.h5"
SCALER_PATH = "models/scaler.pkl"
TRAINING_DATA = "data/training_data.csv"


def prepare_features(df):
    """Prepare features for model training"""
    features = df[
        [
            "rainfall",
            "temperature",
            "soil_moisture",
            "humidity",
        ]
    ].fillna(0)

    # Create additional features
    df_copy = df.copy()
    df_copy["rainfall_temp_ratio"] = (
        df_copy["rainfall"] / (df_copy["temperature"] + 1)
    )
    df_copy["moisture_index"] = df_copy["soil_moisture"] * df_copy["humidity"] / 100

    features["rainfall_temp_ratio"] = df_copy["rainfall_temp_ratio"]
    features["moisture_index"] = df_copy["moisture_index"]

    return features


def prepare_labels(df):
    """Prepare labels for model training"""
    return df[["maize_suitability", "beans_suitability"]].fillna(0)


def build_model(input_dim):
    """Build TensorFlow neural network model"""
    model = keras.Sequential(
        [
            keras.layers.Input(shape=(input_dim,)),
            keras.layers.Dense(128, activation="relu"),
            keras.layers.BatchNormalization(),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(64, activation="relu"),
            keras.layers.BatchNormalization(),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(32, activation="relu"),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(16, activation="relu"),
            keras.layers.Dense(2, activation="sigmoid"),  # Output: maize, beans suitability
        ]
    )

    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss="mse",
        metrics=["mae"],
    )

    return model


def train_model():
    """Train the crop suitability model"""
    print("🌾 Training Crop Suitability Model\n")

    # Load data
    if not os.path.exists(TRAINING_DATA):
        print(f"✗ Training data not found at {TRAINING_DATA}")
        print("  Run: python data/synthetic_data.py")
        return False

    print(f"Loading training data from {TRAINING_DATA}...")
    df = pd.read_csv(TRAINING_DATA)
    print(f"✓ Loaded {len(df)} samples\n")

    # Prepare features and labels
    print("Preparing features and labels...")
    X = prepare_features(df)
    y = prepare_labels(df)
    print(f"✓ Features shape: {X.shape}")
    print(f"✓ Labels shape: {y.shape}\n")

    # Normalize features
    print("Normalizing features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    print("✓ Features normalized\n")

    # Split data
    print("Splitting data (80/20 train/test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    print(f"✓ Training samples: {len(X_train)}")
    print(f"✓ Testing samples: {len(X_test)}\n")

    # Build model
    print("Building neural network...")
    model = build_model(X_train.shape[1])
    print(model.summary())
    print()

    # Train model
    print("Training model...")
    history = model.fit(
        X_train,
        y_train,
        epochs=100,
        batch_size=32,
        validation_split=0.2,
        verbose=1,
    )

    # Evaluate model
    print("\nEvaluating model on test set...")
    test_loss, test_mae = model.evaluate(X_test, y_test, verbose=0)
    print(f"✓ Test Loss: {test_loss:.4f}")
    print(f"✓ Test MAE: {test_mae:.4f}\n")

    # Make predictions
    y_pred = model.predict(X_test, verbose=0)
    print("Sample predictions (first 5):")
    for i in range(min(5, len(y_pred))):
        print(
            f"  Maize: {y_pred[i][0]:.3f} (actual: {y_test.iloc[i, 0]:.3f}) | Beans: {y_pred[i][1]:.3f} (actual: {y_test.iloc[i, 1]:.3f})"
        )

    # Save model and scaler
    print(f"\nSaving model to {MODEL_PATH}...")
    os.makedirs("models", exist_ok=True)
    model.save(MODEL_PATH)
    print("✓ Model saved")

    print(f"Saving scaler to {SCALER_PATH}...")
    with open(SCALER_PATH, "wb") as f:
        pickle.dump(scaler, f)
    print("✓ Scaler saved")

    print("\n✅ Training complete!")
    return True


if __name__ == "__main__":
    train_model()
