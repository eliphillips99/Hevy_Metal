from sqlalchemy import create_engine
import os

# Database connection setup
DATABASE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/hevy_metal.db"))
engine = create_engine(f'sqlite:///{DATABASE_NAME}')
