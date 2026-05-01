#!/bin/bash
#
# DVOACAP Propagation Update Script
# Run this to generate fresh predictions with latest solar data.
#
# Use DVOACAP_DATA_DIR to control where output files are written
# (defaults to the current working directory).
#

echo "========================================="
echo "  DVOACAP HF Propagation Dashboard"
echo "  Updating with latest solar data..."
echo "========================================="
echo ""

# Run the prediction generator via the installed package.
python3 -m dvoacap.dashboard.generate_predictions

echo ""
echo "✓ Predictions updated!"
echo ""
echo "View your dashboard:"
echo "  • Run: dvoacap-dashboard"
echo "  • Then visit: http://localhost:8000/"
echo ""
echo "========================================="
