import os
import sys

# Dynamically add the project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from sqlalchemy import create_engine, MetaData, select, and_
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from src.database.schema import common_data

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

def get_or_create_common_data_id(cursor, timestamp, source):
    """
    Get or create a common_data_id for a given timestamp and source.
    """
    # Check if the entry already exists
    cursor.execute("""
        SELECT common_data_id FROM common_data WHERE date = ? AND source = ?
    """, (timestamp.strftime("%Y-%m-%d %H:%M:%S"), source))
    result = cursor.fetchone()

    if result:
        return result[0]

    # Insert a new entry
    cursor.execute("""
        INSERT INTO common_data (date, source)
        VALUES (?, ?)
    """, (
        timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        source
    ))
    return cursor.lastrowid

def apply_date_filter(query, table, start_date=None, end_date=None, date_column=None):
    """
    Apply a date range filter to a SQLAlchemy query on a specified date column.
    
    :param query: The SQLAlchemy query object.
    :param table: The table object to filter.
    :param start_date: The start date for filtering (inclusive).
    :param end_date: The end date for filtering (inclusive).
    :param date_column: The column name to apply the date filter on. Defaults to 'start_date'.
    :return: The modified query with the date filter applied.
    """
    if date_column is None:
        date_column = 'start_date'  # Default to 'start_date' if not specified

    if start_date:
        query = query.where(table.c[date_column] >= start_date)
    if end_date:
        query = query.where(table.c[date_column] <= end_date)

    return query  # Ensure this returns a valid SQLAlchemy query object