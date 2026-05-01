#!/usr/bin/env python3
"""
PSKreporter Integration - Real-time Signal Reports
Fetches actual reception reports to validate propagation predictions
"""

import requests
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from pathlib import Path


class PSKReporterAPI:
    """
    Interface to PSKreporter API for real-time propagation validation
    """
    
    BASE_URL = "https://retrieve.pskreporter.info/query"
    
    def __init__(self, callsign: str):
        self.callsign = callsign.upper()
        
    def get_recent_spots(self, minutes: int = 60, band_mhz: Optional[float] = None) -> List[Dict]:
        """
        Get recent reception reports for your callsign
        
        Args:
            minutes: How many minutes back to look
            band_mhz: Optional frequency filter (e.g., 7.074 for 40m FT8)
            
        Returns:
            List of spots with receiver info, signal strength, frequency, time
        """
        
        # Calculate time range
        now = datetime.now(timezone.utc)
        flow_start = now - timedelta(minutes=minutes)
        
        params = {
            'senderCallsign': self.callsign,  # Correct parameter: who heard YOU
            'flowStartSeconds': int(flow_start.timestamp()),
            'rronly': 0,
            'noactive': 1
        }
        
        # Add frequency filter if specified
        if band_mhz:
            freq_hz = int(band_mhz * 1_000_000)
            # Allow 100kHz range around target frequency
            params['frange'] = f"{freq_hz-50000}-{freq_hz+50000}"
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=15)
            response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            
            # Process reception reports
            spots = []
            for report in root.findall('receptionReport'):
                spot = {
                    'receiver_call': report.get('receiverCallsign', 'Unknown'),
                    'receiver_grid': report.get('receiverLocator', 'Unknown'),
                    'receiver_country': report.get('receiverDXCC', 'Unknown'),
                    'frequency_mhz': float(report.get('frequency', 0)) / 1_000_000,
                    'snr': int(report.get('sNR', -99)) if report.get('sNR') else None,
                    'mode': report.get('mode', 'Unknown'),
                    'timestamp': datetime.fromtimestamp(
                        int(report.get('flowStartSeconds', 0)), 
                        tz=timezone.utc
                    ).isoformat()
                }
                spots.append(spot)
                    
            return spots
            
        except requests.exceptions.RequestException as e:
            print(f"PSKreporter API error: {e}")
            return []
        except ET.ParseError as e:
            print(f"XML parsing error: {e}")
            print(f"Response content: {response.content[:200]}")
            return []
        except Exception as e:
            print(f"Error processing PSKreporter data: {e}")
            return []
    
    def get_band_activity(self, minutes: int = 30) -> Dict[str, List[Dict]]:
        """
        Get reception reports organized by band
        
        Returns:
            Dict mapping band names to lists of spots
        """
        
        # Define band ranges in MHz
        bands = {
            '160m': (1.8, 2.0),
            '80m': (3.5, 4.0),
            '60m': (5.3, 5.4),
            '40m': (7.0, 7.3),
            '30m': (10.1, 10.15),
            '20m': (14.0, 14.35),
            '17m': (18.068, 18.168),
            '15m': (21.0, 21.45),
            '12m': (24.89, 24.99),
            '10m': (28.0, 29.7),
            '6m': (50.0, 54.0)
        }
        
        # Get all recent spots
        all_spots = self.get_recent_spots(minutes=minutes)
        
        # Organize by band
        band_spots = {band: [] for band in bands}
        
        for spot in all_spots:
            freq = spot['frequency_mhz']
            for band_name, (low, high) in bands.items():
                if low <= freq <= high:
                    band_spots[band_name].append(spot)
                    break
        
        # Remove empty bands
        band_spots = {k: v for k, v in band_spots.items() if v}
        
        return band_spots
    
    def analyze_coverage(self, minutes: int = 60) -> Dict:
        """
        Analyze geographic coverage from reception reports
        
        Returns:
            Dict with statistics about coverage
        """
        
        spots = self.get_recent_spots(minutes=minutes)
        
        if not spots:
            return {
                'total_spots': 0,
                'unique_receivers': 0,
                'countries': [],
                'bands': [],
                'average_snr': None
            }
        
        # Collect statistics
        unique_receivers = set(s['receiver_call'] for s in spots)
        countries = set(s['receiver_country'] for s in spots if s['receiver_country'] != 'Unknown')
        
        # Organize by band
        band_counts = {}
        snr_values = []
        
        for spot in spots:
            freq = spot['frequency_mhz']
            if freq >= 28.0:
                band = '10m'
            elif freq >= 24.89:
                band = '12m'
            elif freq >= 21.0:
                band = '15m'
            elif freq >= 18.068:
                band = '17m'
            elif freq >= 14.0:
                band = '20m'
            elif freq >= 10.1:
                band = '30m'
            elif freq >= 7.0:
                band = '40m'
            elif freq >= 5.3:
                band = '60m'
            elif freq >= 3.5:
                band = '80m'
            elif freq >= 1.8:
                band = '160m'
            else:
                band = 'Other'
            
            band_counts[band] = band_counts.get(band, 0) + 1
            
            if spot['snr'] is not None:
                snr_values.append(spot['snr'])
        
        avg_snr = sum(snr_values) / len(snr_values) if snr_values else None
        
        return {
            'total_spots': len(spots),
            'unique_receivers': len(unique_receivers),
            'countries': sorted(list(countries)),
            'bands': sorted(band_counts.items(), key=lambda x: x[1], reverse=True),
            'average_snr': round(avg_snr, 1) if avg_snr else None,
            'time_range_minutes': minutes
        }


def main():
    """Test PSKreporter integration"""
    
    print("PSKreporter Integration Test")
    print("=" * 60)
    
    # VE1ATM
    callsign = "VE1ATM"
    
    psk = PSKReporterAPI(callsign)
    
    print(f"Checking recent activity for {callsign}...")
    print()
    
    # Get coverage analysis
    coverage = psk.analyze_coverage(minutes=60)
    
    print("Coverage Analysis (Last 60 minutes):")
    print(f"  Total spots: {coverage['total_spots']}")
    print(f"  Unique receivers: {coverage['unique_receivers']}")
    print(f"  Countries: {len(coverage['countries'])}")
    if coverage['countries']:
        print(f"    {', '.join(coverage['countries'][:10])}")
        if len(coverage['countries']) > 10:
            print(f"    ...and {len(coverage['countries']) - 10} more")
    print(f"  Average SNR: {coverage['average_snr']} dB" if coverage['average_snr'] else "  Average SNR: N/A")
    print()
    
    if coverage['bands']:
        print("Band Activity:")
        for band, count in coverage['bands']:
            print(f"  {band}: {count} spots")
        print()
    
    # Get detailed spots for most active band
    if coverage['bands']:
        most_active_band = coverage['bands'][0][0]
        print(f"Recent spots on {most_active_band}:")
        
        band_activity = psk.get_band_activity(minutes=30)
        if most_active_band in band_activity:
            spots = band_activity[most_active_band][:10]  # Show first 10
            for spot in spots:
                time_str = spot['timestamp'].split('T')[1][:8]
                print(f"  {time_str} - {spot['receiver_call']} ({spot['receiver_grid']}) " 
                      f"SNR: {spot['snr']}dB {spot['frequency_mhz']:.3f}MHz")
    
    # Save detailed data
    output_file = Path('pskreporter_data.json')
    output = {
        'callsign': callsign,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'coverage': coverage,
        'band_activity': psk.get_band_activity(minutes=60)
    }
    
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    print()
    print(f"Detailed data saved to: {output_file}")
    

if __name__ == '__main__':
    main()
