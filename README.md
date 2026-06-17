# Git_Agri_Model

An interactive agricultural dashboard that provides crop suitability predictions and planting recommendations based on meteorological data from netCDF4 files.

## Features

- **Upload netCDF4 files** with rainfall and temperature data
- **Interactive map** displaying Kenya constituencies
- **Data visualization** of meteorological variables
- **AI-powered predictions** using TensorFlow for crop suitability
- **Planting recommendations** for maize and beans
- **Real-time analysis** based on geographic selection

## Tech Stack

- **Backend:** Flask
- **Data Processing:** xarray, geopandas, shapely
- **Geospatial:** cartopy
- **Machine Learning:** TensorFlow
- **Visualization:** matplotlib, plotly
- **Frontend:** HTML5, CSS3, JavaScript

## Project Structure

```
Git_Agri_Model/
├── app.py                      # Flask application
├── requirements.txt            # Python dependencies
├── data/
│   ├── synthetic_data.py       # Generate synthetic training data
│   ├── training_data.csv       # Synthetic dataset
│   └── kenya_constituencies.geojson  # Geographic boundaries
├── models/
│   ├── train_model.py          # TensorFlow model training
│   └── crop_model.h5           # Trained model
├── templates/
│   └── index.html              # Dashboard UI
├── static/
│   ├── css/
│   │   └── style.css           # Styling
│   └── js/
│       └── dashboard.js        # Frontend logic
└── utils/
    ├── data_processor.py       # netCDF4 parsing & processing
    ├── predictor.py            # Prediction logic
    └── recommendations.py      # Generate planting recommendations
```

## Installation

```bash
# Clone the repository
git clone https://github.com/RAI-VITEN/Git_Agri_Model.git
cd Git_Agri_Model

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Generate synthetic data and train model
python data/synthetic_data.py
python models/train_model.py

# Run the Flask app
python app.py
```

Navigate to `http://localhost:5000` in your browser.

## Usage

1. **Upload netCDF4 file** - Select a .nc file with rainfall and temperature data
2. **Select constituency** - Choose an area from the interactive map
3. **View analysis** - See parsed data and visualizations
4. **Get predictions** - AI model predicts crop suitability
5. **Read recommendations** - Get planting advice for maize and beans

## Data Format

The netCDF4 file should contain:
- `rainfall` variable (mm or mm/day)
- `temperature` variable (°C)
- Geographic coordinates (latitude, longitude)

## Model

The TensorFlow model predicts:
- Crop suitability score (0-1) for maize and beans
- Optimal planting dates based on weather patterns

## License

MIT License

## Author

RAI-VITEN
