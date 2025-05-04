# filepath: c:\Users\eligp\OneDrive\Documents\Coding Projects\Hevy_Metal\run_refresh.py
import os
import sys

# Add the project root to sys.path
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.utils.refresh_database import initialize, refresh_database

if __name__ == "__main__":
    initialize()
    # refresh_database()