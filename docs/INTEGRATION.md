# DVOACAP-Python Integration Guide

This guide shows how to integrate DVOACAP-Python with web applications, dashboards, and other systems.

## Table of Contents

1. [REST API Integration](#rest-api-integration)
2. [Web Dashboard Integration](#web-dashboard-integration)
3. [Database Integration](#database-integration)
4. [Real-Time Monitoring](#real-time-monitoring)
5. [Data Visualization](#data-visualization)
6. [Microservices Architecture](#microservices-architecture)

---

## REST API Integration

### Flask API Example

Create a REST API for propagation predictions:

```python
# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint
import numpy as np

app = Flask(__name__)
CORS(app)  # Enable CORS for web dashboard access

# Global engine instance (reusable)
engine = PredictionEngine()

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    Predict propagation for given parameters

    Request JSON:
    {
        "tx_location": {"lat": 40.0, "lon": -75.0},
        "rx_location": {"lat": 51.5, "lon": -0.1},
        "frequencies": [14.0, 21.0, 28.0],
        "utc_hour": 12,
        "ssn": 100,
        "month": 6,
        "tx_power": 100.0
    }
    """
    try:
        data = request.json

        # Configure engine
        engine.params.ssn = data.get('ssn', 100.0)
        engine.params.month = data.get('month', 6)
        engine.params.tx_power = data.get('tx_power', 100.0)

        # Parse locations
        tx = GeoPoint.from_degrees(
            data['tx_location']['lat'],
            data['tx_location']['lon']
        )
        rx = GeoPoint.from_degrees(
            data['rx_location']['lat'],
            data['rx_location']['lon']
        )

        engine.params.tx_location = tx

        # Run prediction
        utc_time = data.get('utc_hour', 12) / 24.0
        frequencies = data.get('frequencies', [14.0])

        engine.predict(rx_location=rx, utc_time=utc_time, frequencies=frequencies)

        # Build response
        results = []
        for freq, pred in zip(frequencies, engine.predictions):
            results.append({
                'frequency': freq,
                'snr_db': round(pred.signal.snr_db, 2),
                'reliability': round(pred.signal.reliability, 4),
                'service_probability': round(pred.service_prob, 4),
                'hop_count': pred.hop_count,
                'mode': pred.get_mode_name(engine.path.dist),
                'tx_elevation': round(np.rad2deg(pred.tx_elevation), 2)
            })

        response = {
            'success': True,
            'path': {
                'distance_km': round(engine.path.get_distance_km(), 1),
                'azimuth': round(engine.path.get_azimuth_tr_degrees(), 1),
                'back_azimuth': round(engine.path.get_azimuth_rt_degrees(), 1)
            },
            'muf': {
                'muf': round(engine.muf_calculator.muf, 2),
                'fot': round(engine.muf_calculator.muf_info[2].fot, 2),
                'hpf': round(engine.muf_calculator.muf_info[2].hpf, 2)
            },
            'predictions': results
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/path', methods=['GET'])
def calculate_path():
    """
    Calculate great circle path information

    Query params: tx_lat, tx_lon, rx_lat, rx_lon
    """
    try:
        tx_lat = float(request.args.get('tx_lat'))
        tx_lon = float(request.args.get('tx_lon'))
        rx_lat = float(request.args.get('rx_lat'))
        rx_lon = float(request.args.get('rx_lon'))

        from dvoacap.path_geometry import PathGeometry

        path = PathGeometry()
        tx = GeoPoint.from_degrees(tx_lat, tx_lon)
        rx = GeoPoint.from_degrees(rx_lat, rx_lon)
        path.set_tx_rx(tx, rx)

        # Get midpoint
        midpoint = path.get_point_at_dist(path.dist / 2)
        mid_lat, mid_lon = midpoint.to_degrees()

        return jsonify({
            'success': True,
            'distance_km': round(path.get_distance_km(), 1),
            'azimuth': round(path.get_azimuth_tr_degrees(), 1),
            'back_azimuth': round(path.get_azimuth_rt_degrees(), 1),
            'midpoint': {
                'lat': round(mid_lat, 4),
                'lon': round(mid_lon, 4)
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/frequency-scan', methods=['POST'])
def frequency_scan():
    """
    Scan multiple frequencies to find best propagation

    Request JSON:
    {
        "tx_location": {"lat": 40.0, "lon": -75.0},
        "rx_location": {"lat": 51.5, "lon": -0.1},
        "freq_start": 7,
        "freq_end": 30,
        "freq_step": 1,
        "utc_hour": 12
    }
    """
    try:
        data = request.json

        # Parse locations
        tx = GeoPoint.from_degrees(
            data['tx_location']['lat'],
            data['tx_location']['lon']
        )
        rx = GeoPoint.from_degrees(
            data['rx_location']['lat'],
            data['rx_location']['lon']
        )

        # Generate frequency list
        freq_start = data.get('freq_start', 7)
        freq_end = data.get('freq_end', 30)
        freq_step = data.get('freq_step', 1)
        frequencies = list(range(freq_start, freq_end + 1, freq_step))

        # Run prediction
        engine.params.tx_location = tx
        utc_time = data.get('utc_hour', 12) / 24.0
        engine.predict(rx_location=rx, utc_time=utc_time, frequencies=frequencies)

        # Build results
        results = []
        for freq, pred in zip(frequencies, engine.predictions):
            results.append({
                'frequency': freq,
                'snr_db': round(pred.signal.snr_db, 2),
                'reliability': round(pred.signal.reliability, 4)
            })

        # Find best frequency
        best_idx = max(range(len(results)), key=lambda i: results[i]['reliability'])

        return jsonify({
            'success': True,
            'results': results,
            'best_frequency': results[best_idx]
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '0.5.0',
        'service': 'dvoacap-api'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### FastAPI Alternative

For high-performance async API:

```python
# fastapi_app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint

app = FastAPI(title="DVOACAP Prediction API", version="0.5.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class Location(BaseModel):
    lat: float
    lon: float

class PredictionRequest(BaseModel):
    tx_location: Location
    rx_location: Location
    frequencies: List[float]
    utc_hour: Optional[float] = 12.0
    ssn: Optional[float] = 100.0
    month: Optional[int] = 6
    tx_power: Optional[float] = 100.0

class PredictionResult(BaseModel):
    frequency: float
    snr_db: float
    reliability: float
    service_probability: float
    hop_count: int
    mode: str

class PredictionResponse(BaseModel):
    success: bool
    path: dict
    muf: dict
    predictions: List[PredictionResult]

# Global engine
engine = PredictionEngine()

@app.post("/api/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Run propagation prediction"""
    try:
        # Configure
        engine.params.ssn = request.ssn
        engine.params.month = request.month
        engine.params.tx_power = request.tx_power

        tx = GeoPoint.from_degrees(request.tx_location.lat, request.tx_location.lon)
        rx = GeoPoint.from_degrees(request.rx_location.lat, request.rx_location.lon)
        engine.params.tx_location = tx

        # Predict
        engine.predict(rx_location=rx,
                      utc_time=request.utc_hour / 24.0,
                      frequencies=request.frequencies)

        # Build response
        results = []
        for freq, pred in zip(request.frequencies, engine.predictions):
            results.append(PredictionResult(
                frequency=freq,
                snr_db=round(pred.signal.snr_db, 2),
                reliability=round(pred.signal.reliability, 4),
                service_probability=round(pred.service_prob, 4),
                hop_count=pred.hop_count,
                mode=pred.get_mode_name(engine.path.dist)
            ))

        return PredictionResponse(
            success=True,
            path={
                'distance_km': round(engine.path.get_distance_km(), 1),
                'azimuth': round(engine.path.get_azimuth_tr_degrees(), 1)
            },
            muf={
                'muf': round(engine.muf_calculator.muf, 2),
                'fot': round(engine.muf_calculator.muf_info[2].fot, 2)
            },
            predictions=results
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "0.5.0"}

# Run with: uvicorn fastapi_app:app --reload
```

---

## Web Dashboard Integration

> **Note:** DVOACAP-Python includes a complete production-ready dashboard in the `Dashboard/` directory with Flask backend, interactive visualizations, and DXCC tracking. See [Dashboard/README.md](../Dashboard/README.md) for setup instructions. The examples below show how to build your own custom dashboards.

### React Dashboard Example

```javascript
// PropagationDashboard.jsx
import React, { useState } from 'react';
import axios from 'axios';

const PropagationDashboard = () => {
  const [txLocation, setTxLocation] = useState({ lat: 40.0, lon: -75.0 });
  const [rxLocation, setRxLocation] = useState({ lat: 51.5, lon: -0.1 });
  const [frequency, setFrequency] = useState(14.0);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const runPrediction = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:5000/api/predict', {
        tx_location: txLocation,
        rx_location: rxLocation,
        frequencies: [frequency],
        utc_hour: 12,
        ssn: 100,
        month: 6
      });

      setResults(response.data);
    } catch (error) {
      console.error('Prediction failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      <h1>HF Propagation Dashboard</h1>

      <div className="input-section">
        <h2>Configuration</h2>

        <div className="location-inputs">
          <div>
            <h3>Transmitter</h3>
            <input
              type="number"
              placeholder="Latitude"
              value={txLocation.lat}
              onChange={(e) => setTxLocation({...txLocation, lat: parseFloat(e.target.value)})}
            />
            <input
              type="number"
              placeholder="Longitude"
              value={txLocation.lon}
              onChange={(e) => setTxLocation({...txLocation, lon: parseFloat(e.target.value)})}
            />
          </div>

          <div>
            <h3>Receiver</h3>
            <input
              type="number"
              placeholder="Latitude"
              value={rxLocation.lat}
              onChange={(e) => setRxLocation({...rxLocation, lat: parseFloat(e.target.value)})}
            />
            <input
              type="number"
              placeholder="Longitude"
              value={rxLocation.lon}
              onChange={(e) => setRxLocation({...rxLocation, lon: parseFloat(e.target.value)})}
            />
          </div>
        </div>

        <div>
          <label>Frequency (MHz):</label>
          <input
            type="number"
            value={frequency}
            onChange={(e) => setFrequency(parseFloat(e.target.value))}
          />
        </div>

        <button onClick={runPrediction} disabled={loading}>
          {loading ? 'Running...' : 'Run Prediction'}
        </button>
      </div>

      {results && (
        <div className="results-section">
          <h2>Results</h2>

          <div className="path-info">
            <h3>Path Information</h3>
            <p>Distance: {results.path.distance_km} km</p>
            <p>Azimuth: {results.path.azimuth}°</p>
          </div>

          <div className="muf-info">
            <h3>MUF Information</h3>
            <p>MUF: {results.muf.muf} MHz</p>
            <p>FOT: {results.muf.fot} MHz</p>
            <p>HPF: {results.muf.hpf} MHz</p>
          </div>

          <div className="prediction-info">
            <h3>Prediction</h3>
            {results.predictions.map((pred, idx) => (
              <div key={idx} className="prediction-card">
                <h4>{pred.frequency} MHz</h4>
                <p>SNR: {pred.snr_db} dB</p>
                <p>Reliability: {(pred.reliability * 100).toFixed(1)}%</p>
                <p>Mode: {pred.mode}</p>
                <p>Hops: {pred.hop_count}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PropagationDashboard;
```

### HTML/JavaScript Simple Dashboard

```html
<!-- dashboard.html -->
<!DOCTYPE html>
<html>
<head>
    <title>HF Propagation Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .input-group { margin: 10px 0; }
        .results { margin-top: 20px; padding: 20px; background: #f0f0f0; }
        .prediction-card {
            display: inline-block;
            margin: 10px;
            padding: 15px;
            background: white;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        button {
            padding: 10px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover { background: #0056b3; }
    </style>
</head>
<body>
    <div class="container">
        <h1>HF Propagation Dashboard</h1>

        <div class="input-section">
            <div class="input-group">
                <h3>Transmitter Location</h3>
                <input type="number" id="tx_lat" placeholder="Latitude" value="40.0">
                <input type="number" id="tx_lon" placeholder="Longitude" value="-75.0">
            </div>

            <div class="input-group">
                <h3>Receiver Location</h3>
                <input type="number" id="rx_lat" placeholder="Latitude" value="51.5">
                <input type="number" id="rx_lon" placeholder="Longitude" value="-0.1">
            </div>

            <div class="input-group">
                <label>Frequencies (comma-separated MHz):</label>
                <input type="text" id="frequencies" value="7,14,21,28">
            </div>

            <button onclick="runPrediction()">Run Prediction</button>
        </div>

        <div id="results" class="results" style="display: none;">
            <h2>Results</h2>
            <div id="results-content"></div>
        </div>
    </div>

    <script>
        async function runPrediction() {
            const txLat = parseFloat(document.getElementById('tx_lat').value);
            const txLon = parseFloat(document.getElementById('tx_lon').value);
            const rxLat = parseFloat(document.getElementById('rx_lat').value);
            const rxLon = parseFloat(document.getElementById('rx_lon').value);
            const frequencies = document.getElementById('frequencies').value
                .split(',').map(f => parseFloat(f.trim()));

            const requestData = {
                tx_location: { lat: txLat, lon: txLon },
                rx_location: { lat: rxLat, lon: rxLon },
                frequencies: frequencies,
                utc_hour: 12,
                ssn: 100,
                month: 6
            };

            try {
                const response = await fetch('http://localhost:5000/api/predict', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(requestData)
                });

                const data = await response.json();
                displayResults(data);
            } catch (error) {
                alert('Error: ' + error.message);
            }
        }

        function displayResults(data) {
            const resultsDiv = document.getElementById('results');
            const contentDiv = document.getElementById('results-content');

            let html = `
                <div class="path-info">
                    <h3>Path Information</h3>
                    <p>Distance: ${data.path.distance_km} km</p>
                    <p>Azimuth: ${data.path.azimuth}°</p>
                </div>

                <div class="muf-info">
                    <h3>MUF Information</h3>
                    <p>MUF: ${data.muf.muf} MHz</p>
                    <p>FOT: ${data.muf.fot} MHz</p>
                    <p>HPF: ${data.muf.hpf} MHz</p>
                </div>

                <h3>Predictions</h3>
            `;

            data.predictions.forEach(pred => {
                html += `
                    <div class="prediction-card">
                        <h4>${pred.frequency} MHz</h4>
                        <p><strong>SNR:</strong> ${pred.snr_db} dB</p>
                        <p><strong>Reliability:</strong> ${(pred.reliability * 100).toFixed(1)}%</p>
                        <p><strong>Mode:</strong> ${pred.mode}</p>
                        <p><strong>Hops:</strong> ${pred.hop_count}</p>
                    </div>
                `;
            });

            contentDiv.innerHTML = html;
            resultsDiv.style.display = 'block';
        }
    </script>
</body>
</html>
```

---

## Database Integration

### PostgreSQL Storage

```python
# db_integration.py
import psycopg2
from datetime import datetime
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint

class PropagationDatabase:
    """Store and retrieve propagation predictions from PostgreSQL"""

    def __init__(self, db_config):
        self.conn = psycopg2.connect(**db_config)
        self.create_tables()

    def create_tables(self):
        """Create database tables"""
        with self.conn.cursor() as cur:
            # Predictions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    tx_lat FLOAT,
                    tx_lon FLOAT,
                    rx_lat FLOAT,
                    rx_lon FLOAT,
                    frequency FLOAT,
                    ssn FLOAT,
                    month INTEGER,
                    utc_hour FLOAT,
                    distance_km FLOAT,
                    azimuth FLOAT,
                    muf FLOAT,
                    snr_db FLOAT,
                    reliability FLOAT,
                    hop_count INTEGER,
                    mode VARCHAR(10)
                )
            """)

            # Index for faster queries
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_predictions_timestamp
                ON predictions(timestamp)
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_predictions_locations
                ON predictions(tx_lat, tx_lon, rx_lat, rx_lon)
            """)

            self.conn.commit()

    def store_prediction(self, engine, frequency, prediction, metadata):
        """Store a prediction result"""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO predictions (
                    tx_lat, tx_lon, rx_lat, rx_lon,
                    frequency, ssn, month, utc_hour,
                    distance_km, azimuth, muf,
                    snr_db, reliability, hop_count, mode
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                metadata['tx_lat'], metadata['tx_lon'],
                metadata['rx_lat'], metadata['rx_lon'],
                frequency,
                engine.params.ssn,
                engine.params.month,
                metadata['utc_hour'],
                engine.path.get_distance_km(),
                engine.path.get_azimuth_tr_degrees(),
                engine.muf_calculator.muf,
                prediction.signal.snr_db,
                prediction.signal.reliability,
                prediction.hop_count,
                prediction.get_mode_name(engine.path.dist)
            ))
            self.conn.commit()

    def get_historical_predictions(self, tx_lat, tx_lon, rx_lat, rx_lon,
                                   frequency, days=30):
        """Retrieve historical predictions for a path"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT timestamp, snr_db, reliability, muf
                FROM predictions
                WHERE tx_lat = %s AND tx_lon = %s
                  AND rx_lat = %s AND rx_lon = %s
                  AND frequency = %s
                  AND timestamp > CURRENT_TIMESTAMP - INTERVAL '%s days'
                ORDER BY timestamp DESC
            """, (tx_lat, tx_lon, rx_lat, rx_lon, frequency, days))

            return cur.fetchall()

    def get_path_statistics(self, tx_lat, tx_lon, rx_lat, rx_lon, frequency):
        """Get statistical summary for a path"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT
                    AVG(snr_db) as avg_snr,
                    AVG(reliability) as avg_reliability,
                    AVG(muf) as avg_muf,
                    MIN(snr_db) as min_snr,
                    MAX(snr_db) as max_snr,
                    COUNT(*) as sample_count
                FROM predictions
                WHERE tx_lat = %s AND tx_lon = %s
                  AND rx_lat = %s AND rx_lon = %s
                  AND frequency = %s
            """, (tx_lat, tx_lon, rx_lat, rx_lon, frequency))

            return cur.fetchone()

# Example usage
db_config = {
    'host': 'localhost',
    'database': 'propagation',
    'user': 'dvoacap',
    'password': 'password'
}

db = PropagationDatabase(db_config)

# Run and store prediction
engine = PredictionEngine()
engine.params.tx_location = GeoPoint.from_degrees(40.0, -75.0)
rx = GeoPoint.from_degrees(51.5, -0.1)
engine.predict(rx_location=rx, utc_time=0.5, frequencies=[14.0])

metadata = {
    'tx_lat': 40.0, 'tx_lon': -75.0,
    'rx_lat': 51.5, 'rx_lon': -0.1,
    'utc_hour': 12.0
}

db.store_prediction(engine, 14.0, engine.predictions[0], metadata)

# Retrieve historical data
history = db.get_historical_predictions(40.0, -75.0, 51.5, -0.1, 14.0, days=30)
stats = db.get_path_statistics(40.0, -75.0, 51.5, -0.1, 14.0)
```

---

## Real-Time Monitoring

### WebSocket Real-Time Updates

```python
# websocket_server.py
from flask import Flask
from flask_socketio import SocketIO, emit
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint
import threading
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global monitoring state
monitoring_active = False
monitoring_thread = None

def monitoring_loop(params):
    """Background thread for continuous monitoring"""
    global monitoring_active

    engine = PredictionEngine()
    engine.params.ssn = params['ssn']
    engine.params.month = params['month']
    engine.params.tx_location = GeoPoint.from_degrees(
        params['tx_lat'], params['tx_lon']
    )

    rx = GeoPoint.from_degrees(params['rx_lat'], params['rx_lon'])
    frequency = params['frequency']

    while monitoring_active:
        try:
            # Run prediction
            current_time = time.time() % 86400 / 86400  # Current UTC fraction
            engine.predict(rx_location=rx, utc_time=current_time, frequencies=[frequency])

            pred = engine.predictions[0]

            # Emit update to all connected clients
            socketio.emit('prediction_update', {
                'timestamp': time.time(),
                'frequency': frequency,
                'snr_db': round(pred.signal.snr_db, 2),
                'reliability': round(pred.signal.reliability, 4),
                'muf': round(engine.muf_calculator.muf, 2),
                'hop_count': pred.hop_count
            })

            time.sleep(60)  # Update every minute

        except Exception as e:
            socketio.emit('error', {'message': str(e)})
            time.sleep(60)

@socketio.on('start_monitoring')
def handle_start_monitoring(data):
    """Start continuous monitoring"""
    global monitoring_active, monitoring_thread

    if not monitoring_active:
        monitoring_active = True
        monitoring_thread = threading.Thread(target=monitoring_loop, args=(data,))
        monitoring_thread.start()
        emit('status', {'message': 'Monitoring started'})

@socketio.on('stop_monitoring')
def handle_stop_monitoring():
    """Stop continuous monitoring"""
    global monitoring_active
    monitoring_active = False
    emit('status', {'message': 'Monitoring stopped'})

@socketio.on('connect')
def handle_connect():
    emit('status', {'message': 'Connected to DVOACAP monitoring server'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
```

Client-side WebSocket integration:

```html
<!-- monitoring_client.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Real-Time Propagation Monitoring</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Real-Time Propagation Monitoring</h1>

    <div>
        <button onclick="startMonitoring()">Start Monitoring</button>
        <button onclick="stopMonitoring()">Stop Monitoring</button>
    </div>

    <div>
        <h2>Current Conditions</h2>
        <p>SNR: <span id="current-snr">--</span> dB</p>
        <p>Reliability: <span id="current-reliability">--</span>%</p>
        <p>MUF: <span id="current-muf">--</span> MHz</p>
    </div>

    <canvas id="chart" width="800" height="400"></canvas>

    <script>
        const socket = io('http://localhost:5000');

        // Chart setup
        const ctx = document.getElementById('chart').getContext('2d');
        const chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'SNR (dB)',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                scales: {
                    x: { display: true, title: { display: true, text: 'Time' }},
                    y: { display: true, title: { display: true, text: 'SNR (dB)' }}
                }
            }
        });

        socket.on('prediction_update', (data) => {
            // Update current values
            document.getElementById('current-snr').textContent = data.snr_db;
            document.getElementById('current-reliability').textContent =
                (data.reliability * 100).toFixed(1);
            document.getElementById('current-muf').textContent = data.muf;

            // Update chart
            const time = new Date(data.timestamp * 1000).toLocaleTimeString();
            chart.data.labels.push(time);
            chart.data.datasets[0].data.push(data.snr_db);

            // Keep last 60 points
            if (chart.data.labels.length > 60) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }

            chart.update();
        });

        function startMonitoring() {
            socket.emit('start_monitoring', {
                tx_lat: 40.0,
                tx_lon: -75.0,
                rx_lat: 51.5,
                rx_lon: -0.1,
                frequency: 14.0,
                ssn: 100,
                month: 6
            });
        }

        function stopMonitoring() {
            socket.emit('stop_monitoring');
        }
    </script>
</body>
</html>
```

---

## Data Visualization

### Matplotlib Integration

```python
# visualization.py
import matplotlib.pyplot as plt
import numpy as np
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint

def plot_frequency_response(tx_location, rx_location):
    """Plot SNR vs frequency"""
    engine = PredictionEngine()
    engine.params.tx_location = tx_location

    frequencies = np.arange(3, 30, 0.5)
    engine.predict(rx_location=rx_location, utc_time=0.5, frequencies=frequencies.tolist())

    snr_values = [pred.signal.snr_db for pred in engine.predictions]
    reliability = [pred.signal.reliability * 100 for pred in engine.predictions]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    # SNR plot
    ax1.plot(frequencies, snr_values, 'b-', linewidth=2)
    ax1.axhline(y=10, color='r', linestyle='--', label='Required SNR (10 dB)')
    ax1.set_xlabel('Frequency (MHz)')
    ax1.set_ylabel('SNR (dB)')
    ax1.set_title('Signal-to-Noise Ratio vs Frequency')
    ax1.grid(True)
    ax1.legend()

    # Reliability plot
    ax2.plot(frequencies, reliability, 'g-', linewidth=2)
    ax2.axhline(y=70, color='r', linestyle='--', label='70% Reliability')
    ax2.set_xlabel('Frequency (MHz)')
    ax2.set_ylabel('Reliability (%)')
    ax2.set_title('Circuit Reliability vs Frequency')
    ax2.grid(True)
    ax2.legend()

    plt.tight_layout()
    plt.savefig('frequency_response.png', dpi=300)
    plt.show()

def plot_diurnal_variation(tx_location, rx_location, frequency):
    """Plot propagation vs time of day"""
    engine = PredictionEngine()
    engine.params.tx_location = tx_location

    hours = np.arange(0, 24, 1)
    snr_values = []
    muf_values = []

    for hour in hours:
        engine.predict(rx_location=rx_location,
                      utc_time=hour/24.0,
                      frequencies=[frequency])
        snr_values.append(engine.predictions[0].signal.snr_db)
        muf_values.append(engine.muf_calculator.muf)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    ax1.plot(hours, snr_values, 'b-o', linewidth=2, markersize=6)
    ax1.axhline(y=10, color='r', linestyle='--', alpha=0.5)
    ax1.set_xlabel('UTC Hour')
    ax1.set_ylabel('SNR (dB)')
    ax1.set_title(f'Diurnal Variation - {frequency} MHz')
    ax1.grid(True)
    ax1.set_xticks(hours)

    ax2.plot(hours, muf_values, 'g-o', linewidth=2, markersize=6)
    ax2.axhline(y=frequency, color='r', linestyle='--', label=f'Operating Freq ({frequency} MHz)')
    ax2.set_xlabel('UTC Hour')
    ax2.set_ylabel('MUF (MHz)')
    ax2.set_title('Maximum Usable Frequency')
    ax2.grid(True)
    ax2.set_xticks(hours)
    ax2.legend()

    plt.tight_layout()
    plt.savefig('diurnal_variation.png', dpi=300)
    plt.show()

# Example usage
tx = GeoPoint.from_degrees(40.0, -75.0)
rx = GeoPoint.from_degrees(51.5, -0.1)

plot_frequency_response(tx, rx)
plot_diurnal_variation(tx, rx, 14.0)
```

---

## Microservices Architecture

### Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  dvoacap-api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://dvoacap:password@db:5432/propagation
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./DVoaData:/app/DVoaData

  db:
    image: postgres:14
    environment:
      - POSTGRES_USER=dvoacap
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=propagation
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - dvoacap-api

volumes:
  postgres_data:
  redis_data:
```

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/dvoacap ./dvoacap
COPY app.py .
COPY DVoaData ./DVoaData

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

---

For more examples and detailed API documentation, visit:
- [USAGE.md](USAGE.md) - Basic usage patterns
- [GitHub Repository](https://github.com/skyelaird/dvoacap-python)
- [Issues & Support](https://github.com/skyelaird/dvoacap-python/issues)
