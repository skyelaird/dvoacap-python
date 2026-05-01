"""Path resolution helpers for the dvoacap dashboard.

The dashboard ships static files (HTML, JSON config templates) inside the
package, but writes generated predictions and user-editable config into a
separate data directory chosen at runtime.

Phase 1 keeps this simple:

- Static assets are always located via ``PACKAGE_DIR``.
- The data directory is taken from ``$DVOACAP_DATA_DIR`` if set, otherwise
  the current working directory.

A future phase 2 will introduce a proper user-data directory
(e.g. ``~/.dvoacap/``) and a config file.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

PACKAGE_DIR = Path(__file__).parent


def get_data_dir() -> Path:
    """Return the directory for generated/user data files.

    Resolution order:
      1. ``DVOACAP_DATA_DIR`` environment variable (expanded and resolved)
      2. Current working directory

    The directory is created if it does not exist.
    """
    env = os.environ.get("DVOACAP_DATA_DIR")
    if env:
        p = Path(env).expanduser().resolve()
    else:
        p = Path.cwd()
    p.mkdir(parents=True, exist_ok=True)
    return p


def get_static_file(name: str) -> Path:
    """Return the path to a packaged static file (HTML, JSON template, etc.)."""
    return PACKAGE_DIR / name


def get_user_antenna_config() -> Path:
    """Return the path to the user's antenna_config.json.

    If the file does not exist in the data directory, copy the packaged
    template there on first access.
    """
    data_dir = get_data_dir()
    user_path = data_dir / "antenna_config.json"
    if not user_path.exists():
        template = PACKAGE_DIR / "antenna_config.json"
        if template.exists():
            shutil.copyfile(template, user_path)
    return user_path
