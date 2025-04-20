# workout-analytics/queries.py
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, select, and_, func
import datetime
from sqlalchemy.sql import DateTime, Date
from .schema import metadata, exercises_table, workouts_table, workout_exercises_table, sets_table, sleep_records_table, nutrition_records_table
from sqlalchemy import and_

def apply_date_filter(query, workouts_table, start_date=None, end_date=None):
    """Applies a date range filter to a SQLAlchemy query involving the workouts table."""
    conditions = []
    if start_date:
        conditions.append(workouts_table.c.workout_date >= start_date)
    if end_date:
        conditions.append(workouts_table.c.workout_date <= end_date)

    if conditions:
        return query.where(and_(*conditions))
    return query

def get_all_unique_exercise_names_query(start_date=None, end_date=None):
    """Returns a query for all unique exercise names."""
    query = select(exercises_table.c.exercise_name).distinct()
    return apply_date_filter(query, workout_exercises_table, start_date, end_date)

def get_exercise_counts_query(start_date=None, end_date=None):
    """Returns a query for counting the occurrences of each exercise."""
    query = select(exercises_table.c.exercise_name, func.count(workout_exercises_table.c.exercise_id).label('occurrence_count')).\
        join(workout_exercises_table, exercises_table.c.exercise_id == workout_exercises_table.c.exercise_id).\
        group_by(exercises_table.c.exercise_name).\
        order_by(func.count(workout_exercises_table.c.exercise_id).desc())


    return apply_date_filter(query, workout_exercises_table, start_date, end_date)
# More query functions using SQLAlchemy Core

__all__ = [
    "get_all_unique_exercise_names_query",
    "get_exercise_counts_query",
    # Add other functions here as needed
]