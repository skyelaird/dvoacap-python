#!/usr/bin/env python3
"""Generate validation report for GitHub Actions summary."""

import json
import sys
from pathlib import Path

def main():
    results_file = Path("validation_reference_results.json")

    if not results_file.exists():
        print("❌ Validation failed to produce results")
        return 1

    with open(results_file) as f:
        results = json.load(f)

    summary = results["summary"]
    targets = results["targets"]

    print(f"**Test Cases Run:** {summary['test_cases_run']}")
    print(f"**Total Comparisons:** {summary['total']}")
    print(f"**Passed:** {summary['passed']} ({summary['pass_rate']:.1f}%)")
    print(f"**Failed:** {summary['failed']}")
    print()

    pass_rate = summary["pass_rate"]
    if pass_rate >= targets["excellent_pass_rate"]:
        print(f"✅ **EXCELLENT** - Pass rate {pass_rate:.1f}% exceeds target {targets['excellent_pass_rate']}%")
    elif pass_rate >= targets["target_pass_rate"]:
        print(f"✅ **VERY GOOD** - Pass rate {pass_rate:.1f}% exceeds target {targets['target_pass_rate']}%")
    elif pass_rate >= targets["minimum_pass_rate"]:
        print(f"✅ **PASSED** - Pass rate {pass_rate:.1f}% meets minimum {targets['minimum_pass_rate']}%")
    else:
        print(f"❌ **BELOW TARGET** - Pass rate {pass_rate:.1f}% below minimum {targets['minimum_pass_rate']}%")

    return 0

if __name__ == "__main__":
    sys.exit(main())
