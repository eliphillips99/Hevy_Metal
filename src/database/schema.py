# workout-analytics/database_schema.py
from sqlalchemy import MetaData, Table, Column, Integer, String, Float, DateTime, Date, ForeignKey

metadata = MetaData()

common_data = Table('common_data', metadata,
    Column('common_data_id', Integer, primary_key=True),
    Column('date', DateTime, nullable=False),
    Column('source', String),
)

workouts_table = Table('workouts', metadata,
    Column('common_data_id', Integer, ForeignKey('common_data.common_data_id'), nullable=False),
    Column('workout_id', String, primary_key=True, autoincrement=True),
    Column('workout_name', String),
    Column('workout_description', String),
    Column('start_time', DateTime),
    Column('end_time', DateTime),
    Column('duration', Float),
    Column('routine_title', String),
    Column('created_at', DateTime),
    Column('updated_at', DateTime),
)

exercises_table = Table('exercises', metadata,
    Column('exercise_id', Integer, primary_key=True),
    Column('hevy_exercise_template_id', String, unique=True, nullable=False),
    Column('exercise_name', String, nullable=False)
)

workout_exercises_table = Table('workout_exercises', metadata,
    Column('workout_id', String, ForeignKey('workouts.workout_id'), nullable=False),
    Column('exercise_id', Integer, ForeignKey('exercises.exercise_id'), nullable=False),
    Column('exercise_index', Integer, nullable=False),
    Column('exercise_notes', String),
    Column('superset_id', Integer),
)

sets_table = Table('sets', metadata,
    Column('set_id', Integer, primary_key=True),
    Column('exercise_id', Integer, ForeignKey('exercises.exercise_id'), nullable=False),
    Column('set_index', Integer, nullable=False),
    Column('set_type', String),
    Column('weight_kg', Float),
    Column('reps', Integer),
    Column('duration_seconds', Float),
    Column('rpe', Float)
)

metrics = Table('metrics', metadata,
    Column('metric_id', Integer, primary_key=True, autoincrement=True),
    Column('metric_name', String, nullable=False, unique=True),
    Column('units', String),
    Column('description', String),
    Column('category', String, nullable=False)
)


sleep_records_table = Table('sleep_records', metadata,
    Column('sleep_id', Integer, primary_key=True),
    Column('start_time', DateTime, nullable=False),
    Column('end_time', DateTime, nullable=False),
    Column('duration_seconds', Integer),
    Column('time_in_bed_seconds', Integer),
    Column('sleep_stage_data', String),
    Column('source', String),
    Column('created_at', DateTime),
    Column('updated_at', DateTime)
)

nutrition_records_table = Table('nutrition_records', metadata,
    Column('nutrition_id', Integer, primary_key=True),
    Column('timestamp', DateTime, nullable=False),
    Column('food_name', String),
    Column('calories', Float),
    Column('protein_g', Float),
    Column('carbohydrates_g', Float),
    Column('fat_g', Float),
    Column('meal_type', String),
    Column('source', String),
    Column('created_at', DateTime),
    Column('updated_at', DateTime)
)

diet_cycles_table = Table('diet_cycles', metadata,
    Column('cycle_id', Integer, primary_key=True),
    Column('start_date', Date, nullable=False),
    Column('end_date', Date),  # Can be NULL if the cycle is ongoing
    Column('cycle_type', String, nullable=False),  # 'cut' or 'bulk'
    Column('notes', String)
)