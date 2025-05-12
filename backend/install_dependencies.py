"""
Install missing dependencies for StockMaster Pro
"""

import os
import sys
import subprocess

def install_dependencies():
    """
    This script installs the required dependencies for StockMaster Pro.
    It specifically targets pandas and numpy which are required by the application
    but may not be installed by default.
    """
    print("Checking and installing required dependencies...")
    
    # Get the requirements file path
    requirements_file = os.path.join(os.getcwd(), 'requirements.txt')
    if not os.path.exists(requirements_file):
        print(f"Error: requirements.txt not found at {requirements_file}")
        return False
    
    try:
        # Install dependencies from requirements.txt
        print(f"Installing dependencies from {requirements_file}")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', requirements_file])
        print("All dependencies installed successfully!")
        
        # Verify pandas and numpy installation
        try:
            import pandas
            print(f"Pandas installed successfully! Version: {pandas.__version__}")
        except ImportError:
            print("WARNING: Failed to import pandas after installation. You may need to install it manually.")
        
        try:
            import numpy
            print(f"NumPy installed successfully! Version: {numpy.__version__}")
        except ImportError:
            print("WARNING: Failed to import numpy after installation. You may need to install it manually.")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        print("\nYou may need to install the dependencies manually using:")
        print(f"pip install -r {requirements_file}")
        return False

if __name__ == "__main__":
    success = install_dependencies()
    if success:
        print("\nDependencies installation complete. You can now run the application:")
        print("python app.py")
    else:
        print("\nDependencies installation failed. Please install them manually.")
