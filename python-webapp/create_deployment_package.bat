@echo off
REM Script to create a deployment package for Netcup Webhosting (Windows)
REM This creates a ZIP file with all dependencies included

echo =========================================
echo Creating Netcup Deployment Package
echo =========================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create vendor directory with all dependencies
echo Creating vendor directory...
if exist "vendor" rmdir /s /q vendor
pip install --target vendor -r requirements.txt

REM Create deployment directory
echo Creating deployment package...
if exist "deploy" rmdir /s /q deploy
mkdir deploy\pca-app

REM Copy application files
echo Copying application files...
xcopy /E /I services deploy\pca-app\services
xcopy /E /I templates deploy\pca-app\templates
xcopy /E /I static deploy\pca-app\static
xcopy /E /I vendor deploy\pca-app\vendor
copy app.py deploy\pca-app\
copy config.py deploy\pca-app\
copy passenger_wsgi.py deploy\pca-app\
copy requirements.txt deploy\pca-app\
copy README.md deploy\pca-app\
copy DEPLOYMENT.md deploy\pca-app\

REM Create tmp directory for Passenger
mkdir deploy\pca-app\tmp

REM Update passenger_wsgi.py to include vendor path
echo Updating passenger_wsgi.py for vendor dependencies...
(
echo """
echo Passenger WSGI Entry Point for Netcup Webhosting
echo This file is required by Phusion Passenger to run the Flask application
echo """
echo.
echo import sys
echo import os
echo.
echo # Get the directory of this file
echo CURRENT_DIR = os.path.dirname^(os.path.abspath^(__file__^)^)
echo.
echo # Add vendor directory to Python path ^(for dependencies^)
echo vendor_path = os.path.join^(CURRENT_DIR, 'vendor'^)
echo if vendor_path not in sys.path:
echo     sys.path.insert^(0, vendor_path^)
echo.
echo # Add the application directory to the Python path
echo if CURRENT_DIR not in sys.path:
echo     sys.path.insert^(0, CURRENT_DIR^)
echo.
echo # Import the Flask application
echo from app import app as application
echo.
echo # This is what Passenger will use
echo # The variable MUST be named 'application' for Passenger to recognize it
) > deploy\pca-app\passenger_wsgi.py

REM Create ZIP file (requires PowerShell)
echo Creating ZIP archive...
powershell Compress-Archive -Path deploy\pca-app -DestinationPath pca-app-netcup-deployment.zip -Force

echo.
echo =========================================
echo ✅ Deployment package created successfully!
echo =========================================
echo.
echo 📦 File: pca-app-netcup-deployment.zip
echo.
echo Next steps:
echo 1. Upload and extract pca-app-netcup-deployment.zip to your Netcup webspace
echo 2. Configure Python module in WCP:
echo    - App Root: pca-app
echo    - Startup File: passenger_wsgi.py
echo    - Python Version: 3.9+
echo 3. Reload the application
echo.
echo See DEPLOYMENT.md for detailed instructions.
echo.

REM Cleanup
echo Cleaning up temporary files...
rmdir /s /q deploy

call deactivate

pause
