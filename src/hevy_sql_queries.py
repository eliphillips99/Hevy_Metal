# workout-analytics/queries.py
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, select, func

metadata = MetaData()

exercises_table = Table('exercises', metadata,
    Column('exercise_id', Integer, primary_key=True),
    Column('hevy_exercise_template_id', String),
    Column('exercise_name', String, nullable=False)
)

workout_exercises_table = Table('workout_exercises', metadata,
    Column('workout_exercise_id', Integer, primary_key=True),
    Column('workout_id', String, ForeignKey('workouts.workout_id')),
    Column('exercise_id', Integer, ForeignKey('exercises.exercise_id')),
    Column('exercise_index', Integer),
    Column('exercise_notes', String),
    Column('superset_id', Integer)
)

def get_all_unique_exercise_names_query():
    return select(exercises_table.c.exercise_name).distinct()

def get_exercise_counts_query():
    return select(exercises_table.c.exercise_name, func.count(workout_exercises_table.c.exercise_id).label('occurrence_count')).\
        join(workout_exercises_table, exercises_table.c.exercise_id == workout_exercises_table.c.exercise_id).\
        group_by(exercises_table.c.exercise_name).\
        order_by(func.count(workout_exercises_table.c.exercise_id).desc())

# More query functions using SQLAlchemy Core

__all__ = [
    "get_all_unique_exercise_names_query",
    "get_exercise_counts_query",
    # Add other functions here as needed
]