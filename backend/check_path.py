import sys
import os

print("Python executable:", sys.executable)
print("Python path:", sys.path)
print("Current working directory:", os.getcwd())

try:
    import pandas
    print("Pandas version:", pandas.__version__)
    print("Pandas location:", pandas.__file__)
except ImportError as e:
    print("Error importing pandas:", e)
