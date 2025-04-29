import os
from sqlalchemy import create_engine
import sys
import os

# Dynamically add the project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.utils.historical_hevy import main as populate_hevy_data
from src.utils.historical_health import import_historical_data
from src.utils.historical_diet import import_diet_cycles_from_csv  # Add this import
from src.database.schema import metadata

DATABASE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/hevy_metal.db"))
HEALTH_JSON_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/HealthAutoExport-2023-06-17-2025-04-26.json"))
DIET_CYCLES_CSV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/diet_cycles.csv"))  # Add this constant

def create_new_database():
    """Creates a new SQLite database and applies the schema."""
    print("Creating a new database...")
    engine = create_engine(f"sqlite:///{DATABASE_NAME}")  # Use SQLAlchemy engine
    metadata.create_all(bind=engine)  # Use SQLAlchemy metadata to create tables
    print("Database schema creation complete.")

def refresh_database():
    # Step 1: Delete the existing database file
    if os.path.exists(DATABASE_NAME):
        print(f"Deleting existing database: {DATABASE_NAME}")
        os.remove(DATABASE_NAME)
    else:
        print("No existing database found. Proceeding to create a new one.")

    # Step 2: Create a new database and apply the schema
    create_new_database()

    # Step 3: Populate the database with Hevy workout data
    print("Populating database with Hevy workout data...")
    populate_hevy_data()

    # Step 4: Populate the database with historical health data
    if os.path.exists(HEALTH_JSON_FILE):
        print("Populating database with historical health data...")
        import_historical_data(HEALTH_JSON_FILE)
    else:
        print(f"Health JSON file not found: {HEALTH_JSON_FILE}. Skipping health data import.")

    # Step 5: Populate the database with diet cycle data
    if os.path.exists(DIET_CYCLES_CSV_FILE):
        print("Populating database with diet cycle data...")
        import_diet_cycles_from_csv(DIET_CYCLES_CSV_FILE)
    else:
        print(f"Diet cycles CSV file not found: {DIET_CYCLES_CSV_FILE}. Skipping diet cycle data import.")

    print("Database refresh complete.")

if __name__ == "__main__":
    refresh_database()
