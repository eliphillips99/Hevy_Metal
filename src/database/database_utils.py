from sqlalchemy import create_engine, MetaData, select
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from src.database.schema import common_data
import os

# Database connection setup
DATABASE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/hevy_metal.db"))
engine = create_engine(f'sqlite:///{DATABASE_NAME}')
metadata = MetaData()  # Metadata for schema

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_or_create_common_data_id(session, date, source):
    """
    Get or create a common_data_id for a given date and source.
    """
    # Ensure date is stored as a string
    date_str = date.strftime("%Y-%m-%d %H:%M:%S %z") if isinstance(date, datetime) else date
    result = session.execute(
        select(common_data.c.common_data_id)
        .where(common_data.c.date == date_str)
        .where(common_data.c.source == source)
    ).scalar()

    if result:
        return result

    # Insert new common_data entry
    result = session.execute(
        common_data.insert().values(date=date_str, source=source).returning(common_data.c.common_data_id)
    ).scalar()

    session.commit()
    return result

# filepath: /Users/eliphillips/Documents/Coding Projects/Hevy_Metal/src/utils/historical_health.py
#from src.database.database_utils import get_or_create_common_data_id
###GOES IN OTHER FILES###