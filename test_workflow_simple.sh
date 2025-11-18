#!/bin/bash
# Test validation workflow steps (skip pip upgrade)

set -e

echo "=== Testing Validation Workflow ===
"

echo "Step 1: Run reference validation"
python test_voacap_reference.py --quiet > /tmp/val_output.txt 2>&1
cat /tmp/val_output.txt
echo

echo "Step 2: Check validation results file exists"
if [ -f validation_reference_results.json ]; then
    echo "✓ validation_reference_results.json exists"
    PASS_RATE=$(python -c "import json; r=json.load(open('validation_reference_results.json')); print(r['summary']['pass_rate'])")
    echo "  Pass rate: ${PASS_RATE}%"
else
    echo "✗ validation_reference_results.json NOT FOUND"
    exit 1
fi
echo

echo "Step 3: Verify pass rate meets target"
python -c "
import sys
import json

with open('validation_reference_results.json') as f:
    result = json.load(f)

pass_rate = result['summary']['pass_rate']
min_target = result['targets']['minimum_pass_rate']

print(f'Pass rate: {pass_rate:.1f}%')
print(f'Minimum target: {min_target:.1f}%')

if pass_rate >= min_target:
    print('✓ PASS - Meets minimum target')
    sys.exit(0)
else:
    print('✗ FAIL - Below minimum target')
    sys.exit(1)
"
echo

echo "=== VALIDATION WORKFLOW: PASS ✓ ==="
