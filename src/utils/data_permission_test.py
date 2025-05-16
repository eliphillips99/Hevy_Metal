""" import os
import time
DATABASE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/hevy_metal.db"))
# Ensure the file exists
if os.path.exists(DATABASE_NAME):
    print(f"Deleting existing database: {DATABASE_NAME}")
    time.sleep(1)  # Optional delay
    try:
        os.remove(DATABASE_NAME)
        print("File deleted successfully.")
    except PermissionError as e:
        print(f"Error deleting file: {e}") """


""" from sqlalchemy import create_engine
import os
import time

DATABASE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/hevy_metal.db"))

# Create an engine
engine = create_engine(f"sqlite:///{DATABASE_NAME}")

# Dispose of the engine
engine.dispose()
time.sleep(1)  # Ensure connections are closed

# Attempt to delete the file
if os.path.exists(DATABASE_NAME):
    try:
        os.remove(DATABASE_NAME)
        print("File deleted successfully.")
    except PermissionError as e:
        print(f"Error deleting file: {e}") """


""" from sqlalchemy import create_engine, MetaData
import os
import time

DATABASE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/hevy_metal.db"))

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
        print(f"Error deleting file: {e}") """



from sqlalchemy import create_engine, MetaData
import os
import time

DATABASE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/hevy_metal.db"))


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


