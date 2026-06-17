# 🌾 Agricultural Dashboard - Setup & Getting Started Guide

## Project Overview

The **Agricultural Dashboard** is an intelligent crop suitability prediction system that uses machine learning to recommend optimal planting times and crop choices for Kenyan farmers. It integrates meteorological data (netCDF4 format) with a TensorFlow neural network to provide real-time, data-driven agricultural advice.

### Key Features

- 📊 **Interactive Dashboard**: Web-based interface for easy data visualization
- 🤖 **AI Predictions**: TensorFlow-powered crop suitability scoring
- 📍 **Geographic Integration**: Leaflet maps with Kenya constituencies
- 📤 **netCDF4 Support**: Direct integration with meteorological data files
- 💾 **Persistent Recommendations**: Detailed planting guidance with crop requirements
- 📈 **Data Visualization**: Charts and analytics for weather patterns

---

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/RAI-VITEN/Git_Agri_Model.git
cd Git_Agri_Model
```

### Step 2: Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Generate Training Data

```bash
python data/synthetic_data.py
```

This will create:
- `data/training_data.csv` - 1000 synthetic training samples
- `data/sample_meteorological.nc` - Sample netCDF4 file for testing

### Step 5: Train the Model

```bash
python models/train_model.py
```

This trains the TensorFlow neural network and saves:
- `models/crop_model.h5` - Trained model weights
- `models/scaler.pkl` - Feature scaler for predictions

**⏱️ Expected time: 2-5 minutes**

---

## Running the Application

### Start the Flask Server

```bash
python app.py
```

Expected output:
```
🌾 Agricultural Dashboard Server
================================

Starting Flask application...

📊 Dashboard available at: http://localhost:5000
📡 API documentation:
   GET  /api/health           - Health check
   GET  /api/constituencies   - List Kenya constituencies
   POST /api/upload           - Upload and parse netCDF file
   POST /api/predict          - Make crop predictions
```

### Access the Dashboard

Open your web browser and navigate to:
```
http://localhost:5000
```

---

## Usage Guide

### Workflow: Step-by-Step

#### Step 1: Upload Meteorological Data 📁
1. Prepare a netCDF4 (.nc) file containing:
   - `rainfall` variable (in mm)
   - `temperature` variable (in °C)
2. Click the upload area or drag-and-drop your file
3. File will be validated for format and required variables

#### Step 2: Select Area & Parse Data 📍
1. **Method A**: Click on the interactive map to select a location
2. **Method B**: Use the dropdown to select a Kenyan constituency
3. Click "Parse Data" button
4. The system will extract meteorological data for your selected location

#### Step 3: View Data Visualization 📊
- Rainfall statistics (min, max, mean, std)
- Temperature statistics
- Soil moisture and humidity estimates
- Interactive weather charts using Plotly

#### Step 4: AI Predictions 🤖
- The system automatically generates crop suitability scores:
  - **Maize (Corn)**: Scored 0-1 based on optimal conditions
  - **Beans**: Scored 0-1 based on optimal conditions
- Scores indicate planting suitability:
  - **0.8-1.0**: Highly Recommended ✅
  - **0.6-0.8**: Recommended ✔️
  - **0.4-0.6**: Marginal ⚠️
  - **0.0-0.4**: Not Recommended ❌

#### Step 5: Get Recommendations ✅
- Detailed planting guidance for each crop
- Growing period and seed requirements
- Spacing and rainfall needs
- Actionable advisor summary

---

## API Reference

### Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "ok",
  "predictor_ready": true,
  "message": "Agricultural Dashboard API"
}
```

---

### Get Constituencies
```http
GET /api/constituencies
```

**Response:** GeoJSON FeatureCollection with Kenya constituencies

---

### Upload & Parse netCDF
```http
POST /api/upload
Content-Type: multipart/form-data

file: <netCDF4 file>
latitude: -1.29
longitude: 36.81
```

**Response:**
```json
{
  "success": true,
  "data": {
    "latitude": -1.29,
    "longitude": 36.81,
    "rainfall": {
      "min": 0.5,
      "max": 150.2,
      "mean": 75.3,
      "std": 35.8
    },
    "temperature": {
      "min": 15.2,
      "max": 28.5,
      "mean": 22.1,
      "std": 3.2
    }
  }
}
```

---

### Make Predictions
```http
POST /api/predict
Content-Type: application/json

{
  "rainfall": 800,
  "temperature": 22,
  "soil_moisture": 50,
  "humidity": 70
}
```

**Response:**
```json
{
  "success": true,
  "predictions": {
    "maize_suitability": 0.856,
    "beans_suitability": 0.642
  },
  "recommendations": [
    {
      "crop": "maize",
      "crop_name": "Maize (Corn)",
      "suitability_score": 0.856,
      "recommendation": "HIGHLY RECOMMENDED",
      "action": "Plant immediately",
      "icon": "✅",
      "reasoning": [
        "Rainfall conditions are favorable",
        "Temperature conditions are optimal"
      ],
      "crop_details": {
        "growing_period": "120 days",
        "spacing": "75cm x 25cm",
        "seed_rate": "25kg/hectare",
        "rainfall_needed": "500-1200mm",
        "temperature_range": "15-32°C"
      }
    }
  ],
  "advisory": "🌾 PLANTING ADVISORY SUMMARY\n..."
}
```

---

## Project Structure

```
Git_Agri_Model/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
├── README.md                       # Project documentation
│
├── models/
│   ├── train_model.py             # TensorFlow model training script
│   ├── crop_model.h5              # Trained model (generated after training)
│   └── scaler.pkl                 # Feature scaler (generated after training)
│
├── data/
│   ├── synthetic_data.py          # Data generation script
│   ├── training_data.csv          # Training dataset (generated)
│   ├── sample_meteorological.nc   # Sample netCDF file (generated)
│   └── kenya_constituencies.geojson  # Kenya geographic data
│
├── utils/
│   ├── predictor.py               # Crop prediction module
│   ├── recommendations.py         # Recommendation generation
│   ├── data_processor.py          # netCDF4 data processing
│   └── __init__.py
│
├── templates/
│   └── index.html                 # HTML dashboard template
│
└── static/
    ├── css/
    │   └── style.css              # Dashboard styling
    └── js/
        └── dashboard.js           # Frontend JavaScript logic
```

---

## Model Architecture

### Neural Network Layers

```
Input Layer (6 features)
    ↓
Dense(128, ReLU) + BatchNorm + Dropout(0.3)
    ↓
Dense(64, ReLU) + BatchNorm + Dropout(0.3)
    ↓
Dense(32, ReLU) + Dropout(0.2)
    ↓
Dense(16, ReLU)
    ↓
Output Layer (2 neurons, Sigmoid)
    ↓
[Maize Suitability, Beans Suitability]
```

### Input Features

1. **Rainfall** (mm)
2. **Temperature** (°C)
3. **Soil Moisture** (%)
4. **Humidity** (%)
5. **Rainfall-Temperature Ratio** (derived)
6. **Moisture Index** (derived)

### Training Configuration

- **Optimizer**: Adam (learning_rate=0.001)
- **Loss Function**: Mean Squared Error (MSE)
- **Epochs**: 100
- **Batch Size**: 32
- **Validation Split**: 20%
- **Test Split**: 20%

---

## Crop Requirements

### Maize (Corn)
- **Rainfall**: 500-1200 mm
- **Temperature**: 15-32°C (optimal: 24°C)
- **Growing Period**: 120 days
- **Spacing**: 75cm × 25cm
- **Seed Rate**: 25 kg/hectare

### Beans
- **Rainfall**: 400-1000 mm
- **Temperature**: 16-28°C (optimal: 22°C)
- **Growing Period**: 90 days
- **Spacing**: 45cm × 15cm
- **Seed Rate**: 60 kg/hectare

---

## Troubleshooting

### Issue: Model Not Found
**Error**: `FileNotFoundError: Model not found at models/crop_model.h5`

**Solution**: Train the model first
```bash
python data/synthetic_data.py
python models/train_model.py
```

---

### Issue: Port Already in Use
**Error**: `OSError: [Errno 48] Address already in use`

**Solution**: Use a different port
```bash
# Modify app.py or run with:
python app.py --port 5001
```

---

### Issue: File Upload Fails
**Error**: `File must be .nc (netCDF4) format`

**Solution**: Ensure your file:
- Has `.nc` extension
- Contains `rainfall` and `temperature` variables
- Is valid netCDF4 format

---

### Issue: Import Errors
**Error**: `ModuleNotFoundError: No module named 'tensorflow'`

**Solution**: Reinstall dependencies
```bash
pip install --upgrade -r requirements.txt
```

---

## Development & Contributions

### Running Tests
```bash
pytest tests/
```

### Code Style
```bash
# Format code with black
black .

# Check style with flake8
flake8 .
```

### Adding New Crops

1. Update `CROP_REQUIREMENTS` in `data/synthetic_data.py`
2. Update `CROP_INFO` in `utils/recommendations.py`
3. Retrain the model with new data

---

## Performance Considerations

- **Model Training**: ~2-5 minutes on standard CPU
- **Prediction Time**: <100ms per request
- **File Upload**: Supports files up to 50MB
- **Concurrent Users**: Flask development server supports ~10-20 users

For production deployment, use Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## Deployment

### Docker (Optional)

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

Build and run:
```bash
docker build -t agri-dashboard .
docker run -p 5000:5000 agri-dashboard
```

---

## License

This project is open source and available under the MIT License.

---

## Support & Contact

For issues, feature requests, or contributions:
- Open an issue on GitHub
- Contact: [Your Contact Info]

---

## References

- **TensorFlow Documentation**: https://www.tensorflow.org/
- **Flask Documentation**: https://flask.palletsprojects.com/
- **netCDF4 Format**: https://www.unidata.ucar.edu/software/netcdf/
- **Leaflet Maps**: https://leafletjs.com/
- **Kenya GIS Data**: https://data.humdata.org/

---

**Last Updated**: June 2026  
**Version**: 1.0.0

Happy farming! 🌾🚀
