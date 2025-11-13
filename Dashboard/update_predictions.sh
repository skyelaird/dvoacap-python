#!/bin/bash
#
# VE1ATM Propagation Update Script
# Run this to generate fresh predictions with latest solar data
#

echo "========================================="
echo "  VE1ATM HF Propagation Prediction"
echo "  Updating with latest solar data..."
echo "========================================="
echo ""

# Run the Python prediction generator
python3 generate_propagation.py

echo ""
echo "✓ Predictions updated!"
echo ""
echo "View your dashboard:"
echo "  • Open: propagation_dashboard.html"
echo "  • Or run: python3 -m http.server 8000"
echo "  • Then visit: http://localhost:8000/propagation_dashboard.html"
echo ""
echo "========================================="
