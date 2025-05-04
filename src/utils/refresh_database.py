import os
import sys
from sqlalchemy import create_engine, MetaData, NullPool
import json
import time

# Remove dynamic sys.path modification
# Assume the script is run with the correct working directory or PYTHONPATH

from src.utils.historical_hevy import main as populate_hevy_data
from src.utils.historical_health import import_historical_data
from src.utils.historical_diet import import_diet_cycles_from_csv
from src.database.schema import metadata

DATABASE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/hevy_metal.db"))
HEALTH_JSON_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/HealthAutoExport-2023-06-17-2025-04-26.json"))
DIET_CYCLES_CSV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/diet_cycles.csv"))

def initialize():
    """Initialize the database by deleting the old one and creating a new one."""
    # Create an engine
    engine = create_engine(f"sqlite:///{DATABASE_NAME}")

    # Perform a minimal operation
    metadata = MetaData()
    metadata.create_all(bind=engine)

    # Dispose of the engine
    engine.dispose()
    time.sleep(1)  # Ensure connections are closed

    # Attempt to delete the file
    if os.path.exists(DATABASE_NAME):
        try:
            os.remove(DATABASE_NAME)
            print("File deleted successfully.")
        except PermissionError as e:
            print(f"Error deleting file: {e}")
            return  # Exit if the file cannot be deleted

    # Create a new database
    print("Creating a new database...")
    engine = create_engine(f"sqlite:///{DATABASE_NAME}", poolclass=NullPool)
    metadata.create_all(bind=engine)
    engine.dispose()  # Dispose of the engine after creation
    time.sleep(1)  # Ensure connections are closed
    print("Database schema creation complete.")

def refresh_database():
    print("Populating database with Hevy workout data...")
    populate_hevy_data()

    # Step 5: Populate the database with historical health data
    if os.path.exists(HEALTH_JSON_FILE):
        print("Populating database with historical health data...")
        import_historical_data(HEALTH_JSON_FILE)
    else:
        print(f"Health JSON file not found: {HEALTH_JSON_FILE}. Skipping health data import.")

    # Step 6: Populate the database with diet cycle data
    if os.path.exists(DIET_CYCLES_CSV_FILE):
        print("Populating database with diet cycle data...")
        import_diet_cycles_from_csv(DIET_CYCLES_CSV_FILE)
    else:
        print(f"Diet cycles CSV file not found: {DIET_CYCLES_CSV_FILE}. Skipping diet cycle data import.")

    print("Database refresh complete.")

if __name__ == "__main__":
    # Initialize the database
    initialize()

    # Refresh the database with data
    # refresh_database()