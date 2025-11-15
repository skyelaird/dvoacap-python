# Integration Guide

Learn how to integrate DVOACAP-Python into your applications, web services, and automation workflows.

## Table of Contents

- [Python Applications](#python-applications)
- [Web Applications](#web-applications)
- [REST API Integration](#rest-api-integration)
- [Database Integration](#database-integration)
- [Message Queue Integration](#message-queue-integration)
- [Automation and Scheduling](#automation-and-scheduling)
- [Ham Radio Software](#ham-radio-software)
- [Best Practices](#best-practices)

---

## Python Applications

### Basic Integration

Import and use DVOACAP in your Python scripts:

```python
from dvoacap import PredictionEngine
from dvoacap.path_geometry import GeoPoint
import numpy as np

class PropagationService:
    """Service for managing propagation predictions"""

    def __init__(self, tx_location, tx_power=100.0):
        self.engine = PredictionEngine()
        self.engine.params.tx_location = tx_location
        self.engine.params.tx_power = tx_power
        self.engine.params.required_snr = 10.0
        self.engine.params.required_reliability = 0.9

    def predict_path(self, rx_location, frequencies, month, ssn, utc_time):
        """Run prediction for a single path"""
        self.engine.params.month = month
        self.engine.params.ssn = ssn

        self.engine.predict(
            rx_location=rx_location,
            utc_time=utc_time / 24.0,
            frequencies=frequencies
        )

        return {
            'distance_km': self.engine.path.dist * 6370,
            'azimuth_deg': np.rad2deg(self.engine.path.azim_tr),
            'muf_mhz': self.engine.muf_calculator.muf,
            'predictions': [
                {
                    'frequency': freq,
                    'snr_db': pred.signal.snr_db,
                    'reliability': pred.signal.reliability,
                    'mode': pred.get_mode_name(self.engine.path.dist)
                }
                for freq, pred in zip(frequencies, self.engine.predictions)
            ]
        }

# Usage
service = PropagationService(
    tx_location=GeoPoint.from_degrees(44.374, -64.300),
    tx_power=100.0
)

result = service.predict_path(
    rx_location=GeoPoint.from_degrees(51.51, -0.13),  # London
    frequencies=[7.0, 14.0, 21.0],
    month=6,
    ssn=100,
    utc_time=12
)

print(f"Distance: {result['distance_km']:.1f} km")
print(f"MUF: {result['muf_mhz']:.2f} MHz")
```

### Object-Oriented Wrapper

Create a clean API for your application:

```python
from dvoacap import PredictionEngine
from dvoacap.path_geometry import GeoPoint
from dataclasses import dataclass
from typing import List, Optional
import numpy as np

@dataclass
class PropagationResult:
    """Results from a propagation prediction"""
    frequency_mhz: float
    mode: str
    hops: int
    snr_db: float
    reliability_pct: float
    service_probability_pct: float
    signal_strength_db: float

@dataclass
class PathInfo:
    """Information about the propagation path"""
    distance_km: float
    azimuth_tx_rx_deg: float
    azimuth_rx_tx_deg: float
    muf_mhz: float
    fot_mhz: float
    hpf_mhz: float

class DVOACAPClient:
    """High-level client for DVOACAP predictions"""

    def __init__(self, callsign: str, location: tuple[float, float], power_watts: float = 100):
        self.callsign = callsign
        self.location = GeoPoint.from_degrees(*location)
        self.power = power_watts
        self._engine = None

    def _get_engine(self) -> PredictionEngine:
        """Lazy-load the prediction engine"""
        if self._engine is None:
            self._engine = PredictionEngine()
            self._engine.params.tx_location = self.location
            self._engine.params.tx_power = self.power
            self._engine.params.min_angle = np.deg2rad(3.0)
            self._engine.params.required_snr = 10.0
        return self._engine

    def predict(self,
                target_location: tuple[float, float],
                frequencies: List[float],
                month: int,
                sunspot_number: float,
                utc_hour: float) -> tuple[PathInfo, List[PropagationResult]]:
        """
        Run propagation prediction

        Args:
            target_location: (latitude, longitude) in degrees
            frequencies: List of frequencies in MHz
            month: Month (1-12)
            sunspot_number: Sunspot number (0-300)
            utc_hour: UTC time (0-23)

        Returns:
            Tuple of (PathInfo, list of PropagationResult)
        """
        engine = self._get_engine()
        engine.params.month = month
        engine.params.ssn = sunspot_number

        rx_location = GeoPoint.from_degrees(*target_location)

        engine.predict(
            rx_location=rx_location,
            utc_time=utc_hour / 24.0,
            frequencies=frequencies
        )

        # Build path info
        path_info = PathInfo(
            distance_km=engine.path.dist * 6370,
            azimuth_tx_rx_deg=np.rad2deg(engine.path.azim_tr),
            azimuth_rx_tx_deg=np.rad2deg(engine.path.azim_rt),
            muf_mhz=engine.muf_calculator.muf,
            fot_mhz=engine.muf_calculator.muf_info[2].fot,
            hpf_mhz=engine.muf_calculator.muf_info[2].hpf
        )

        # Build results
        results = [
            PropagationResult(
                frequency_mhz=freq,
                mode=pred.get_mode_name(engine.path.dist),
                hops=pred.hop_count,
                snr_db=pred.signal.snr_db,
                reliability_pct=pred.signal.reliability * 100,
                service_probability_pct=pred.service_prob * 100,
                signal_strength_db=pred.signal.total_loss_db
            )
            for freq, pred in zip(frequencies, engine.predictions)
        ]

        return path_info, results

# Usage
client = DVOACAPClient(
    callsign="VE1ATM",
    location=(44.374, -64.300),  # Lunenburg, NS
    power_watts=100
)

path, predictions = client.predict(
    target_location=(51.51, -0.13),  # London
    frequencies=[7.0, 14.0, 21.0, 28.0],
    month=6,
    sunspot_number=100,
    utc_hour=12
)

print(f"Path to target: {path.distance_km:.0f} km at {path.azimuth_tx_rx_deg:.0f}°")
print(f"MUF: {path.muf_mhz:.2f} MHz, FOT: {path.fot_mhz:.2f} MHz")

for pred in predictions:
    print(f"{pred.frequency_mhz} MHz: {pred.mode} mode, "
          f"SNR {pred.snr_db:.1f} dB, {pred.reliability_pct:.0f}% reliable")
```

---

## Web Applications

### Flask REST API

Create a RESTful API service for propagation predictions:

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
from dvoacap import PredictionEngine
from dvoacap.path_geometry import GeoPoint
import numpy as np
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Global prediction engine (thread-safe for read operations)
engine = PredictionEngine()

@app.route('/api/predict', methods=['POST'])
def predict():
    """
    POST /api/predict

    Request body:
    {
        "tx": {"lat": 44.374, "lon": -64.300},
        "rx": {"lat": 51.51, "lon": -0.13},
        "frequencies": [7.0, 14.0, 21.0],
        "month": 6,
        "ssn": 100,
        "utc_hour": 12,
        "tx_power": 100
    }
    """
    try:
        data = request.json

        # Configure engine
        engine.params.tx_location = GeoPoint.from_degrees(
            data['tx']['lat'], data['tx']['lon']
        )
        engine.params.tx_power = data.get('tx_power', 100.0)
        engine.params.month = data['month']
        engine.params.ssn = data['ssn']

        # Run prediction
        rx_location = GeoPoint.from_degrees(data['rx']['lat'], data['rx']['lon'])
        frequencies = data['frequencies']

        engine.predict(
            rx_location=rx_location,
            utc_time=data['utc_hour'] / 24.0,
            frequencies=frequencies
        )

        # Format response
        response = {
            'timestamp': datetime.utcnow().isoformat(),
            'path': {
                'distance_km': round(engine.path.dist * 6370, 1),
                'azimuth_deg': round(np.rad2deg(engine.path.azim_tr), 1),
            },
            'muf': {
                'muf_mhz': round(engine.muf_calculator.muf, 2),
                'fot_mhz': round(engine.muf_calculator.muf_info[2].fot, 2),
            },
            'predictions': [
                {
                    'frequency_mhz': freq,
                    'mode': pred.get_mode_name(engine.path.dist),
                    'snr_db': round(pred.signal.snr_db, 1),
                    'reliability_pct': round(pred.signal.reliability * 100, 1),
                }
                for freq, pred in zip(frequencies, engine.predictions)
            ]
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'version': '0.5.0'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
```

**Usage:**

```bash
# Start server
python3 api_server.py

# Make request
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "tx": {"lat": 44.374, "lon": -64.300},
    "rx": {"lat": 51.51, "lon": -0.13},
    "frequencies": [14.0, 21.0],
    "month": 6,
    "ssn": 100,
    "utc_hour": 12,
    "tx_power": 100
  }'
```

### Django Integration

Integrate with Django models and views:

```python
# models.py
from django.db import models
from dvoacap.path_geometry import GeoPoint
from dvoacap import PredictionEngine
import numpy as np

class Station(models.Model):
    callsign = models.CharField(max_length=10)
    latitude = models.FloatField()
    longitude = models.FloatField()
    power_watts = models.IntegerField(default=100)

    def predict_to(self, target_lat, target_lon, frequencies, month, ssn, utc_hour):
        """Run prediction from this station to target"""
        engine = PredictionEngine()
        engine.params.tx_location = GeoPoint.from_degrees(self.latitude, self.longitude)
        engine.params.tx_power = self.power_watts
        engine.params.month = month
        engine.params.ssn = ssn

        rx_location = GeoPoint.from_degrees(target_lat, target_lon)

        engine.predict(
            rx_location=rx_location,
            utc_time=utc_hour / 24.0,
            frequencies=frequencies
        )

        return {
            'distance_km': engine.path.dist * 6370,
            'azimuth_deg': np.rad2deg(engine.path.azim_tr),
            'predictions': engine.predictions
        }

# views.py
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Station
import json

@require_POST
def predict_view(request):
    data = json.loads(request.body)

    station = Station.objects.get(callsign=data['callsign'])

    result = station.predict_to(
        target_lat=data['target_lat'],
        target_lon=data['target_lon'],
        frequencies=data['frequencies'],
        month=data['month'],
        ssn=data['ssn'],
        utc_hour=data['utc_hour']
    )

    return JsonResponse(result)
```

---

## Database Integration

### Store Predictions in Database

```python
import sqlite3
from dvoacap import PredictionEngine
from dvoacap.path_geometry import GeoPoint
import json
from datetime import datetime

class PredictionDatabase:
    """Store and retrieve predictions from SQLite"""

    def __init__(self, db_path='predictions.db'):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                tx_lat REAL,
                tx_lon REAL,
                rx_lat REAL,
                rx_lon REAL,
                month INTEGER,
                ssn REAL,
                utc_hour REAL,
                distance_km REAL,
                azimuth_deg REAL,
                muf_mhz REAL,
                predictions_json TEXT
            )
        ''')
        self.conn.commit()

    def store_prediction(self, engine, frequencies, month, ssn, utc_hour):
        """Store prediction results"""
        predictions_data = [
            {
                'frequency': freq,
                'snr_db': pred.signal.snr_db,
                'reliability': pred.signal.reliability,
                'mode': pred.get_mode_name(engine.path.dist)
            }
            for freq, pred in zip(frequencies, engine.predictions)
        ]

        tx_lat, tx_lon = engine.params.tx_location.to_degrees()
        rx_lat, rx_lon = engine.path.rx_location.to_degrees()

        self.conn.execute('''
            INSERT INTO predictions
            (timestamp, tx_lat, tx_lon, rx_lat, rx_lon, month, ssn, utc_hour,
             distance_km, azimuth_deg, muf_mhz, predictions_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.utcnow().isoformat(),
            tx_lat, tx_lon, rx_lat, rx_lon,
            month, ssn, utc_hour,
            engine.path.dist * 6370,
            np.rad2deg(engine.path.azim_tr),
            engine.muf_calculator.muf,
            json.dumps(predictions_data)
        ))
        self.conn.commit()

    def get_recent_predictions(self, limit=10):
        """Retrieve recent predictions"""
        cursor = self.conn.execute('''
            SELECT * FROM predictions
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))

        return cursor.fetchall()
```

---

## Message Queue Integration

### Celery Task Queue

For asynchronous prediction processing:

```python
from celery import Celery
from dvoacap import PredictionEngine
from dvoacap.path_geometry import GeoPoint
import numpy as np

app = Celery('dvoacap_tasks', broker='redis://localhost:6379/0')

@app.task
def run_prediction_async(tx_lat, tx_lon, rx_lat, rx_lon, frequencies, month, ssn, utc_hour):
    """Asynchronous prediction task"""
    engine = PredictionEngine()
    engine.params.tx_location = GeoPoint.from_degrees(tx_lat, tx_lon)
    engine.params.month = month
    engine.params.ssn = ssn

    rx_location = GeoPoint.from_degrees(rx_lat, rx_lon)

    engine.predict(
        rx_location=rx_location,
        utc_time=utc_hour / 24.0,
        frequencies=frequencies
    )

    return {
        'distance_km': engine.path.dist * 6370,
        'muf_mhz': engine.muf_calculator.muf,
        'predictions': [
            {
                'frequency': freq,
                'snr_db': pred.signal.snr_db,
                'reliability': pred.signal.reliability
            }
            for freq, pred in zip(frequencies, engine.predictions)
        ]
    }

# Usage
result = run_prediction_async.delay(44.374, -64.300, 51.51, -0.13,
                                     [7.0, 14.0], 6, 100, 12)
print(result.get())  # Block until complete
```

---

## Automation and Scheduling

### Cron Job Integration

Schedule regular prediction updates:

```bash
# crontab -e

# Run predictions every 2 hours
0 */2 * * * cd /home/user/dvoacap-python/Dashboard && /usr/bin/python3 generate_predictions.py

# Run at specific times (e.g., 00:00, 06:00, 12:00, 18:00 UTC)
0 0,6,12,18 * * * cd /home/user/dvoacap-python && /usr/bin/python3 scripts/daily_predictions.py
```

### Python Scheduling (APScheduler)

```python
from apscheduler.schedulers.blocking import BlockingScheduler
from dvoacap_client import DVOACAPClient

scheduler = BlockingScheduler()
client = DVOACAPClient("VE1ATM", (44.374, -64.300))

@scheduler.scheduled_job('interval', hours=2)
def run_predictions():
    """Run predictions every 2 hours"""
    targets = [
        ("EU", (50.0, 10.0)),
        ("JA", (36.0, 138.0)),
        ("VK", (-33.87, 151.21))
    ]

    for name, location in targets:
        path, preds = client.predict(
            target_location=location,
            frequencies=[7.0, 14.0, 21.0],
            month=6,
            sunspot_number=100,
            utc_hour=12
        )
        print(f"{name}: MUF {path.muf_mhz:.2f} MHz")

scheduler.start()
```

---

## Ham Radio Software

### Integration with WSJT-X / JTDX

Monitor WSJT-X and provide propagation predictions:

```python
import socket
from dvoacap_client import DVOACAPClient

def parse_wsjtx_packet(data):
    """Parse WSJT-X UDP packet (simplified)"""
    # Implement WSJT-X protocol parsing
    pass

client = DVOACAPClient("VE1ATM", (44.374, -64.300))
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('127.0.0.1', 2237))

while True:
    data, addr = sock.recvfrom(1024)
    callsign, grid = parse_wsjtx_packet(data)

    # Get prediction for this station
    # ...
```

### Log Analysis

Analyze your QSO log and compare with predictions:

```python
def analyze_log_vs_predictions(adif_file, predictions_db):
    """Compare actual QSOs with predictions"""
    # Parse ADIF
    # Compare with stored predictions
    # Generate accuracy report
    pass
```

---

## Best Practices

### Performance Optimization

1. **Reuse PredictionEngine instances:**
   ```python
   engine = PredictionEngine()  # Create once
   # Reuse for multiple predictions
   ```

2. **Batch predictions:**
   ```python
   # Process multiple frequencies at once
   engine.predict(rx_location, utc_time, frequencies=[7.0, 14.0, 21.0, 28.0])
   ```

3. **Cache CCIR maps:**
   Maps are automatically cached after first load.

### Error Handling

```python
try:
    engine.predict(rx_location, utc_time, frequencies)
except ValueError as e:
    # Invalid parameters
    logger.error(f"Invalid prediction parameters: {e}")
except RuntimeError as e:
    # Prediction failed (e.g., path not feasible)
    logger.warning(f"Prediction failed: {e}")
```

### Thread Safety

DVOACAP is **not thread-safe** for concurrent writes. Use separate engine instances per thread or protect with locks.

```python
import threading

class ThreadSafePredictionService:
    def __init__(self):
        self.lock = threading.Lock()
        self.engine = PredictionEngine()

    def predict(self, *args, **kwargs):
        with self.lock:
            return self.engine.predict(*args, **kwargs)
```

---

## Next Steps

- **[API Reference](API-Reference)** - Complete class documentation
- **[Quick Examples](Quick-Examples)** - More code examples
- **[Performance Tips](Performance-Tips)** - Optimization strategies
- **[Dashboard Guide](Dashboard-Guide)** - Web dashboard setup

---

For questions or issues, visit the [GitHub repository](https://github.com/skyelaird/dvoacap-python/issues).
