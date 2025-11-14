#!/usr/bin/env python3
"""
Proppy.net API Integration - Professional VOACAP Predictions
Uses the proppy.net web service by G4FUI for accurate HF propagation predictions

⚠️ DEPRECATED - This module is no longer functional ⚠️

As of 2025, proppy.net is no longer operational (domain for sale).
This code is preserved for reference only.

Alternative VOACAP services:
- voacap.com - Active but prohibits automated API access without permission
- soundbytes.asia/proppy/ - Active web interface (ITU P.533-14), no documented API
- Local VOACAP engines - Use DVOACAP-Python local prediction engine instead

This repository already has a fully functional local VOACAP engine.
See validate_predictions.py for local engine validation.
"""

import requests
import json
import time
from datetime import datetime, timezone
from typing import Dict, Optional, List
from pathlib import Path


class ProppyNetAPI:
    """
    Interface to proppy.net web service for VOACAP predictions
    
    proppy.net provides professional-grade HF propagation predictions
    using the VOACAP engine via a web API.
    """
    
    BASE_URL = "https://www.proppy.net/cgi-bin/postFile.py"
    
    def __init__(self, tx_lat: float, tx_lon: float, tx_power: int = 100):
        """
        Initialize proppy.net API client
        
        Args:
            tx_lat: Transmitter latitude
            tx_lon: Transmitter longitude  
            tx_power: Transmit power in watts (default 100W)
        """
        self.tx_lat = tx_lat
        self.tx_lon = tx_lon
        self.tx_power = tx_power
        
    def get_prediction(self, 
                      rx_lat: float, 
                      rx_lon: float,
                      freq_mhz: float,
                      hour_utc: int,
                      month: int,
                      ssn: int = 100) -> Optional[Dict]:
        """
        Get VOACAP prediction for a specific path
        
        Args:
            rx_lat: Receiver latitude
            rx_lon: Receiver longitude
            freq_mhz: Frequency in MHz
            hour_utc: Hour in UTC (0-23)
            month: Month (1-12)
            ssn: Sunspot number (default 100)
            
        Returns:
            Dict with prediction results or None on error
        """
        
        try:
            # Build VOA area file format for proppy.net
            voa_file = self._build_voa_file(
                rx_lat, rx_lon, freq_mhz, hour_utc, month, ssn
            )
            
            # Submit to proppy.net
            response = requests.post(
                self.BASE_URL,
                files={'file': ('prediction.voa', voa_file, 'text/plain')},
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"Proppy.net API error: HTTP {response.status_code}")
                return None
            
            # Parse response
            result = self._parse_proppy_response(response.text)
            
            return result
            
        except requests.exceptions.Timeout:
            print("Proppy.net API timeout - service may be busy")
            return None
        except Exception as e:
            print(f"Proppy.net prediction error: {e}")
            return None
    
    def _build_voa_file(self, rx_lat: float, rx_lon: float, 
                       freq_mhz: float, hour_utc: int, 
                       month: int, ssn: int) -> str:
        """
        Build VOACAP VOA file format for proppy.net
        
        This is a simplified P2P (point-to-point) prediction file
        """
        
        voa_content = f"""LINEMAX 0
COEFFS CCIR
TIME {hour_utc} 1 {hour_utc}
MONTH {month} {month}
SUNSPOT {ssn}
LABEL VE1ATM Propagation Prediction
TRANSMIT POWER {self.tx_power}
TXLOCATION {self.tx_lat:.2f} {self.tx_lon:.2f}
ANTENNA ISOTROPIC
RXLOCATION {rx_lat:.2f} {rx_lon:.2f}
FREQUENCY {freq_mhz:.3f} {freq_mhz:.3f} 1
SYSTEM 145 3.0 90 0.1 0.1
FPROB 1 1 1
METHOD 30
EXECUTE
QUIT
"""
        return voa_content.strip()
    
    def _parse_proppy_response(self, response_text: str) -> Dict:
        """
        Parse proppy.net response
        
        proppy.net returns predictions in a structured format
        We extract key metrics: reliability, SNR, MUF
        """
        
        result = {
            'method': 'VOACAP',
            'reliability': 0,
            'snr_db': -999,
            'muf': 0,
            'raw_response': response_text[:500]  # Keep sample for debugging
        }
        
        try:
            # proppy.net returns predictions in various formats
            # For basic P2P predictions, we look for key values
            
            lines = response_text.split('\n')
            
            for line in lines:
                line = line.strip()
                
                # Look for reliability percentage
                if 'REL' in line or 'RELIABILITY' in line:
                    # Extract percentage value
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part.replace('.', '').isdigit():
                            try:
                                rel = float(part)
                                if 0 <= rel <= 100:
                                    result['reliability'] = int(rel)
                            except ValueError:
                                pass
                
                # Look for SNR or S/N ratio
                if 'SNR' in line or 'S/N' in line or 'SIGNAL' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        try:
                            val = float(part.replace('dB', '').strip())
                            if -50 < val < 50:  # Reasonable SNR range
                                result['snr_db'] = round(val, 1)
                        except ValueError:
                            pass
                
                # Look for MUF
                if 'MUF' in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        try:
                            val = float(part)
                            if 1 < val < 50:  # Reasonable MUF range in MHz
                                result['muf'] = round(val, 1)
                        except ValueError:
                            pass
            
            # Determine quality based on reliability
            if result['reliability'] >= 70:
                result['quality'] = 'GOOD'
            elif result['reliability'] >= 40:
                result['quality'] = 'FAIR'
            else:
                result['quality'] = 'POOR'
                
        except Exception as e:
            print(f"Error parsing proppy.net response: {e}")
        
        return result
    
    def predict_multiple_bands(self,
                              rx_lat: float,
                              rx_lon: float,
                              band_freqs: Dict[str, float],
                              ssn: int = 100) -> Dict[str, Dict]:
        """
        Get predictions for multiple bands
        
        Args:
            rx_lat: Receiver latitude
            rx_lon: Receiver longitude
            band_freqs: Dict of band_name -> frequency_mhz
            ssn: Sunspot number
            
        Returns:
            Dict of band_name -> prediction results
        """
        
        current_hour = datetime.now(timezone.utc).hour
        current_month = datetime.now(timezone.utc).month
        
        results = {}
        
        for band_name, freq_mhz in band_freqs.items():
            print(f"  Fetching VOACAP prediction for {band_name}...", end='', flush=True)
            
            prediction = self.get_prediction(
                rx_lat=rx_lat,
                rx_lon=rx_lon,
                freq_mhz=freq_mhz,
                hour_utc=current_hour,
                month=current_month,
                ssn=ssn
            )
            
            if prediction:
                results[band_name] = prediction
                print(f" {prediction['reliability']}% {prediction['quality']}")
            else:
                print(" FAILED")
            
            # Rate limiting - be nice to proppy.net
            time.sleep(2)
        
        return results


def test_proppy_api():
    """Test proppy.net API integration"""
    
    print("Proppy.net VOACAP API Test")
    print("=" * 60)
    
    # VE1ATM location
    api = ProppyNetAPI(tx_lat=44.376, tx_lon=-64.317, tx_power=100)
    
    # Test prediction to UK (London)
    print("\nTesting prediction: VE1ATM -> UK (London)")
    print("  Path: ~4500 km across Atlantic")
    print("  Band: 20m (14.15 MHz)")
    print()
    
    result = api.get_prediction(
        rx_lat=51.5,
        rx_lon=-0.1,
        freq_mhz=14.15,
        hour_utc=datetime.now(timezone.utc).hour,
        month=datetime.now(timezone.utc).month,
        ssn=100
    )
    
    if result:
        print("✓ Proppy.net API working!")
        print(f"  Reliability: {result['reliability']}%")
        print(f"  SNR: {result['snr_db']} dB")
        print(f"  MUF: {result['muf']} MHz")
        print(f"  Quality: {result['quality']}")
        print(f"  Method: {result['method']}")
    else:
        print("✗ Proppy.net API failed")
        print("  This may be due to:")
        print("    - Internet connectivity")
        print("    - Proppy.net service unavailable")
        print("    - Rate limiting")
    
    print()
    print("=" * 60)
    

if __name__ == '__main__':
    test_proppy_api()
