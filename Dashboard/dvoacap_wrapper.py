#!/usr/bin/env python3
"""
DVOACAP Python Wrapper - Corrected Version
Calls the dvoa.dll with the EXACT format it expects
Based on reverse-engineered API structure
"""

import json
import ctypes
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class DVOACAPEngine:
    """Python wrapper for DVOACAP DLL"""
    
    def __init__(self, dll_path: str = "./dvoa.dll"):
        """Initialize the DVOACAP engine
        
        Args:
            dll_path: Path to dvoa.dll file
        """
        dll_file = Path(dll_path)
        if not dll_file.exists():
            raise FileNotFoundError(f"DVOACAP DLL not found at: {dll_path}")
        
        # Load the DLL
        self.dll = ctypes.WinDLL(str(dll_file))
        
        # Define the Predict function signature
        # extern "C" {char* __declspec(dllexport) __stdcall Predict(char* ArgsStr);}
        self.dll.Predict.argtypes = [ctypes.c_char_p]
        self.dll.Predict.restype = ctypes.c_char_p
        
        print(f"✓ DVOACAP engine loaded from {dll_path}")
    
    def predict(self, 
                tx_lat: float, tx_lon: float,
                rx_locations: List[Dict],  # Changed to list of RX locations
                frequencies: List[float],  # Changed to list of frequencies
                hours: Dict,  # Changed to hours object
                ssn: int = None,
                month: int = None,
                include_muf: bool = True,
                **kwargs) -> Dict:
        """Run VOACAP prediction with EXACT API format
        
        Args:
            tx_lat: Transmitter latitude
            tx_lon: Transmitter longitude
            rx_locations: List of receiver locations [{"Lat": 44.90, "Lon": 20.50, "Label": "CITY"}]
            frequencies: List of frequencies in MHz [7.2, 14.15, 21.2]
            hours: Hours object {"Start": 1, "Step": 1, "Count": 24}
            ssn: Smoothed sunspot number (optional)
            month: Month (1-12), defaults to current month
            include_muf: Include MUF in results
            
        Returns:
            Dictionary with prediction results
        """
        if month is None:
            month = datetime.now().month
        
        # Build DVOACAP JSON input in EXACT format expected
        input_data = {
            "Arguments": {
                "RxLocations": rx_locations,
                "Hours": hours,
                "Freqs": frequencies,
                "IncludeMuf": include_muf
            }
        }
        
        # Add optional parameters if provided
        if ssn is not None:
            input_data["Arguments"]["SSN"] = ssn
        if month is not None:
            input_data["Arguments"]["Month"] = month
        
        # Convert to JSON string
        input_json = json.dumps(input_data)
        
        # Call the DLL
        try:
            result_bytes = self.dll.Predict(input_json.encode('utf-8'))
            result_json = result_bytes.decode('utf-8')
            
            # Parse the result
            result = json.loads(result_json)
            return result
            
        except Exception as e:
            print(f"✗ DVOACAP prediction error: {e}")
            return None
    
    def predict_simple(self,
                      tx_lat: float, tx_lon: float,
                      rx_lat: float, rx_lon: float,
                      frequency_mhz: float,
                      hour_utc: int,
                      ssn: int,
                      rx_label: str = "RX") -> Dict:
        """Simplified prediction for a single path/frequency/hour
        
        Args:
            tx_lat: Transmitter latitude
            tx_lon: Transmitter longitude
            rx_lat: Receiver latitude
            rx_lon: Receiver longitude
            frequency_mhz: Single frequency in MHz
            hour_utc: Single UTC hour (0-23)
            ssn: Smoothed sunspot number
            rx_label: Label for receiver location
            
        Returns:
            {
                'reliability': int (0-100),
                'snr_db': float,
                'quality': str (GOOD/FAIR/POOR),
                'muf': float,
                'method': 'VOACAP'
            }
        """
        # Format parameters for the API
        rx_locations = [{
            "Lat": rx_lat,
            "Lon": rx_lon,
            "Label": rx_label
        }]
        
        hours = {
            "Start": hour_utc,
            "Step": 1,
            "Count": 1
        }
        
        frequencies = [frequency_mhz]
        
        result = self.predict(
            tx_lat=tx_lat,
            tx_lon=tx_lon,
            rx_locations=rx_locations,
            frequencies=frequencies,
            hours=hours,
            ssn=ssn
        )
        
        if not result:
            return {
                'reliability': 0,
                'snr_db': -99,
                'quality': 'POOR',
                'muf': 0,
                'method': 'VOACAP-ERROR'
            }
        
        # Extract key metrics from DVOACAP result
        # (Format depends on actual DVOACAP output - need to adjust after testing)
        try:
            # Navigate the result structure (adjust based on actual format)
            reliability = result.get('Reliability', 0)
            snr = result.get('SNR', -99)
            muf = result.get('MUF', 0)
            
            # Determine quality
            if reliability >= 70:
                quality = 'GOOD'
            elif reliability >= 40:
                quality = 'FAIR'
            else:
                quality = 'POOR'
            
            return {
                'reliability': reliability,
                'snr_db': snr,
                'quality': quality,
                'muf': muf,
                'method': 'VOACAP'
            }
        except Exception as e:
            print(f"✗ Error parsing DVOACAP result: {e}")
            print(f"  Raw result: {json.dumps(result, indent=2)}")
            return {
                'reliability': 0,
                'snr_db': -99,
                'quality': 'ERROR',
                'muf': 0,
                'method': 'VOACAP-PARSE-ERROR'
            }
    
    def predict_multi_band(self,
                          tx_lat: float, tx_lon: float,
                          rx_lat: float, rx_lon: float,
                          rx_label: str = "RX",
                          ssn: int = 140) -> Dict:
        """Predict across all HF bands for 24 hours
        
        Returns predictions for common HF bands throughout the day
        """
        # Common HF amateur frequencies
        frequencies = [
            1.85,   # 160m
            3.65,   # 80m
            7.10,   # 40m
            10.13,  # 30m
            14.15,  # 20m
            18.10,  # 17m
            21.20,  # 15m
            24.95,  # 12m
            28.40   # 10m
        ]
        
        rx_locations = [{
            "Lat": rx_lat,
            "Lon": rx_lon,
            "Label": rx_label
        }]
        
        hours = {
            "Start": 0,
            "Step": 1,
            "Count": 24
        }
        
        return self.predict(
            tx_lat=tx_lat,
            tx_lon=tx_lon,
            rx_locations=rx_locations,
            frequencies=frequencies,
            hours=hours,
            ssn=ssn,
            include_muf=True
        )


def test_dvoacap():
    """Test the DVOACAP wrapper"""
    print("Testing DVOACAP Engine (Corrected Version)...")
    print("=" * 60)
    
    try:
        # Initialize engine
        engine = DVOACAPEngine("dvoa.dll")
        
        # Test 1: Simple single prediction
        print("\n[TEST 1] Single path/frequency/hour")
        print("  Path: VE1ATM -> Belgrade")
        print("  Frequency: 14.15 MHz (20m)")
        print("  Hour: 18:00 UTC")
        print("  SSN: 140")
        
        result = engine.predict_simple(
            tx_lat=44.374, tx_lon=-64.300,  # Halifax
            rx_lat=44.90, rx_lon=20.50,     # Belgrade
            frequency_mhz=14.15,
            hour_utc=18,
            ssn=140,
            rx_label="BELGRADE"
        )
        
        print(f"\n  Result:")
        print(f"    Method: {result['method']}")
        print(f"    Quality: {result['quality']}")
        print(f"    Reliability: {result['reliability']}%")
        print(f"    SNR: {result['snr_db']} dB")
        print(f"    MUF: {result['muf']} MHz")
        
        # Test 2: Multi-band 24-hour prediction
        print("\n[TEST 2] Multi-band 24-hour prediction")
        print("  Path: VE1ATM -> Belgrade")
        print("  Bands: All HF (160m-10m)")
        print("  Hours: 0-23 UTC")
        
        result_full = engine.predict_multi_band(
            tx_lat=44.374, tx_lon=-64.300,
            rx_lat=44.90, rx_lon=20.50,
            rx_label="BELGRADE",
            ssn=140
        )
        
        if result_full:
            print(f"\n  ✓ Received full prediction data")
            print(f"  Result structure: {list(result_full.keys())}")
        
        print("\n✓ Tests complete!")
        
    except FileNotFoundError as e:
        print(f"\n✗ {e}")
        print("\n  To fix:")
        print("    1. Download DVOACAP from: https://github.com/VE3NEA/DVOACAP")
        print("    2. Extract dvoa.dll to the same folder as this script")
        print("    3. Run this test again")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    test_dvoacap()
