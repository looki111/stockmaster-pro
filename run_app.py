#!/usr/bin/env python
"""
Run Flask Application Script for StockMaster Pro

This script loads environment variables and runs the Flask application.
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

def run_app():
    """Run the Flask application with proper environment setup"""
    print("\n" + "=" * 70)
    print("Starting StockMaster Pro Application".center(70))
    print("=" * 70)
    
    # Load environment variables
    load_dotenv()
    
    # Ensure DEV_MODE is set for development
    if os.environ.get("DEV_MODE", "").lower() != "true":
        print("⚠️ DEV_MODE is not enabled. Token verification might fail.")
        print("   Run setup_env.py first to enable development mode.")
        
        if input("Do you want to enable DEV_MODE now? (y/n): ").lower() == 'y':
            os.environ["DEV_MODE"] = "true"
            print("✅ DEV_MODE enabled for this session")
    else:
        print("✅ DEV_MODE is enabled")
    
    # Run the Flask application
    app_file = "app.py"
    if not os.path.exists(app_file):
        app_file = "backend/app.py"
        if not os.path.exists(app_file):
            print(f"❌ Cannot find application file. Tried 'app.py' and 'backend/app.py'")
            return False
    
    print(f"\nStarting Flask application from: {app_file}")
    print("=" * 70)
    
    # Use sys.executable to ensure we use the same Python interpreter
    cmd = [sys.executable, app_file]
    
    try:
        # Run the app in a subprocess
        process = subprocess.Popen(cmd)
        print(f"Flask app is running. Press Ctrl+C to stop.")
        process.wait()
    except KeyboardInterrupt:
        print("\nStopping Flask application...")
        process.terminate()
    except Exception as e:
        print(f"❌ Error running Flask application: {e}")
        return False
    
    return True

if __name__ == "__main__":
    run_app() 