"""Backward-compatibility shim.

This script has moved to ``dvoacap.dashboard.transform_data``. Use::

    python -m dvoacap.dashboard.transform_data
"""

import sys
import warnings

warnings.warn(
    "Running transform_data.py from Dashboard/ is deprecated. "
    "Use `python -m dvoacap.dashboard.transform_data` instead.",
    DeprecationWarning,
    stacklevel=2,
)

from dvoacap.dashboard.transform_data import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
