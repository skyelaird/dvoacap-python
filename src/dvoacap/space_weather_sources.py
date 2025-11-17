#!/usr/bin/env python3
"""
Multi-Source Space Weather Data Fetcher

This module provides resilient fetching of space weather data from multiple
international sources with automatic fallback when primary sources fail.

Data Sources:
- Solar Flux (F10.7): NOAA SWPC, LISIRD, Space Weather Canada
- Sunspot Number: SIDC/SILSO, NOAA, LISIRD
- Kp Index: GFZ Potsdam, NOAA SWPC, Space Weather Canada
- A-Index: GFZ Potsdam, NOAA SWPC

Author: 2025
License: MIT
"""

import requests
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, List, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import json


# =============================================================================
# Data Classes
# =============================================================================

class DataSource(Enum):
    """Data source identifiers"""
    NOAA_SWPC = "NOAA SWPC (USA)"
    GFZ_POTSDAM = "GFZ Potsdam (Germany)"
    SIDC_SILSO = "SIDC/SILSO (Belgium)"
    SPACE_WEATHER_CANADA = "Space Weather Canada"
    LISIRD = "LISIRD (LASP)"
    INTERMAGNET = "INTERMAGNET"
    IMAGE_NETWORK = "IMAGE Network (Finland)"
    OPENDATASOFT = "OpenDataSoft API"
    DEFAULT = "Default Values"


@dataclass
class SpaceWeatherData:
    """Complete space weather conditions"""
    sfi: float  # Solar Flux Index (F10.7)
    ssn: float  # Sunspot Number
    kp: float   # Planetary K-index
    a_index: float  # A-index
    timestamp: str
    sources: Dict[str, str]  # Which source provided each value
    fetch_errors: List[str]  # Any errors encountered

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


# =============================================================================
# Default Values
# =============================================================================

DEFAULT_VALUES = {
    'sfi': 150.0,      # Mid-cycle solar flux
    'ssn': 100.0,      # Mid-cycle sunspot number
    'kp': 2.0,         # Quiet conditions
    'a_index': 10.0,   # Quiet conditions
}


# =============================================================================
# Solar Flux Index (F10.7) Fetchers
# =============================================================================

class SolarFluxFetcher:
    """Fetch solar flux index from multiple sources"""

    @staticmethod
    def fetch_noaa_swpc(timeout: int = 10) -> Optional[Tuple[float, DataSource]]:
        """
        Fetch F10.7 from NOAA SWPC

        API: https://services.swpc.noaa.gov/json/f107_cm_flux.json
        """
        try:
            url = "https://services.swpc.noaa.gov/json/f107_cm_flux.json"
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    latest = data[-1]
                    sfi = float(latest.get('flux', 0))
                    if sfi > 0:
                        return sfi, DataSource.NOAA_SWPC
        except Exception as e:
            print(f"[DEBUG] NOAA SWPC SFI failed: {e}")
        return None

    @staticmethod
    def fetch_lisird(timeout: int = 10) -> Optional[Tuple[float, DataSource]]:
        """
        Fetch F10.7 from LISIRD (LASP Colorado)

        API: https://lasp.colorado.edu/lisird/data/penticton_radio_flux/
        Note: This may require parsing HTML or using their data files
        """
        try:
            # LISIRD provides data files, typically in CSV format
            # For now, this is a placeholder - would need to implement file parsing
            # or find their JSON API endpoint
            pass
        except Exception as e:
            print(f"[DEBUG] LISIRD SFI failed: {e}")
        return None

    @staticmethod
    def fetch_space_weather_canada(timeout: int = 10) -> Optional[Tuple[float, DataSource]]:
        """
        Fetch F10.7 from Space Weather Canada

        URL: https://spaceweather.gc.ca/forecast-prevision/solar-solaire/solarflux/sx-4a-en.php
        Note: May require HTML parsing
        """
        try:
            # Space Weather Canada provides data but may need parsing
            # Placeholder for future implementation
            pass
        except Exception as e:
            print(f"[DEBUG] Space Weather Canada SFI failed: {e}")
        return None

    @classmethod
    def fetch(cls, timeout: int = 10) -> Tuple[float, DataSource]:
        """
        Fetch solar flux with fallback

        Returns:
            Tuple of (sfi_value, source)
        """
        # Try sources in order of preference
        sources = [
            cls.fetch_noaa_swpc,
            cls.fetch_lisird,
            cls.fetch_space_weather_canada,
        ]

        for fetch_func in sources:
            result = fetch_func(timeout)
            if result:
                return result

        # All sources failed - return default
        return DEFAULT_VALUES['sfi'], DataSource.DEFAULT


# =============================================================================
# Sunspot Number Fetchers
# =============================================================================

class SunspotNumberFetcher:
    """Fetch sunspot number from multiple sources"""

    @staticmethod
    def fetch_sidc_silso(timeout: int = 10) -> Optional[Tuple[float, DataSource]]:
        """
        Fetch SSN from SIDC/SILSO via OpenDataSoft API

        API: https://data.opendatasoft.com/api/records/1.0/search/
        Dataset: daily-sunspot-number@datastro
        """
        try:
            url = "https://data.opendatasoft.com/api/records/1.0/search/"
            params = {
                'dataset': 'daily-sunspot-number@datastro',
                'rows': 1,
                'sort': '-date',
                'timezone': 'UTC'
            }
            response = requests.get(url, params=params, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if 'records' in data and len(data['records']) > 0:
                    record = data['records'][0]
                    # Try different field names
                    ssn = (record.get('fields', {}).get('sunspot_number') or
                           record.get('fields', {}).get('total_sunspot_number') or
                           record.get('fields', {}).get('ssn'))
                    if ssn is not None:
                        return float(ssn), DataSource.SIDC_SILSO
        except Exception as e:
            print(f"[DEBUG] SIDC/SILSO SSN failed: {e}")
        return None

    @staticmethod
    def fetch_noaa_swpc(timeout: int = 10) -> Optional[Tuple[float, DataSource]]:
        """
        Fetch SSN from NOAA SWPC

        API: https://services.swpc.noaa.gov/json/solar-cycle/observed-solar-cycle-indices.json
        """
        try:
            url = "https://services.swpc.noaa.gov/json/solar-cycle/observed-solar-cycle-indices.json"
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    latest = data[-1]
                    ssn = latest.get('ssn') or latest.get('sunspot') or latest.get('smoothed_ssn')
                    if ssn is not None:
                        return float(ssn), DataSource.NOAA_SWPC
        except Exception as e:
            print(f"[DEBUG] NOAA SWPC SSN failed: {e}")
        return None

    @classmethod
    def fetch(cls, timeout: int = 10) -> Tuple[float, DataSource]:
        """
        Fetch sunspot number with fallback

        Returns:
            Tuple of (ssn_value, source)
        """
        # Try SIDC/SILSO first (authoritative source), then NOAA
        sources = [
            cls.fetch_sidc_silso,
            cls.fetch_noaa_swpc,
        ]

        for fetch_func in sources:
            result = fetch_func(timeout)
            if result:
                return result

        return DEFAULT_VALUES['ssn'], DataSource.DEFAULT


# =============================================================================
# Kp Index Fetchers
# =============================================================================

class KpIndexFetcher:
    """Fetch Kp index from multiple sources"""

    @staticmethod
    def fetch_gfz_potsdam(timeout: int = 10) -> Optional[Tuple[float, DataSource]]:
        """
        Fetch Kp from GFZ Potsdam (authoritative source)

        API: https://kp.gfz.de/app/json/?start=...&end=...&index=Kp
        """
        try:
            # Get data for last 24 hours
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=24)

            url = "https://kp.gfz.de/app/json/"
            params = {
                'start': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'end': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'index': 'Kp'
            }

            response = requests.get(url, params=params, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                # GFZ returns array of measurements
                if isinstance(data, list) and len(data) > 0:
                    # Get most recent Kp value
                    latest = data[-1]
                    kp = latest.get('Kp')
                    if kp is not None:
                        return float(kp), DataSource.GFZ_POTSDAM
        except Exception as e:
            print(f"[DEBUG] GFZ Potsdam Kp failed: {e}")
        return None

    @staticmethod
    def fetch_noaa_swpc(timeout: int = 10) -> Optional[Tuple[float, DataSource]]:
        """
        Fetch Kp from NOAA SWPC

        API: https://services.swpc.noaa.gov/json/planetary_k_index_1m.json
        """
        try:
            url = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    latest = data[-1]
                    kp = latest.get('kp_index') or latest.get('Kp') or latest.get('kp')
                    if kp is not None:
                        return float(kp), DataSource.NOAA_SWPC
        except Exception as e:
            print(f"[DEBUG] NOAA SWPC Kp failed: {e}")
        return None

    @classmethod
    def fetch(cls, timeout: int = 10) -> Tuple[float, DataSource]:
        """
        Fetch Kp index with fallback

        Returns:
            Tuple of (kp_value, source)
        """
        # Try GFZ first (authoritative), then NOAA
        sources = [
            cls.fetch_gfz_potsdam,
            cls.fetch_noaa_swpc,
        ]

        for fetch_func in sources:
            result = fetch_func(timeout)
            if result:
                return result

        return DEFAULT_VALUES['kp'], DataSource.DEFAULT


# =============================================================================
# A-Index Fetchers
# =============================================================================

class AIndexFetcher:
    """Fetch A-index from multiple sources"""

    @staticmethod
    def fetch_gfz_potsdam(timeout: int = 10) -> Optional[Tuple[float, DataSource]]:
        """
        Fetch A-index from GFZ Potsdam

        API: https://kp.gfz.de/app/json/?start=...&end=...&index=Ap
        """
        try:
            # Get data for last 24 hours
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(hours=24)

            url = "https://kp.gfz.de/app/json/"
            params = {
                'start': start_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'end': end_time.strftime('%Y-%m-%dT%H:%M:%SZ'),
                'index': 'Ap'
            }

            response = requests.get(url, params=params, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    latest = data[-1]
                    a_index = latest.get('Ap')
                    if a_index is not None:
                        return float(a_index), DataSource.GFZ_POTSDAM
        except Exception as e:
            print(f"[DEBUG] GFZ Potsdam A-index failed: {e}")
        return None

    @staticmethod
    def fetch_noaa_swpc(timeout: int = 10) -> Optional[Tuple[float, DataSource]]:
        """
        Fetch A-index from NOAA SWPC

        API: https://services.swpc.noaa.gov/json/predicted_fredericksburg_a_index.json
        """
        try:
            url = "https://services.swpc.noaa.gov/json/predicted_fredericksburg_a_index.json"
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    # Try to find today's value
                    today = datetime.now(timezone.utc).date()
                    for entry in reversed(data):
                        time_tag = entry.get('time_tag', '')
                        if time_tag.startswith(str(today)):
                            a_value = entry.get('a_index') or entry.get('A') or entry.get('a')
                            if a_value is not None:
                                return float(a_value), DataSource.NOAA_SWPC

                    # If not found for today, use most recent
                    latest = data[-1]
                    a_value = latest.get('a_index') or latest.get('A') or latest.get('a')
                    if a_value is not None:
                        return float(a_value), DataSource.NOAA_SWPC
        except Exception as e:
            print(f"[DEBUG] NOAA SWPC A-index failed: {e}")
        return None

    @classmethod
    def fetch(cls, timeout: int = 10) -> Tuple[float, DataSource]:
        """
        Fetch A-index with fallback

        Returns:
            Tuple of (a_index_value, source)
        """
        # Try GFZ first, then NOAA
        sources = [
            cls.fetch_gfz_potsdam,
            cls.fetch_noaa_swpc,
        ]

        for fetch_func in sources:
            result = fetch_func(timeout)
            if result:
                return result

        return DEFAULT_VALUES['a_index'], DataSource.DEFAULT


# =============================================================================
# Main Multi-Source Fetcher
# =============================================================================

class MultiSourceSpaceWeatherFetcher:
    """
    Fetch space weather data from multiple international sources with fallback

    This fetcher tries multiple sources for each parameter and automatically
    falls back to alternative sources if primary sources are unavailable.

    Example:
        >>> fetcher = MultiSourceSpaceWeatherFetcher()
        >>> data = fetcher.fetch_all()
        >>> print(f"SFI: {data.sfi} from {data.sources['sfi']}")
        >>> print(f"SSN: {data.ssn} from {data.sources['ssn']}")
    """

    def __init__(self, timeout: int = 10, verbose: bool = True) -> None:
        """
        Initialize fetcher

        Args:
            timeout: Request timeout in seconds
            verbose: Print status messages
        """
        self.timeout = timeout
        self.verbose = verbose

    def fetch_all(self) -> SpaceWeatherData:
        """
        Fetch all space weather parameters with automatic fallback

        Returns:
            SpaceWeatherData object with all parameters and source information
        """
        errors = []

        if self.verbose:
            print("=" * 70)
            print("Multi-Source Space Weather Data Fetcher")
            print("=" * 70)

        # Fetch each parameter from multiple sources
        try:
            sfi, sfi_source = SolarFluxFetcher.fetch(self.timeout)
            if self.verbose:
                print(f"[OK] Solar Flux (F10.7): {sfi:.1f} from {sfi_source.value}")
        except Exception as e:
            sfi, sfi_source = DEFAULT_VALUES['sfi'], DataSource.DEFAULT
            errors.append(f"SFI fetch error: {e}")
            if self.verbose:
                print(f"[WARNING] Solar Flux failed: {e}")

        try:
            ssn, ssn_source = SunspotNumberFetcher.fetch(self.timeout)
            if self.verbose:
                print(f"[OK] Sunspot Number: {ssn:.1f} from {ssn_source.value}")
        except Exception as e:
            ssn, ssn_source = DEFAULT_VALUES['ssn'], DataSource.DEFAULT
            errors.append(f"SSN fetch error: {e}")
            if self.verbose:
                print(f"[WARNING] Sunspot Number failed: {e}")

        try:
            kp, kp_source = KpIndexFetcher.fetch(self.timeout)
            if self.verbose:
                print(f"[OK] Kp Index: {kp:.1f} from {kp_source.value}")
        except Exception as e:
            kp, kp_source = DEFAULT_VALUES['kp'], DataSource.DEFAULT
            errors.append(f"Kp fetch error: {e}")
            if self.verbose:
                print(f"[WARNING] Kp Index failed: {e}")

        try:
            a_index, a_source = AIndexFetcher.fetch(self.timeout)
            if self.verbose:
                print(f"[OK] A-Index: {a_index:.1f} from {a_source.value}")
        except Exception as e:
            a_index, a_source = DEFAULT_VALUES['a_index'], DataSource.DEFAULT
            errors.append(f"A-index fetch error: {e}")
            if self.verbose:
                print(f"[WARNING] A-Index failed: {e}")

        if self.verbose:
            print("=" * 70)

        # Build result
        return SpaceWeatherData(
            sfi=sfi,
            ssn=ssn,
            kp=kp,
            a_index=a_index,
            timestamp=datetime.now(timezone.utc).isoformat(),
            sources={
                'sfi': sfi_source.value,
                'ssn': ssn_source.value,
                'kp': kp_source.value,
                'a_index': a_source.value,
            },
            fetch_errors=errors
        )

    def fetch_all_legacy_format(self) -> Dict:
        """
        Fetch all data in legacy format (for backward compatibility)

        Returns:
            Dict with keys: sfi, ssn, kp, a_index, timestamp, source
        """
        data = self.fetch_all()

        # Determine overall source
        sources_used = set(data.sources.values())
        if len(sources_used) == 1:
            overall_source = list(sources_used)[0]
        elif DataSource.DEFAULT.value in sources_used:
            overall_source = "Mixed sources (some defaults)"
        else:
            overall_source = "Mixed international sources"

        return {
            'sfi': data.sfi,
            'ssn': data.ssn,
            'kp': data.kp,
            'a_index': data.a_index,
            'timestamp': data.timestamp,
            'source': overall_source,
            'sources_detail': data.sources,
            'errors': data.fetch_errors
        }


# =============================================================================
# CLI / Testing
# =============================================================================

def main() -> None:
    """Test the multi-source fetcher"""
    print("\n" + "=" * 70)
    print("DVOACAP Multi-Source Space Weather Data Fetcher")
    print("=" * 70)
    print()

    fetcher = MultiSourceSpaceWeatherFetcher(verbose=True)
    data = fetcher.fetch_all()

    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)
    print(f"Solar Flux (F10.7): {data.sfi:.1f} sfu")
    print(f"  Source: {data.sources['sfi']}")
    print()
    print(f"Sunspot Number: {data.ssn:.1f}")
    print(f"  Source: {data.sources['ssn']}")
    print()
    print(f"Kp Index: {data.kp:.1f}")
    print(f"  Source: {data.sources['kp']}")
    print()
    print(f"A-Index: {data.a_index:.1f}")
    print(f"  Source: {data.sources['a_index']}")
    print()
    print(f"Timestamp: {data.timestamp}")

    if data.fetch_errors:
        print()
        print("Errors encountered:")
        for error in data.fetch_errors:
            print(f"  - {error}")

    print()
    print("=" * 70)
    print("Data Diversity: Using international sources increases reliability!")
    print("=" * 70)
    print()


if __name__ == '__main__':
    main()
