"""Backward-compatibility shim.

The dashboard has moved to ``src/dvoacap/dashboard/``. To run it, install
the dashboard extra and use the console script::

    pip install -e ".[dashboard]"
    dvoacap-dashboard

This shim allows the old ``python Dashboard/server.py`` invocation to keep
working.
"""

import warnings

warnings.warn(
    "Running the dashboard from Dashboard/ is deprecated. "
    "Install with `pip install -e .[dashboard]` and run `dvoacap-dashboard` instead.",
    DeprecationWarning,
    stacklevel=2,
)

from dvoacap.dashboard.server import _parse_args_and_run, main  # noqa: E402,F401

if __name__ == "__main__":
    _parse_args_and_run()
