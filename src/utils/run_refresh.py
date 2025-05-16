import os
import sys

# Add the src directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.refresh_database import initialize, refresh_database

if __name__ == "__main__":
    initialize()
    refresh_database()
