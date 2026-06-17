"""
Flask Agricultural Dashboard Application
Main application server for the crop suitability and planting recommendation system
"""

import os
import json
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import tempfile
import traceback

from utils.data_processor import NetCDFProcessor
from utils.predictor import CropPredictor
from utils.recommendations import generate_recommendations, get_advisory_summary

# Flask configuration
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

# Load Kenya constituencies
CONSTITUENCIES_FILE = "data/kenya_constituencies.geojson"
with open(CONSTITUENCIES_FILE, 'r') as f:
    CONSTITUENCIES_DATA = json.load(f)

# Initialize predictor
try:
    predictor = CropPredictor()
    PREDICTOR_READY = True
except Exception as e:
    print(f"⚠ Warning: Predictor not ready. Run: python models/train_model.py")
    print(f"  Error: {str(e)}")
    PREDICTOR_READY = False


@app.route('/')
def index():
    """Render main dashboard"""
    return render_template('index.html')


@app.route('/api/constituencies')
def get_constituencies():
    """API endpoint to get Kenya constituencies"""
    return jsonify(CONSTITUENCIES_DATA)


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Handle netCDF file upload and data extraction
    
    Expected request:
    - file: netCDF4 file
    - latitude: float
    - longitude: float
    """
    try:
        # Validate request
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file.filename.endswith('.nc'):
            return jsonify({'error': 'File must be .nc (netCDF4) format'}), 400

        # Get coordinates
        latitude = request.form.get('latitude', type=float)
        longitude = request.form.get('longitude', type=float)

        if latitude is None or longitude is None:
            return jsonify({'error': 'Latitude and longitude required'}), 400

        # Save temporary file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process netCDF file
        with NetCDFProcessor(filepath) as processor:
            if not processor.load_file():
                return jsonify({'error': 'Failed to load netCDF file'}), 400

            if not processor.validate_variables():
                return jsonify({'error': 'File missing required variables (rainfall, temperature)'}), 400

            # Extract data for selected point
            point_data = processor.extract_point_data(latitude, longitude)
            if not point_data:
                return jsonify({'error': 'Failed to extract data for selected location'}), 400

        # Clean up temporary file
        os.remove(filepath)

        return jsonify({
            'success': True,
            'data': point_data
        })

    except Exception as e:
        print(f"✗ Upload error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Make crop suitability predictions
    
    Expected request JSON:
    {
        "rainfall": float,
        "temperature": float,
        "soil_moisture": float (optional),
        "humidity": float (optional)
    }
    """
    try:
        if not PREDICTOR_READY:
            return jsonify({'error': 'Predictor model not loaded. Run: python models/train_model.py'}), 503

        data = request.get_json()

        # Validate input
        if not data or 'rainfall' not in data or 'temperature' not in data:
            return jsonify({'error': 'rainfall and temperature required'}), 400

        rainfall = float(data['rainfall'])
        temperature = float(data['temperature'])
        soil_moisture = float(data.get('soil_moisture', 50))
        humidity = float(data.get('humidity', 70))

        # Make prediction
        predictions = predictor.predict(
            rainfall=rainfall,
            temperature=temperature,
            soil_moisture=soil_moisture,
            humidity=humidity
        )

        # Generate recommendations
        recommendations = generate_recommendations(
            predictions,
            rainfall,
            temperature
        )

        return jsonify({
            'success': True,
            'predictions': predictions,
            'recommendations': recommendations,
            'advisory': get_advisory_summary(predictions, rainfall, temperature)
        })

    except ValueError as e:
        return jsonify({'error': f'Invalid input: {str(e)}'}), 400
    except Exception as e:
        print(f"✗ Prediction error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}'}), 500


@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'predictor_ready': PREDICTOR_READY,
        'message': 'Agricultural Dashboard API'
    })


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("""
    🌾 Agricultural Dashboard Server
    ================================
    
    Starting Flask application...
    """)

    if not PREDICTOR_READY:
        print("⚠ WARNING: Predictor model not ready")
        print("  To train the model, run:")
        print("    python data/synthetic_data.py")
        print("    python models/train_model.py")
        print()

    print("📊 Dashboard available at: http://localhost:5000")
    print("📡 API documentation:")
    print("   GET  /api/health           - Health check")
    print("   GET  /api/constituencies   - List Kenya constituencies")
    print("   POST /api/upload           - Upload and parse netCDF file")
    print("   POST /api/predict          - Make crop predictions")
    print()

    app.run(debug=True, host='0.0.0.0', port=5000)
