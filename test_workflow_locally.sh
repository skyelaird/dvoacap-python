#!/bin/bash
# Test if validation workflow would pass locally

set -e

echo "=== Testing Validation Workflow Steps Locally ==="
echo

echo "Step 1: Install dependencies"
python -m pip install --upgrade pip -q
pip install numpy scipy matplotlib pytest -q
pip install -e . -q
echo "✓ Dependencies installed"
echo

echo "Step 2: Run reference validation"
python test_voacap_reference.py --quiet
echo "✓ Validation completed"
echo

echo "Step 3: Check validation results"
if [ -f validation_reference_results.json ]; then
    PASS_RATE=$(python -c "import json; print(json.load(open('validation_reference_results.json'))['summary']['pass_rate'])")
    echo "Pass rate: ${PASS_RATE}%"
    
    python -c "import sys; import json; \
      result = json.load(open('validation_reference_results.json')); \
      pass_rate = result['summary']['pass_rate']; \
      min_target = result['targets']['minimum_pass_rate']; \
      print(f'Pass rate: {pass_rate}%'); \
      print(f'Target: {min_target}%'); \
      print(f'Result: {\"PASS\" if pass_rate >= min_target else \"FAIL\"}'); \
      sys.exit(0 if pass_rate >= min_target else 1)"
else
    echo "ERROR: validation_reference_results.json not found"
    exit 1
fi
echo "✓ Validation check passed"
echo

echo "Step 4: Check test coverage"
python -c "
import json

with open('test_config.json') as f:
    config = json.load(f)

total_tests = len(config['test_cases'])
active_tests = len([tc for tc in config['test_cases'] if tc.get('status') == 'active'])
pending_tests = total_tests - active_tests

print(f'Total test cases defined: {total_tests}')
print(f'Active test cases: {active_tests}')
print(f'Pending reference data: {pending_tests}')

if active_tests == 0:
    print('WARNING: No active test cases')
    exit(1)
"
echo "✓ Test coverage check passed"
echo

echo "=== ALL WORKFLOW STEPS PASSED ✓ ==="
