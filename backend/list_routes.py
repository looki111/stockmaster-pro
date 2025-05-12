"""
List all routes in the application
"""

import os
import sys
from flask import Flask

def list_routes():
    """List all routes in the application"""
    # Create a Flask app
    app = Flask(__name__)
    
    # Import the app
    from app import app as main_app
    
    # List all routes
    print("Available routes:")
    for rule in main_app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule}")

if __name__ == "__main__":
    list_routes()
