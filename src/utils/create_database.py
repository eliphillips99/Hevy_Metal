from sqlalchemy import create_engine
import sys
import os

# Dynamically add the project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.database.schema import metadata

DATABASE_NAME = "c:/Users/eligp/OneDrive/Documents/Coding Projects/Hevy_Metal/data/hevy_metal.db"

'''Create a SQLite database with the schema defined in the schema.py file.'''
def initialize_database():
    engine = create_engine(f"sqlite:///{DATABASE_NAME}")
    metadata.create_all(engine)
    print(f"Database initialized with schema at {DATABASE_NAME}")

if __name__ == "__main__":
    initialize_database()