from schema import metadata
from database_utils import engine

# Create all tables defined in the schema
metadata.create_all(engine)
print("All tables created successfully.")