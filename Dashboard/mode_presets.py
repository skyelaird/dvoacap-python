"""
Mode Presets for DVOACAP Predictions

Provides standard configurations for common amateur radio modes matching
VOACAP reference parameters.
"""

# Mode-specific parameters matching VOACAP specifications
MODE_PRESETS = {
    'WSPR': {
        'name': 'WSPR',
        'bandwidth_hz': 6,  # 6 Hz
        'bandwidth_db_hz': 3,  # VOACAP uses 3 dB/Hz for WSPR
        'required_snr': -28,  # dB
        'description': 'Weak Signal Propagation Reporter'
    },
    'FT8': {
        'name': 'FT8',
        'bandwidth_hz': 50,  # 50 Hz
        'bandwidth_db_hz': 19,  # VOACAP uses 19 dB/Hz for FT8
        'required_snr': -21,  # dB
        'description': 'FT8 Digital Mode'
    },
    'FT4': {
        'name': 'FT4',
        'bandwidth_hz': 90,  # 90 Hz
        'bandwidth_db_hz': 19,  # Similar to FT8
        'required_snr': -17,  # dB (slightly less robust than FT8)
        'description': 'FT4 Digital Mode (faster than FT8)'
    },
    'CW': {
        'name': 'CW',
        'bandwidth_hz': 500,  # 500 Hz (typical CW filter)
        'bandwidth_db_hz': 13,  # VOACAP uses 13 dB/Hz for CW
        'required_snr': 6,  # dB
        'description': 'Morse Code (CW)'
    },
    'SSB': {
        'name': 'SSB',
        'bandwidth_hz': 2700,  # 2.7 kHz (standard SSB bandwidth)
        'bandwidth_db_hz': 38,  # VOACAP uses 38 dB/Hz for SSB
        'required_snr': 10,  # dB
        'description': 'Single Sideband Voice'
    },
    'AM': {
        'name': 'AM',
        'bandwidth_hz': 6000,  # 6 kHz
        'bandwidth_db_hz': 42,  # 10*log10(6000) ≈ 38 + 4
        'required_snr': 15,  # dB (less efficient than SSB)
        'description': 'Amplitude Modulation Voice'
    },
    'PSK31': {
        'name': 'PSK31',
        'bandwidth_hz': 31.25,  # 31.25 Hz
        'bandwidth_db_hz': 15,  # 10*log10(31.25)
        'required_snr': -10,  # dB
        'description': 'PSK31 Digital Mode'
    },
    'RTTY': {
        'name': 'RTTY',
        'bandwidth_hz': 170,  # 170 Hz shift + filters
        'bandwidth_db_hz': 22,  # 10*log10(170)
        'required_snr': 0,  # dB
        'description': 'Radioteletype'
    }
}


def apply_mode_preset(engine, mode):
    """
    Apply a mode preset to a PredictionEngine.

    Args:
        engine: PredictionEngine instance
        mode: Mode name (e.g., 'WSPR', 'FT8', 'CW', 'SSB')

    Returns:
        bool: True if preset was applied, False if mode not found

    Example:
        >>> engine = PredictionEngine()
        >>> apply_mode_preset(engine, 'FT8')
        >>> # Engine is now configured for FT8 mode
    """
    if mode.upper() not in MODE_PRESETS:
        return False

    preset = MODE_PRESETS[mode.upper()]
    engine.params.bandwidth_hz = preset['bandwidth_hz']
    engine.params.required_snr = preset['required_snr']

    return True


def get_mode_list():
    """
    Get list of available mode names.

    Returns:
        list: List of mode names
    """
    return list(MODE_PRESETS.keys())


def get_mode_info(mode):
    """
    Get information about a specific mode.

    Args:
        mode: Mode name

    Returns:
        dict: Mode information or None if not found
    """
    return MODE_PRESETS.get(mode.upper(), None)
