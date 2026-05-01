"""Backward-compatibility shim.

This script has moved to ``dvoacap.dashboard.generate_predictions``. Use::

    python -m dvoacap.dashboard.generate_predictions

or the bundled ``dvoacap-dashboard`` console script.
"""

import warnings

warnings.warn(
    "Running generate_predictions.py from Dashboard/ is deprecated. "
    "Use `python -m dvoacap.dashboard.generate_predictions` instead.",
    DeprecationWarning,
    stacklevel=2,
)

from dvoacap.dashboard.generate_predictions import main  # noqa: E402

if __name__ == "__main__":
    main()
