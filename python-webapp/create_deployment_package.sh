#!/bin/bash

# Script to create a deployment package for Netcup Webhosting
# This creates a ZIP file with all dependencies included

echo "========================================="
echo "Creating Netcup Deployment Package"
echo "========================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create vendor directory with all dependencies
echo "Creating vendor directory..."
rm -rf vendor
pip install --target vendor -r requirements.txt

# Create deployment directory
echo "Creating deployment package..."
rm -rf deploy
mkdir -p deploy/pca-app

# Copy application files
echo "Copying application files..."
cp -r services deploy/pca-app/
cp -r templates deploy/pca-app/
cp -r static deploy/pca-app/
cp -r vendor deploy/pca-app/
cp app.py deploy/pca-app/
cp config.py deploy/pca-app/
cp passenger_wsgi.py deploy/pca-app/
cp requirements.txt deploy/pca-app/
cp README.md deploy/pca-app/
cp DEPLOYMENT.md deploy/pca-app/

# Create tmp directory for Passenger
mkdir -p deploy/pca-app/tmp

# Update passenger_wsgi.py to include vendor path
echo "Updating passenger_wsgi.py for vendor dependencies..."
cat > deploy/pca-app/passenger_wsgi.py << 'EOF'
"""
Passenger WSGI Entry Point for Netcup Webhosting
This file is required by Phusion Passenger to run the Flask application
"""

import sys
import os

# Get the directory of this file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Add vendor directory to Python path (for dependencies)
vendor_path = os.path.join(CURRENT_DIR, 'vendor')
if vendor_path not in sys.path:
    sys.path.insert(0, vendor_path)

# Add the application directory to the Python path
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Import the Flask application
from app import app as application

# This is what Passenger will use
# The variable MUST be named 'application' for Passenger to recognize it
EOF

# Create ZIP file
echo "Creating ZIP archive..."
cd deploy
zip -r ../pca-app-netcup-deployment.zip pca-app/
cd ..

echo ""
echo "========================================="
echo "✅ Deployment package created successfully!"
echo "========================================="
echo ""
echo "📦 File: pca-app-netcup-deployment.zip"
echo "📊 Size: $(du -h pca-app-netcup-deployment.zip | cut -f1)"
echo ""
echo "Next steps:"
echo "1. Upload and extract pca-app-netcup-deployment.zip to your Netcup webspace"
echo "2. Configure Python module in WCP:"
echo "   - App Root: pca-app"
echo "   - Startup File: passenger_wsgi.py"
echo "   - Python Version: 3.9+"
echo "3. Reload the application"
echo ""
echo "See DEPLOYMENT.md for detailed instructions."
echo ""

# Cleanup
echo "Cleaning up temporary files..."
rm -rf deploy

deactivate
