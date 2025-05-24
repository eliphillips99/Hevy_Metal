# workout-analytics/queries.py
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, select, func
from sqlalchemy.types import DateTime, Date  # Correct import for DateTime and Date
import datetime
from src.database.schema import metadata, exercises_table, workouts_table, workout_exercises_table, sets, sleep_data_table, nutrition_data_table, diet_cycles_table, common_data
from sqlalchemy import and_, or_  # Ensure or_ is imported
from sqlalchemy.orm import Session
from src.database.connection import engine  # Assuming `engine` is defined in a connection module
from src.database.database_utils import apply_date_filter

# Initialize the database session
db = Session(bind=engine)

def query_apply_date_filter(query, table, start_date=None, end_date=None, date_column='date'):
    """
    Applies a date range filter to a SQLAlchemy query on a specified date column.
    """
    conditions = []
    if start_date:
        conditions.append(table.c[date_column] >= start_date)
    if end_date:
        conditions.append(table.c[date_column] <= end_date)

    if conditions:
        query = query.where(and_(*conditions))
    return query

def query_get_all_workouts(start_date=None, end_date=None):
    """Returns a query for all workouts, ordered by start time."""
    query = select(
        workouts_table.c.hevy_workout_id.label("workout_id"),
        workouts_table.c.workout_name,
        workouts_table.c.start_time,
        workouts_table.c.end_time
    ).order_by(workouts_table.c.start_time.desc())

    query = apply_date_filter(query, workouts_table, start_date, end_date, date_column='start_time')
    return db.execute(query).fetchall()

def query_get_exercises_in_workout(workout_id):
    query = select(
        exercises_table.c.exercise_name
    ).\
        join(workout_exercises_table, exercises_table.c.exercise_id == workout_exercises_table.c.exercise_id).\
        where(workout_exercises_table.c.hevy_workout_id == workout_id)
    
    return db.execute(query).fetchall()

def query_get_sets_for_exercise_in_workout(workout_id, exercise_name):
    query = select(
        sets.c.set_index,
        sets.c.set_type,
        sets.c.weight_kg,
        sets.c.reps
    ).\
        join(workout_exercises_table, sets.c.exercise_id == workout_exercises_table.c.exercise_id).\
        join(exercises_table, workout_exercises_table.c.exercise_id == exercises_table.c.exercise_id).\
        where(and_(workout_exercises_table.c.hevy_workout_id == workout_id, exercises_table.c.exercise_name == exercise_name)).\
        order_by(sets.c.set_index)
    
    return db.execute(query).fetchall()

def query_get_all_unique_exercise_names(start_date=None, end_date=None):
    """Returns a query for all unique exercise names."""
    query = select(exercises_table.c.exercise_name).distinct()
    return query_apply_date_filter(query, common_data, start_date, end_date, date_column='date')

def query_get_exercise_counts(start_date=None, end_date=None):
    """Returns a query for counting the occurrences of each exercise."""
    query = select(
        exercises_table.c.exercise_name,
        func.count(workout_exercises_table.c.exercise_id).label('occurrence_count')
    ).join(
        workout_exercises_table, exercises_table.c.exercise_id == workout_exercises_table.c.exercise_id
    ).join(
        workouts_table, workout_exercises_table.c.hevy_workout_id == workouts_table.c.hevy_workout_id
    ).join(
        common_data, workouts_table.c.common_data_id == common_data.c.common_data_id
    ).group_by(
        exercises_table.c.exercise_name
    ).order_by(
        func.count(workout_exercises_table.c.exercise_id).desc()
    )
    return query_apply_date_filter(query, common_data, start_date, end_date, date_column='date')

# More query functions using SQLAlchemy Core

def query_get_current_diet_cycle(on_date=None):
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

def query_get_primary_muscle_volume(muscle_name, start_date=None, end_date=None):
    """Returns the total volume for exercises where the muscle is the primary muscle."""
    conditions = [
        func.lower(func.trim(func.replace(exercises_table.c.primary_muscles, ',', ' '))).like(f"%{muscle_name.lower()}%")
    ]
    if start_date:
        conditions.append(workouts_table.c.start_time >= start_date)
    if end_date:
        conditions.append(workouts_table.c.start_time <= end_date)

    query = select(
        func.sum((func.coalesce(sets.c.weight_kg, 0) * func.coalesce(sets.c.reps, 0))).label('volume')
    ).\
        join(workout_exercises_table, sets.c.workout_exercise_id == workout_exercises_table.c.workout_exercise_id).\
        join(exercises_table, workout_exercises_table.c.exercise_id == exercises_table.c.exercise_id).\
        join(workouts_table, workout_exercises_table.c.hevy_workout_id == workouts_table.c.hevy_workout_id)

    if conditions:
        query = query.where(and_(*conditions))

    return query

def query_get_secondary_muscle_volume(muscle_name, start_date=None, end_date=None):
    """Returns the total volume for exercises where the muscle is part of the secondary muscle group."""
    conditions = [
        func.lower(func.trim(func.replace(exercises_table.c.secondary_muscles, ',', ' '))).like(f"%{muscle_name.lower()}%")
    ]
    if start_date:
        conditions.append(workouts_table.c.start_time >= start_date)
    if end_date:
        conditions.append(workouts_table.c.start_time <= end_date)

    query = select(
        func.sum((func.coalesce(sets.c.weight_kg, 0) * func.coalesce(sets.c.reps, 0))).label('volume')
    ).\
        join(workout_exercises_table, sets.c.workout_exercise_id == workout_exercises_table.c.workout_exercise_id).\
        join(exercises_table, workout_exercises_table.c.exercise_id == exercises_table.c.exercise_id).\
        join(workouts_table, workout_exercises_table.c.hevy_workout_id == workouts_table.c.hevy_workout_id)

    if conditions:
        query = query.where(and_(*conditions))

    return query

def query_get_all_unique_muscle_groups(start_date=None, end_date=None):
    """Returns a query for all unique primary and secondary muscle groups within a date range."""
    primary_query = select(
        func.distinct(func.trim(func.lower(exercises_table.c.primary_muscles))).label("muscle_group")
    ).join(
        workout_exercises_table, exercises_table.c.exercise_id == workout_exercises_table.c.exercise_id
    ).join(
        workouts_table, workout_exercises_table.c.hevy_workout_id == workouts_table.c.hevy_workout_id
    ).join(
        common_data, workouts_table.c.common_data_id == common_data.c.common_data_id
    )

    secondary_query = select(
        func.distinct(func.trim(func.lower(exercises_table.c.secondary_muscles))).label("muscle_group")
    ).join(
        workout_exercises_table, exercises_table.c.exercise_id == workout_exercises_table.c.exercise_id
    ).join(
        workouts_table, workout_exercises_table.c.hevy_workout_id == workouts_table.c.hevy_workout_id
    ).join(
        common_data, workouts_table.c.common_data_id == common_data.c.common_data_id
    )

    # Apply date filters
    primary_query = query_apply_date_filter(primary_query, common_data, start_date, end_date, date_column='date')
    secondary_query = query_apply_date_filter(secondary_query, common_data, start_date, end_date, date_column='date')

    return primary_query.union(secondary_query)

def query_debug_sets_data():
    """Debug query to fetch all sets data with related exercise and workout details."""
    query = select(
        sets.c.set_id,
        sets.c.exercise_id,
        sets.c.weight_kg,
        sets.c.reps
    ).\
        join(exercises_table, sets.c.exercise_id == exercises_table.c.exercise_id, isouter=True).\
        join(workout_exercises_table, workout_exercises_table.c.exercise_id == exercises_table.c.exercise_id, isouter=True).\
        join(workouts_table, workout_exercises_table.c.hevy_workout_id == workouts_table.c.hevy_workout_id, isouter=True)
    return query

def query_debug_raw_sets_data():
    """Debug query to fetch all rows from the sets table."""
    query = select(
        sets.c.set_id,
        sets.c.exercise_id,
        sets.c.set_index,
        sets.c.weight_kg,
        sets.c.reps,
        sets.c.set_type
    )
    return query

def query_debug_exercises_data():
    """Debug query to fetch all exercises data."""
    query = select(
        exercises_table.c.exercise_id,
        exercises_table.c.exercise_name,
        exercises_table.c.primary_muscles,
        exercises_table.c.secondary_muscles
    )
    return query

def query_debug_workout_exercises_data():
    """Debug query to fetch all workout_exercises data."""
    query = select(
        workout_exercises_table.c.hevy_workout_id,
        workout_exercises_table.c.exercise_id,
        workout_exercises_table.c.exercise_index
    )
    return query

def query_debug_workouts_data():
    """Debug query to fetch all workouts data."""
    query = select(
        workouts_table.c.hevy_workout_id.label("workout_id"),
        workouts_table.c.workout_name,
        workouts_table.c.start_time,
        workouts_table.c.end_time
    )
    return query

def query_debug_unique_muscle_groups():
    """Debug query to fetch all unique primary and secondary muscle groups."""
    query = select(
        func.distinct(func.trim(func.lower(exercises_table.c.primary_muscles))).label("primary_muscle_group")
    ).union(
        select(func.distinct(func.trim(func.lower(exercises_table.c.secondary_muscles))).label("secondary_muscle_group"))
    )
    return query

def query_debug_primary_muscle_matching(muscle_name):
    """Debug query to fetch rows where the muscle matches primary_muscles."""
    query = select(
        sets.c.set_id,
        sets.c.weight_kg,
        sets.c.reps,
        exercises_table.c.primary_muscles,
        workouts_table.c.start_time
    ).\
        join(exercises_table, sets.c.exercise_id == exercises_table.c.exercise_id).\
        join(workout_exercises_table, workout_exercises_table.c.exercise_id == exercises_table.c.exercise_id).\
        join(workouts_table, workout_exercises_table.c.hevy_workout_id == workouts_table.c.hevy_workout_id).\
        where(func.lower(func.trim(func.replace(exercises_table.c.primary_muscles, ',', ' '))).like(f"%{muscle_name.lower()}%"))
    return query

def query_debug_secondary_muscle_matching(muscle_name):
    """Debug query to fetch rows where the muscle matches secondary_muscles."""
    query = select(
        sets.c.set_id,
        sets.c.weight_kg,
        sets.c.reps,
        exercises_table.c.secondary_muscles,
        workouts_table.c.start_time
    ).\
        join(exercises_table, sets.c.exercise_id == exercises_table.c.exercise_id).\
        join(workout_exercises_table, workout_exercises_table.c.exercise_id == exercises_table.c.exercise_id).\
        join(workouts_table, workout_exercises_table.c.hevy_workout_id == workouts_table.c.hevy_workout_id).\
        where(func.lower(func.trim(func.replace(exercises_table.c.secondary_muscles, ',', ' '))).like(f"%{muscle_name.lower()}%"))
    return query

def query_debug_joined_sets_exercises_workouts():
    """Debug query to fetch all rows from sets, exercises, and workouts with their relationships."""
    query = select(
        sets.c.set_id,
        sets.c.weight_kg,
        sets.c.reps,
        exercises_table.c.exercise_id,
        exercises_table.c.primary_muscles,
        exercises_table.c.secondary_muscles,
        workouts_table.c.hevy_workout_id.label("workout_id"),  # Use hevy_workout_id as the correct key
        workouts_table.c.start_time
    ).\
        join(exercises_table, sets.c.exercise_id == exercises_table.c.exercise_id, isouter=True).\
        join(workout_exercises_table, workout_exercises_table.c.exercise_id == exercises_table.c.exercise_id, isouter=True).\
        join(workouts_table, workout_exercises_table.c.hevy_workout_id == workouts_table.c.hevy_workout_id, isouter=True)  # Correct join
    return query

def query_debug_no_date_filter(muscle_name):
    """Debug query to fetch rows matching primary_muscles without date filtering."""
    query = select(
        sets.c.set_id,
        sets.c.weight_kg,
        sets.c.reps,
        exercises_table.c.primary_muscles,
        workouts_table.c.start_time
    ).\
        join(exercises_table, sets.c.exercise_id == exercises_table.c.exercise_id).\
        join(workout_exercises_table, workout_exercises_table.c.exercise_id == exercises_table.c.exercise_id).\
        join(workouts_table, workout_exercises_table.c.hevy_workout_id == workouts_table.c.hevy_workout_id).\
        where(func.lower(func.trim(func.replace(exercises_table.c.primary_muscles, ',', ' '))).like(f"%{muscle_name.lower()}%"))
    return query

def query_debug_all_sets():
    """Debug query to fetch all rows from the sets table."""
    query = select(
        sets.c.set_id,
        sets.c.exercise_id,
        sets.c.weight_kg,
        sets.c.reps,
        sets.c.set_type
    )
    return query

def query_debug_all_exercises():
    """Debug query to fetch all rows from the exercises table."""
    query = select(
        exercises_table.c.exercise_id,
        exercises_table.c.exercise_name,
        exercises_table.c.primary_muscles,
        exercises_table.c.secondary_muscles
    )
    return query

def query_debug_all_workout_exercises():
    """Debug query to fetch all rows from the workout_exercises table."""
    query = select(
        workout_exercises_table.c.hevy_workout_id,
        workout_exercises_table.c.exercise_id,
        workout_exercises_table.c.exercise_index
    )
    return query

def query_debug_all_workouts():
    """Debug query to fetch all rows from the workouts table."""
    query = select(
        workouts_table.c.hevy_workout_id.label("workout_id"),
        workouts_table.c.workout_name,
        workouts_table.c.start_time,
        workouts_table.c.end_time
    )
    return query

def query_debug_broken_relationships():
    """Debug query to find rows with broken relationships between sets and workout_exercises."""
    query = select(
        sets.c.set_id,
        sets.c.workout_exercise_id
    ).where(~sets.c.workout_exercise_id.in_(select(workout_exercises_table.c.workout_exercise_id)))
    return query

def query_debug_broken_workout_relationships():
    """
    Debug query to find rows in the workouts table with broken relationships to other tables.
    """
    query = select(
        workouts_table.c.hevy_workout_id,
        workouts_table.c.common_data_id
    ).where(
        ~workouts_table.c.common_data_id.in_(select(common_data.c.common_data_id))
    )
    return query

def query_debug_broken_set_relationships():
    """Debug query to find rows in workout_exercises without matching workout or exercise."""
    query = select(
        workout_exercises_table.c.workout_exercise_id,
        workout_exercises_table.c.hevy_workout_id,
        workout_exercises_table.c.exercise_id
    ).where(
        or_(
            ~workout_exercises_table.c.hevy_workout_id.in_(select(workouts_table.c.hevy_workout_id)),
            ~workout_exercises_table.c.exercise_id.in_(select(exercises_table.c.exercise_id))
        )
    )
    return query

def query_debug_intermediate_results(muscle_name, start_date=None, end_date=None):
    """Debug query to log intermediate results for primary muscle volume."""
    query = select(
        sets.c.set_id,
        sets.c.weight_kg,
        sets.c.reps,
        exercises_table.c.exercise_id,
        exercises_table.c.primary_muscles,
        exercises_table.c.secondary_muscles,
        workouts_table.c.start_time
    ).\
        join(exercises_table, sets.c.exercise_id == exercises_table.c.exercise_id).\
        join(workout_exercises_table, workout_exercises_table.c.exercise_id == exercises_table.c.exercise_id).\
        join(workouts_table, workout_exercises_table.c.hevy_workout_id == workouts_table.c.hevy_workout_id).\
        where(and_(
            func.lower(func.trim(func.replace(exercises_table.c.primary_muscles, ',', ' '))).like(f"%{muscle_name.lower()}%"),
            workouts_table.c.start_time >= start_date if start_date else True,
            workouts_table.c.start_time <= end_date if end_date else True
        ))

    # Debugging: Log intermediate results
    results = db.execute(query).fetchall()
    print(f"Debug: Intermediate Results for '{muscle_name}' - {results}")
    return results

def query_get_one_rm_for_exercise(exercise_name, start_date=None, end_date=None):
    """
    Returns the highest calculated 1RM for the given exercise within the specified date range.
    """
    query = select(
        sets.c.set_id,
        common_data.c.date.label("date"),
        sets.c.weight_kg.label("weight"),
        sets.c.reps.label("reps"),
        (sets.c.weight_kg * (1 + (sets.c.reps / 30))).label("calculated_1rm")  # Epley formula
    ).join(
        workout_exercises_table, sets.c.workout_exercise_id == workout_exercises_table.c.workout_exercise_id
    ).join(
        exercises_table, workout_exercises_table.c.exercise_id == exercises_table.c.exercise_id
    ).join(
        workouts_table, workout_exercises_table.c.hevy_workout_id == workouts_table.c.hevy_workout_id
    ).join(
        common_data, workouts_table.c.common_data_id == common_data.c.common_data_id
    ).where(
        exercises_table.c.exercise_name.ilike(f"%{exercise_name}%"),
        sets.c.reps > 0
    )

    # Apply date range filter using common_data's date column
    query = query_apply_date_filter(query, common_data, start_date, end_date, date_column='date')

    # Group by set ID to ensure all sets are considered and calculate the max 1RM
    query = query.group_by(
        sets.c.set_id,
        common_data.c.date,
        sets.c.weight_kg,
        sets.c.reps
    ).order_by((sets.c.weight_kg * (1 + (sets.c.reps / 30))).desc())

    return query

def query_get_heaviest_weight_for_exercise(exercise_name, start_date=None, end_date=None):
    """
    Returns the heaviest weight ever used for the given exercise, the earliest date it was achieved, and the reps for that set.
    """
    subquery = select(
        sets.c.weight_kg.label("weight"),
        common_data.c.date.label("date"),
        sets.c.reps.label("reps")
    ).join(
        workout_exercises_table, sets.c.workout_exercise_id == workout_exercises_table.c.workout_exercise_id
    ).join(
        exercises_table, workout_exercises_table.c.exercise_id == exercises_table.c.exercise_id
    ).join(
        workouts_table, workout_exercises_table.c.hevy_workout_id == workouts_table.c.hevy_workout_id
    ).join(
        common_data, workouts_table.c.common_data_id == common_data.c.common_data_id
    ).where(
        exercises_table.c.exercise_name.ilike(f"%{exercise_name}%"),
        sets.c.weight_kg.isnot(None)
    )

    # Apply date range filter using common_data's date column
    subquery = query_apply_date_filter(subquery, common_data, start_date, end_date, date_column='date')

    # Use a subquery to find the row with the maximum weight
    max_weight_subquery = subquery.alias("max_weight_subquery")
    query = select(
        max_weight_subquery.c.weight.label("max_weight"),
        func.min(max_weight_subquery.c.date).label("earliest_date"),
        max_weight_subquery.c.reps.label("reps")
    ).where(
        max_weight_subquery.c.weight == select(func.max(subquery.c.weight)).scalar_subquery()
    )

    return query

def query_debug_sets_with_exercise_and_workout_details():
    """Debug query to fetch all rows from sets_table with related exercise and workout details."""
    query = select(
        sets.c.set_id,
        sets.c.weight_kg,
        sets.c.reps,
        exercises_table.c.exercise_name,
        workouts_table.c.start_time
    ).join(
        workout_exercises_table, sets.c.workout_exercise_id == workout_exercises_table.c.workout_exercise_id  # Updated join condition
    ).join(
        exercises_table, workout_exercises_table.c.exercise_id == exercises_table.c.exercise_id  # Updated join condition
    ).join(
        workouts_table, workout_exercises_table.c.hevy_workout_id == workouts_table.c.hevy_workout_id  # Updated join condition
    )

    # Debug: Log the generated SQL query
    print(f"Generated SQL Query: {query}")

    # Return the query object instead of executing it
    return query

__all__ = [
    "query_get_all_workouts",
    "query_get_exercises_in_workout",
    "query_get_sets_for_exercise_in_workout",
    "query_get_all_unique_exercise_names",
    "query_get_exercise_counts",
    "query_get_current_diet_cycle",
    "query_get_all_diet_cycles",
    "query_apply_date_filter",
    "query_get_primary_muscle_volume",
    "query_get_secondary_muscle_volume",
    "query_get_all_unique_muscle_groups",
    "query_debug_sets_data",
    "query_debug_exercises_data",
    "query_debug_workout_exercises_data",
    "query_debug_workouts_data",
    "query_debug_raw_sets_data",  # Ensure this is included
    "query_debug_unique_muscle_groups",  # Ensure this is included
    "query_debug_primary_muscle_matching",
    "query_debug_secondary_muscle_matching",
    "query_debug_joined_sets_exercises_workouts",
    "query_debug_no_date_filter",
    "query_debug_all_sets",
    "query_debug_all_exercises",
    "query_debug_all_workout_exercises",
    "query_debug_all_workouts",
    "query_debug_broken_relationships",
    "query_debug_broken_workout_relationships",
    "query_debug_broken_set_relationships",
    "query_debug_intermediate_results",
    "query_get_one_rm_for_exercise",
    "query_get_heaviest_weight_for_exercise",
    "query_debug_sets_with_exercise_and_workout_details"
]