import os
from sqlalchemy import create_engine
import sys
import os
import json
import time
from sqlalchemy.pool import NullPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

# Dynamically add the project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.utils.historical_hevy import main as populate_hevy_data
from src.utils.historical_health import import_historical_data
from src.utils.historical_diet import import_diet_cycles_from_csv
from src.database.schema import metadata

DATABASE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/hevy_metal.db"))
HEALTH_JSON_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/HealthAutoExport-2023-06-17-2025-04-26.json"))
DIET_CYCLES_CSV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/diet_cycles.csv"))

# Define the engine as a global variable
engine = create_engine(f"sqlite:///{DATABASE_NAME}")  # Use SQLAlchemy engine

def create_new_database():
    """Creates a new SQLite database and applies the schema."""
    print("Creating a new database...")
    temp_engine = create_engine(f"sqlite:///{DATABASE_NAME}", poolclass=NullPool)
    metadata.create_all(bind=temp_engine)  # Use a temporary engine
    temp_engine.dispose()  # Dispose of the temporary engine
    print("Database schema creation complete.")

from sqlalchemy import inspect

def close_all_connections():
    global engine
    if engine:
        # Dispose of the engine to close all connections
        engine.dispose()
        engine = None
        print("All connections closed and engine disposed.")

from sqlalchemy import inspect

def print_active_connections():
    global engine
    if engine:
        close_all_connections
        try:
            # Use the pool's status method to get connection information
            pool_status = engine.pool.status()
            print(f"Connection pool status: {pool_status}")
        except AttributeError:
            print("Unable to determine active connections. Connection pool may not support this operation.")

def refresh_database():
    # Step 1: Dispose of the engine to ensure all connections are closed
    global engine

    Session = scoped_session(sessionmaker(bind=engine))

    if engine:
        close_all_connections()
        time.sleep(1)  # Ensure connections are fully closed
    

    # Step 2: Delete the existing database file
    print_active_connections()
    if os.path.exists(DATABASE_NAME):
        print(f"Deleting existing database: {DATABASE_NAME}")

        try:
            if is_file_locked(DATABASE_NAME):
                print("Database file is still locked before deletion.")
            print_active_connections()    
            os.remove(DATABASE_NAME)
        
        except PermissionError as e:
            print(f"Error deleting database file: {e}")
            raise

    else:
        print("No existing database found. Proceeding to create a new one.")

    engine = create_engine(f"sqlite:///{DATABASE_NAME}", poolclass=NullPool)    

    # Step 3: Create a new database and apply the schema
    create_new_database()

    # Step 4: Populate the database with Hevy workout data
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

import psutil

def is_file_locked(filepath):
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            for item in proc.open_files():
                if filepath == item.path:
                    print(f"File is locked by process: PID={proc.info['pid']}, Name={proc.info['name']}")
                    return True
        except Exception as e:
            print(f"Error checking process: {e}")
            continue
    return False

if __name__ == "__main__":
    print_active_connections()
    refresh_database()
