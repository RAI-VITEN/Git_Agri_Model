/**
 * Agricultural Dashboard JavaScript
 * Handles frontend logic for file upload, map interaction, and API calls
 */

// Global variables
let map;
let currentData = null;
let selectedLocation = null;
let constituencies = [];

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeMap();
    loadConstituencies();
    setupFileUpload();
    setupEventListeners();
});

/**
 * Initialize Leaflet map
 */
function initializeMap() {
    map = L.map('map').setView([-1.3, 36.8], 7);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(map);

    // Add click handler
    map.on('click', function(e) {
        selectLocation(e.latlng.lat, e.latlng.lng);
    });
}

/**
 * Load constituencies from API
 */
async function loadConstituencies() {
    try {
        const response = await fetch('/api/constituencies');
        const data = await response.json();
        
        constituencies = data.features;
        
        // Populate dropdown
        const select = document.getElementById('constituencies');
        constituencies.forEach((feature, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = feature.properties.name;
            select.appendChild(option);
        });

        // Add markers to map
        constituencies.forEach(feature => {
            const coords = feature.geometry.coordinates;
            L.circleMarker([coords[1], coords[0]], {
                radius: 6,
                fillColor: '#2ecc71',
                color: '#fff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.8
            }).bindPopup(feature.properties.name).addTo(map);
        });

        select.addEventListener('change', function(e) {
            if (e.target.value) {
                const feature = constituencies[e.target.value];
                const coords = feature.geometry.coordinates;
                selectLocation(coords[1], coords[0], feature.properties.name);
                map.setView([coords[1], coords[0]], 10);
            }
        });
    } catch (error) {
        showMessage('Error loading constituencies', 'error');
    }
}

/**
 * Select a location on the map
 */
function selectLocation(lat, lng, name = null) {
    selectedLocation = { lat, lng, name };
    document.getElementById('parseBtn').disabled = false;
    
    // Clear previous marker
    map.eachLayer(layer => {
        if (layer instanceof L.Marker) {
            map.removeLayer(layer);
        }
    });

    // Add selected marker
    L.marker([lat, lng], {
        icon: L.icon({
            iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
            shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41]
        })
    }).bindPopup(name || `${lat.toFixed(2)}, ${lng.toFixed(2)}`).addTo(map);
}

/**
 * Setup file upload
 */
function setupFileUpload() {
    const fileInput = document.getElementById('ncFile');
    const fileLabel = document.querySelector('.file-label');

    // Click to select
    fileLabel.addEventListener('click', () => fileInput.click());

    // Drag and drop
    fileLabel.addEventListener('dragover', (e) => {
        e.preventDefault();
        fileLabel.style.background = '#f0fdf4';
        fileLabel.style.borderColor = '#27ae60';
    });

    fileLabel.addEventListener('dragleave', () => {
        fileLabel.style.background = 'white';
        fileLabel.style.borderColor = '#2ecc71';
    });

    fileLabel.addEventListener('drop', (e) => {
        e.preventDefault();
        fileLabel.style.background = 'white';
        fileLabel.style.borderColor = '#2ecc71';
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            showMessage('File selected: ' + files[0].name, 'success');
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            showMessage('File selected: ' + e.target.files[0].name, 'success');
        }
    });
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    document.getElementById('parseBtn').addEventListener('click', parseData);
}

/**
 * Parse uploaded netCDF file
 */
async function parseData() {
    const fileInput = document.getElementById('ncFile');
    
    if (!fileInput.files.length) {
        showMessage('Please select a netCDF file', 'error', 'parseStatus');
        return;
    }

    if (!selectedLocation) {
        showMessage('Please select a location on the map', 'error', 'parseStatus');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    formData.append('latitude', selectedLocation.lat);
    formData.append('longitude', selectedLocation.lng);

    showMessage('Parsing netCDF file...', 'loading', 'parseStatus');

    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Upload failed');
        }

        currentData = result.data;
        showMessage('Data parsed successfully!', 'success', 'parseStatus');
        
        // Display data
        displayData(currentData);
        
        // Make predictions
        await makePredictions();

    } catch (error) {
        showMessage('Error: ' + error.message, 'error', 'parseStatus');
    }
}

/**
 * Display parsed meteorological data
 */
function displayData(data) {
    // Update cards
    document.getElementById('rainfallValue').textContent = 
        data.rainfall.mean ? data.rainfall.mean.toFixed(1) : '--';
    document.getElementById('temperatureValue').textContent = 
        data.temperature.mean ? data.temperature.mean.toFixed(1) : '--';
    document.getElementById('soilMoistureValue').textContent = '50'; // Default
    document.getElementById('humidityValue').textContent = '70'; // Default

    // Show charts container
    document.getElementById('chartsContainer').style.display = 'block';

    // Create visualization
    const rainfallData = [{
        x: ['Min', 'Mean', 'Max'],
        y: [data.rainfall.min, data.rainfall.mean, data.rainfall.max],
        type: 'bar',
        marker: { color: ['#3498db', '#2ecc71', '#e74c3c'] }
    }];

    const tempData = [{
        x: ['Min', 'Mean', 'Max'],
        y: [data.temperature.min, data.temperature.mean, data.temperature.max],
        type: 'bar',
        marker: { color: ['#3498db', '#2ecc71', '#e74c3c'] }
    }];

    const layout = {
        title: 'Meteorological Data Summary',
        xaxis: { title: 'Metric' },
        yaxis: { title: 'Value' },
        showlegend: false
    };

    Plotly.newPlot('weatherChart', rainfallData, {
        title: 'Rainfall Statistics (mm)',
        xaxis: { title: 'Statistic' },
        yaxis: { title: 'Rainfall (mm)' }
    });
}

/**
 * Make predictions with the model
 */
async function makePredictions() {
    if (!currentData) {
        showMessage('No data to predict', 'error', 'predictStatus');
        return;
    }

    const rainfall = currentData.rainfall.mean || 600;
    const temperature = currentData.temperature.mean || 22;

    showMessage('Making predictions...', 'loading', 'predictStatus');

    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                rainfall: rainfall,
                temperature: temperature,
                soil_moisture: 50,
                humidity: 70
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Prediction failed');
        }

        showMessage('Predictions complete!', 'success', 'predictStatus');
        displayPredictions(result.predictions);
        displayRecommendations(result.recommendations, result.advisory);

    } catch (error) {
        showMessage('Error: ' + error.message, 'error', 'predictStatus');
    }
}

/**
 * Display predictions
 */
function displayPredictions(predictions) {
    const container = document.getElementById('predictionsContent');
    container.innerHTML = '';

    if (predictions.maize_suitability !== undefined) {
        container.appendChild(createPredictionCard(
            'Maize (Corn)',
            predictions.maize_suitability,
            '🌽',
            'maize'
        ));
    }

    if (predictions.beans_suitability !== undefined) {
        container.appendChild(createPredictionCard(
            'Beans',
            predictions.beans_suitability,
            '🫘',
            'beans'
        ));
    }
}

/**
 * Create prediction card element
 */
function createPredictionCard(name, score, emoji, type) {
    const card = document.createElement('div');
    card.className = `prediction-card ${type}`;

    const percentage = (score * 100).toFixed(1);
    let statusClass = 'not';
    let statusText = 'Not Recommended';

    if (score >= 0.8) {
        statusClass = 'highly';
        statusText = 'Highly Recommended';
    } else if (score >= 0.6) {
        statusClass = 'recommended';
        statusText = 'Recommended';
    } else if (score >= 0.4) {
        statusClass = 'marginal';
        statusText = 'Marginal';
    }

    card.innerHTML = `
        <h3>${emoji} ${name}</h3>
        <div class="suitability-bar">
            <div class="suitability-fill" style="width: ${percentage}%"></div>
        </div>
        <p>Suitability Score: <strong>${percentage}%</strong></p>
        <span class="recommendation-status ${statusClass}">${statusText}</span>
    `;

    return card;
}

/**
 * Display recommendations
 */
function displayRecommendations(recommendations, advisory) {
    const container = document.getElementById('recommendationsContent');
    container.innerHTML = '';

    recommendations.forEach(rec => {
        const item = document.createElement('div');
        item.className = 'recommendation-item';

        const detailsHtml = `
            <div class="crop-details">
                <strong>Crop Details:</strong>
                <div class="crop-details-grid">
                    <div class="detail-item">
                        <div class="detail-label">Growing Period</div>
                        <div class="detail-value">${rec.crop_details.growing_period}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Spacing</div>
                        <div class="detail-value">${rec.crop_details.spacing}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Seed Rate</div>
                        <div class="detail-value">${rec.crop_details.seed_rate}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Rainfall Needed</div>
                        <div class="detail-value">${rec.crop_details.rainfall_needed}</div>
                    </div>
                </div>
            </div>
        `;

        const reasoningHtml = rec.reasoning.map(r => `<li>${r}</li>`).join('');

        item.innerHTML = `
            <h4>${rec.icon} ${rec.crop_name}</h4>
            <p><strong>Status:</strong> <span class="recommendation-status ${rec.recommendation.toLowerCase().replace(/\s/g, '')}">${rec.recommendation}</span></p>
            <p><strong>Suitability Score:</strong> ${(rec.suitability_score * 100).toFixed(1)}%</p>
            <p><strong>Recommended Action:</strong> ${rec.action}</p>
            <p><strong>Analysis:</strong></p>
            <ul style="margin-left: 20px;">
                ${reasoningHtml}
            </ul>
            ${detailsHtml}
        `;

        container.appendChild(item);
    });

    // Display advisory summary
    if (advisory) {
        const advisoryBox = document.getElementById('advisorySummary');
        const advisoryText = document.getElementById('advisoryText');
        advisoryText.textContent = advisory;
        advisoryBox.style.display = 'block';
    }
}

/**
 * Show status message
 */
function showMessage(message, type = 'info', elementId = 'uploadStatus') {
    const element = document.getElementById(elementId);
    element.textContent = message;
    element.className = `status-message ${type}`;
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}
