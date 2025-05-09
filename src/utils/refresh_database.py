import os
import sys
from sqlalchemy import create_engine, MetaData, NullPool, text
import json
import time

# Remove dynamic sys.path modification
# Assume the script is run with the correct working directory or PYTHONPATH

from utils.historical_hevy import main as populate_hevy_data
from utils.historical_health import import_historical_data
from utils.historical_diet import import_diet_cycles_from_csv
from src.database.schema import metadata

DATABASE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/hevy_metal.db"))
HEALTH_JSON_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/HealthAutoExport-2023-06-17-2025-04-26.json"))
DIET_CYCLES_CSV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/diet_cycles.csv"))

def initialize():
    """Initialize the database by clearing the existing one."""
    # Check if the database file exists
    if os.path.exists(DATABASE_NAME):
        print(f"Clearing existing database: {DATABASE_NAME}")
        # Create an engine
        engine = create_engine(f"sqlite:///{DATABASE_NAME}", poolclass=NullPool)
        with engine.connect() as connection:
            # Drop all tables
            metadata.drop_all(bind=connection)
            # Recreate all tables
            metadata.create_all(bind=connection)
        engine.dispose()  # Dispose of the engine after clearing
        print("Database cleared and schema recreated.")
    else:
        print(f"Database file does not exist. Creating a new database: {DATABASE_NAME}")
        # Create an engine
        engine = create_engine(f"sqlite:///{DATABASE_NAME}", poolclass=NullPool)
        with engine.connect() as connection:
            # Create all tables based on the schema
            metadata.create_all(bind=connection)
        engine.dispose()  # Dispose of the engine after creation
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