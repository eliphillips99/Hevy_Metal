# workout-analytics/queries.py
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, select, func
from sqlalchemy.types import DateTime, Date  # Correct import for DateTime and Date
import datetime
from src.database.schema import metadata, exercises_table, workouts_table, workout_exercises_table, sets_table, sleep_data_table, nutrition_data_table, diet_cycles_table
from sqlalchemy import and_
from sqlalchemy.orm import Session
from src.database.connection import engine  # Assuming `engine` is defined in a connection module

# Initialize the database session
db = Session(bind=engine)

def query_apply_date_filter(query, table, start_date=None, end_date=None, date_column='start_time'):  # Updated default to `start_time`
    """Applies a date range filter to a SQLAlchemy query on a specified date column."""
    conditions = []
    if start_date:
        conditions.append(table.c[date_column] >= start_date)
    if end_date:
        conditions.append(table.c[date_column] <= end_date)

    if conditions:
        return query.where(and_(*conditions))
    return query

print("Debug: Columns in workouts_table:", workouts_table.columns.keys())  # Confirm available columns

def query_get_all_workouts(start_date=None, end_date=None):
    """Returns a query for all workouts, ordered by start time."""
    query = select(
        workouts_table.c.workout_id,
        workouts_table.c.workout_name,  # Correct column name
        workouts_table.c.start_time,
        workouts_table.c.end_time
    ).order_by(workouts_table.c.start_time.desc())  # Ensure `start_time` is used for ordering

    if start_date or end_date:
        conditions = []
        if start_date:
            conditions.append(workouts_table.c.start_time >= start_date)  # Use `start_time` for filtering
        if end_date:
            conditions.append(workouts_table.c.start_time <= end_date)  # Use `start_time` for filtering
        query = query.where(and_(*conditions))

    print("Debug: Generated Query:", query)  # Log the generated query
    return db.execute(query).fetchall()

def query_get_exercises_in_workout(workout_id):
    query = select(
        exercises_table.c.exercise_name
    ).\
        join(workout_exercises_table, exercises_table.c.exercise_id == workout_exercises_table.c.exercise_id).\
        where(workout_exercises_table.c.workout_id == workout_id)
    
    return db.execute(query).fetchall()

def query_get_sets_for_exercise_in_workout(workout_id, exercise_name):
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
    
    return db.execute(query).fetchall()

def query_get_all_unique_exercise_names(start_date=None, end_date=None):
    """Returns a query for all unique exercise names."""
    query = select(exercises_table.c.exercise_name).distinct()
    
    return query_apply_date_filter(query, workout_exercises_table, start_date, end_date)

def query_get_exercise_counts(start_date=None, end_date=None):
    """Returns a query for counting the occurrences of each exercise."""
    query = select(exercises_table.c.exercise_name, func.count(workout_exercises_table.c.exercise_id).label('occurrence_count')).\
        join(workout_exercises_table, exercises_table.c.exercise_id == workout_exercises_table.c.exercise_id).\
        join(workouts_table, workout_exercises_table.c.workout_id == workouts_table.c.workout_id).\
        group_by(exercises_table.c.exercise_name).\
        order_by(func.count(workout_exercises_table.c.exercise_id).desc())
    
    return query_apply_date_filter(query, workouts_table, start_date, end_date)
# More query functions using SQLAlchemy Core

def query_insert_diet_cycle(start_date, cycle_type, end_date=None, notes=None):
    return diet_cycles_table.insert().values(
        start_date=start_date,
        end_date=end_date,
        cycle_type=cycle_type,
        notes=notes
    )

def query_update_diet_cycle_end_date(cycle_id, end_date):
    return diet_cycles_table.update().where(diet_cycles_table.c.cycle_id == cycle_id).values(end_date=end_date)

def query_get_current_diet_cycle(on_date=None):
    from sqlalchemy import or_
    if on_date:
        return select(diet_cycles_table).\
            where(and_(diet_cycles_table.c.start_date <= on_date,
                       or_(diet_cycles_table.c.end_date >= on_date,
                           diet_cycles_table.c.end_date == None)))
    else:
        return select(diet_cycles_table).\
            where(diet_cycles_table.c.end_date == None).\
            order_by(diet_cycles_table.c.start_date.desc()).limit(1)

def query_get_all_diet_cycles(start_date=None, end_date=None):
    query = select(diet_cycles_table).order_by(diet_cycles_table.c.start_date.desc())
    conditions = []
    if start_date:
        conditions.append(diet_cycles_table.c.start_date >= start_date)
    if end_date:
        conditions.append(diet_cycles_table.c.start_date <= end_date)  # Assuming you filter by cycle start
    if conditions:
        query = query.where(and_(*conditions))
    return query

__all__ = [
    "query_get_all_workouts",
    "query_get_exercises_in_workout",
    "query_get_sets_for_exercise_in_workout",
    "query_get_all_unique_exercise_names",
    "query_get_exercise_counts",
    "query_insert_diet_cycle",
    "query_update_diet_cycle_end_date",
    "query_get_current_diet_cycle",
    "query_get_all_diet_cycles",
    "query_apply_date_filter",
    # Add other functions here as needed
]