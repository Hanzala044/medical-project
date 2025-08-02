#!/usr/bin/env python3
"""
Railway deployment entry point for MEDicos Pharmacy
"""

import sys
import os

# Add the medical directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'medical'))

# Import and run the main Flask app
from medical.app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False) 