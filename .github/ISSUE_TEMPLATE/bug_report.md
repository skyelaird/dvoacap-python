---
name: Bug Report
about: Report a bug or unexpected behavior
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description
A clear and concise description of what the bug is.

## To Reproduce
Steps to reproduce the behavior:
1. Use these parameters: '...'
2. Run this code: '...'
3. See error

## Expected Behavior
A clear description of what you expected to happen.

## Actual Behavior
What actually happened instead.

## Code Example
```python
# Minimal code example that reproduces the issue
from dvoacap import PredictionEngine
from dvoacap.path_geometry import GeoPoint

engine = PredictionEngine()
# ... your code here
```

## Environment
- DVOACAP-Python version: [e.g., 0.9.0]
- Python version: [e.g., 3.11.4]
- Operating System: [e.g., Ubuntu 22.04, macOS 14, Windows 11]
- NumPy version: [e.g., 1.24.3]
- SciPy version: [e.g., 1.11.1]

## Output/Error Messages
```
Paste any error messages or unexpected output here
```

## Additional Context
Add any other context about the problem here:
- Does this only happen with specific frequencies?
- Does this only happen at certain times of day?
- Does this only happen for certain geographic paths?
- Have you checked the validation tolerances in VALIDATION_STRATEGY.md?

## Validation Data (if applicable)
If you're comparing with VOACAP or other propagation tools:
- Tool name and version:
- Comparison data:
- Expected vs actual values:

## Possible Solution
If you have ideas on how to fix this, please share them here.
