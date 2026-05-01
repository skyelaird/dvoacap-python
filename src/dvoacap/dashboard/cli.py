"""CLI entry point for the dvoacap dashboard."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        prog="dvoacap-dashboard",
        description="Run the DVOACAP HF propagation dashboard.",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=None,
        help="Directory for generated data and user config "
             "(default: current working directory).",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="Host to bind (default: 127.0.0.1).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind (default: 8000).",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable Flask debug mode.",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable HTTP caching (useful during development).",
    )
    parser.add_argument(
        "--skip-deps-check",
        action="store_true",
        help="Skip startup dependency check.",
    )
    parser.add_argument(
        "--skip-auto-gen",
        action="store_true",
        help="Skip automatic prediction generation on startup.",
    )
    args = parser.parse_args()

    if args.data_dir:
        os.environ["DVOACAP_DATA_DIR"] = str(args.data_dir.expanduser().resolve())

    # Imported here so DVOACAP_DATA_DIR is honoured by the time paths.py runs.
    from .server import main as server_main
    return server_main(
        host=args.host,
        port=args.port,
        debug=args.debug,
        no_cache=args.no_cache,
        skip_deps_check=args.skip_deps_check,
        skip_auto_gen=args.skip_auto_gen,
    )


if __name__ == "__main__":
    sys.exit(main())
