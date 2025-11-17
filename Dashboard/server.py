#!/usr/bin/env python3
"""
VE1ATM HF Propagation Dashboard Server

Lightweight Flask server that:
- Serves the dashboard and static files
- Provides API endpoint to trigger prediction generation
- Allows on-demand refresh from the web interface

Usage:
    python3 server.py

Then visit: http://localhost:8000
"""

import sys
import json
import threading
import subprocess
from pathlib import Path
from datetime import datetime
from flask import Flask, jsonify, send_from_directory, request, make_response
from flask_cors import CORS

# Add parent directory to import dvoacap
sys.path.insert(0, str(Path(__file__).parent.parent))

app = Flask(__name__)
CORS(app)  # Enable CORS for API requests

# Global state for prediction generation
generation_state = {
    'running': False,
    'progress': 0,
    'message': 'Ready',
    'last_updated': None,
    'error': None
}

# Global configuration
server_config = {
    'disable_cache': False  # Set to True to disable HTTP caching
}


def apply_cache_control(response):
    """
    Apply cache control headers to a response based on server configuration

    Args:
        response: Flask response object

    Returns:
        Modified response with cache control headers
    """
    if server_config.get('disable_cache', False) or app.debug:
        # Disable caching for development
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    else:
        # Allow caching in production with 5 minute max-age
        response.headers['Cache-Control'] = 'public, max-age=300'

    return response


def run_prediction_generator():
    """
    Run the prediction generator in a background thread
    Updates global state as it progresses
    """
    global generation_state

    try:
        generation_state['running'] = True
        generation_state['progress'] = 10
        generation_state['message'] = 'Starting prediction engine...'
        generation_state['error'] = None

        # Run the prediction generator as a subprocess
        script_path = Path(__file__).parent / 'generate_predictions.py'

        generation_state['progress'] = 20
        generation_state['message'] = 'Fetching solar conditions...'

        # Execute the script
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=str(Path(__file__).parent),
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode == 0:
            generation_state['progress'] = 100
            generation_state['message'] = 'Predictions updated successfully!'
            generation_state['last_updated'] = datetime.now().isoformat()
        else:
            # Combine stdout and stderr for complete error message
            error_output = result.stderr if result.stderr else result.stdout
            if not error_output:
                error_output = f"Process exited with code {result.returncode}"
            generation_state['error'] = f"Generator failed: {error_output[:500]}"
            generation_state['message'] = 'Generation failed'

    except subprocess.TimeoutExpired:
        generation_state['error'] = 'Prediction generation timed out (>5 minutes)'
        generation_state['message'] = 'Timeout error'
    except Exception as e:
        generation_state['error'] = str(e)
        generation_state['message'] = f'Error: {str(e)[:100]}'
    finally:
        generation_state['running'] = False


# =============================================================================
# API Endpoints
# =============================================================================

@app.route('/api/generate', methods=['POST'])
def trigger_generation():
    """
    API endpoint to trigger prediction generation

    Returns:
        JSON with status
    """
    global generation_state

    if generation_state['running']:
        return jsonify({
            'status': 'already_running',
            'message': 'Prediction generation already in progress'
        }), 409

    # Start generation in background thread
    thread = threading.Thread(target=run_prediction_generator, daemon=True)
    thread.start()

    return jsonify({
        'status': 'started',
        'message': 'Prediction generation started'
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """
    API endpoint for health check monitoring

    Returns:
        JSON with health status
    """
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'dvoacap-dashboard'
    })


@app.route('/api/train', methods=['GET', 'POST'])
def train_model():
    """
    API endpoint for model training status

    Returns:
        JSON with training status
    """
    # For now, return a placeholder response
    # This can be expanded to handle actual model training
    return jsonify({
        'status': 'not_implemented',
        'message': 'Training endpoint placeholder',
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/status', methods=['GET'])
def get_status():
    """
    API endpoint to check generation status

    Returns:
        JSON with current state
    """
    return jsonify(generation_state)


@app.route('/api/data', methods=['GET'])
def get_prediction_data():
    """
    API endpoint to fetch current prediction data

    Returns:
        JSON prediction data
    """
    try:
        data_file = Path(__file__).parent / 'enhanced_predictions.json'
        if data_file.exists():
            with open(data_file, 'r') as f:
                data = json.load(f)
                # Extract predictions object from enhanced data structure
                predictions = data.get('predictions', data)
                return jsonify(predictions)
        else:
            return jsonify({'error': 'No prediction data available'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/station-config', methods=['GET', 'POST'])
def station_config():
    """
    API endpoint to get/set station configuration

    GET: Returns current station configuration
    POST: Saves new station configuration

    Returns:
        JSON with station configuration
    """
    config_file = Path(__file__).parent / 'station_config.json'

    if request.method == 'POST':
        try:
            config = request.get_json()
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return jsonify({'status': 'success', 'message': 'Station configuration saved'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    else:  # GET
        try:
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                return jsonify(config)
            else:
                # Return default configuration
                return jsonify({
                    'name': '',
                    'callsign': 'VE1ATM',
                    'grid': 'FN74ui',
                    'lat': 44.374,
                    'lon': -64.300,
                    'power': 100
                })
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.route('/api/antenna-config', methods=['GET', 'POST'])
def antenna_config():
    """
    API endpoint to get/set antenna configuration

    GET: Returns current antenna configuration and band assignments
    POST: Saves new antenna configuration

    Returns:
        JSON with antenna configuration
    """
    config_file = Path(__file__).parent / 'antenna_config.json'

    if request.method == 'POST':
        try:
            config = request.get_json()
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            return jsonify({'status': 'success', 'message': 'Antenna configuration saved'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    else:  # GET
        try:
            if config_file.exists():
                with open(config_file, 'r') as f:
                    config = json.load(f)
                return jsonify(config)
            else:
                # Return empty configuration
                return jsonify({
                    'antennas': [],
                    'band_assignments': {}
                })
        except Exception as e:
            return jsonify({'error': str(e)}), 500


@app.route('/api/debug/cache', methods=['GET'])
def debug_cache():
    """
    API endpoint to debug HTTP caching configuration

    Returns:
        JSON with current cache configuration and sample headers
    """
    # Create a sample response to show what headers would be sent
    sample_response = make_response("sample")
    sample_response = apply_cache_control(sample_response)

    return jsonify({
        'cache_enabled': not (server_config.get('disable_cache', False) or app.debug),
        'debug_mode': app.debug,
        'disable_cache_flag': server_config.get('disable_cache', False),
        'sample_headers': dict(sample_response.headers),
        'explanation': {
            '200': 'First request - Full content sent with ETag/Last-Modified headers',
            '304': 'Subsequent requests - Browser sends If-None-Match/If-Modified-Since, server responds with 304 if unchanged',
            'cache_control': sample_response.headers.get('Cache-Control', 'default')
        },
        'tips': {
            'disable_cache': 'Start server with --no-cache flag to disable caching',
            'debug_mode': 'Start server with --debug flag to auto-disable caching',
            'browser_refresh': 'Use Ctrl+Shift+R (Cmd+Shift+R on Mac) for hard refresh'
        }
    })


# =============================================================================
# Static File Serving
# =============================================================================

@app.route('/')
def index():
    """Serve the main dashboard"""
    response = make_response(send_from_directory('.', 'dashboard.html'))
    return apply_cache_control(response)


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    response = make_response(send_from_directory('.', path))
    return apply_cache_control(response)


# =============================================================================
# Main
# =============================================================================

def check_dependencies():
    """
    Check if required dependencies are installed
    Returns tuple: (success: bool, missing: list)
    """
    missing = []

    # Check core dependencies
    try:
        import numpy
    except ImportError:
        missing.append('numpy')

    try:
        import requests
    except ImportError:
        missing.append('requests')

    # Check if dvoacap module is importable
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from src.dvoacap.prediction_engine import PredictionEngine
    except ImportError as e:
        missing.append(f'dvoacap ({str(e)})')

    return len(missing) == 0, missing


def main():
    """Start the Flask server"""
    import argparse

    parser = argparse.ArgumentParser(description='VE1ATM Propagation Dashboard Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to (default: 8000)')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-cache', action='store_true', help='Disable HTTP caching (for development)')
    parser.add_argument('--skip-deps-check', action='store_true', help='Skip dependency check')

    args = parser.parse_args()

    # Configure caching
    if args.no_cache:
        server_config['disable_cache'] = True

    # Check dependencies unless skipped
    if not args.skip_deps_check:
        success, missing = check_dependencies()
        if not success:
            print("=" * 80)
            print("ERROR: Missing Dependencies")
            print("=" * 80)
            print("\nThe following required packages are not installed:")
            for dep in missing:
                print(f"  ✗ {dep}")
            print("\nTo fix this, run:")
            print("  pip install -e .[dashboard]")
            print("\nOr install individual packages:")
            print("  pip install numpy requests flask flask-cors")
            print("=" * 80)
            sys.exit(1)

    print("=" * 80)
    print("VE1ATM HF Propagation Dashboard Server")
    print("=" * 80)
    print(f"\n✓ Server starting on http://{args.host}:{args.port}")
    print(f"✓ Dashboard: http://{args.host}:{args.port}/")
    print(f"✓ Debug mode: {'Enabled' if args.debug else 'Disabled'}")
    print(f"✓ HTTP caching: {'Disabled' if server_config['disable_cache'] or args.debug else 'Enabled'}")
    print(f"✓ Press Ctrl+C to stop\n")
    print("=" * 80)

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
