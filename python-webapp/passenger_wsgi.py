"""
Passenger WSGI Entry Point for Netcup Webhosting
This file is required by Phusion Passenger to run the Flask application
"""

import sys
import os

# Get the directory of this file
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Add the application directory to the Python path
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Import the Flask application
from app import app as application

# This is what Passenger will use
# The variable MUST be named 'application' for Passenger to recognize it
