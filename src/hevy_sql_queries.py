# workout-analytics/queries.py
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, select, func
from sqlalchemy.types import DateTime, Date  # Correct import for DateTime and Date
import datetime
from schema import metadata, exercises_table, workouts_table, workout_exercises_table, sets_table, sleep_records_table, nutrition_records_table
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

def get_all_workouts_query(start_date=None, end_date=None):
    """Returns a query for all workouts, ordered by start time."""
    query = select(
        workouts_table.c.workout_id,
        workouts_table.c.title,
        workouts_table.c.start_time,
        workouts_table.c.end_time,
        workouts_table.c.workout_date
    ).order_by(workouts_table.c.start_time.desc())

    return apply_date_filter(query, workouts_table, start_date, end_date)

def get_exercises_in_workout_query(workout_id):
    query = select(
        exercises_table.c.exercise_name
    ).\
        join(workout_exercises_table, exercises_table.c.exercise_id == workout_exercises_table.c.exercise_id).\
        where(workout_exercises_table.c.workout_id == workout_id)
    
    return query

def get_sets_for_exercise_in_workout_query(workout_id, exercise_name):
    query = select(
        sets_table.c.set_index,
        sets_table.c.set_type,
        sets_table.c.weight_kg,
        sets_table.c.reps
    ).\
        join(workout_exercises_table, sets_table.c.workout_exercise_id == workout_exercises_table.c.workout_exercise_id).\
        join(exercises_table, workout_exercises_table.c.exercise_id == exercises_table.c.exercise_id).\
        where(and_(workout_exercises_table.c.workout_id == workout_id, exercises_table.c.exercise_name == exercise_name)).\
        order_by(sets_table.c.set_index)
    
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
    "get_all_workouts_query",
    "get_exercises_in_workout_query",
    "get_sets_for_exercise_in_workout_query",
    "get_all_unique_exercise_names_query",
    "get_exercise_counts_query",
    # Add other functions here as needed
]