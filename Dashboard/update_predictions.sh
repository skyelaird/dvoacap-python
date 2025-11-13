#!/bin/bash
#
# VE1ATM Propagation Update Script
# Run this to generate fresh predictions with latest solar data
#

echo "========================================="
echo "  VE1ATM HF Propagation Dashboard"
echo "  Updating with latest solar data..."
echo "========================================="
echo ""

# Run the Python prediction generator
python3 generate_predictions.py

echo ""
echo "✓ Predictions updated!"
echo ""
echo "View your dashboard:"
echo "  • Open: dashboard.html"
echo "  • Or run: python3 -m http.server 8000"
echo "  • Then visit: http://localhost:8000/dashboard.html"
echo ""
echo "========================================="
