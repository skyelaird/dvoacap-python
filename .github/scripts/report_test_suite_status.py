#!/usr/bin/env python3
"""Report test suite status for GitHub Actions summary."""

import json
import sys
from pathlib import Path

def main():
    config_file = Path("test_config.json")

    if not config_file.exists():
        print("❌ test_config.json not found")
        return 1

    with open(config_file) as f:
        config = json.load(f)

    test_cases = config["test_cases"]
    active = [tc for tc in test_cases if tc.get("status") == "active"]
    pending = [tc for tc in test_cases if tc.get("status") == "pending_reference"]

    print(f"**Total Test Cases:** {len(test_cases)}")
    print(f"**Active:** {len(active)}")
    print(f"**Pending Reference Data:** {len(pending)}")
    print()
    print("### Active Test Cases:")
    for tc in active:
        print(f"- ✅ {tc['id']}: {tc['name']}")
    print()
    print("### Pending Test Cases:")
    for tc in pending:
        print(f"- ⏳ {tc['id']}: {tc['name']}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
