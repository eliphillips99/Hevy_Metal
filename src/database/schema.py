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
    Column('workout_id', Integer, primary_key=True, autoincrement=True),
    Column('hevy_workout_id', String, unique=True, nullable=False),
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
    Column('workout_id', Integer, ForeignKey('workouts.workout_id'), nullable=False),
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
    Column('rpe', Float),
    Column('custom_metric', String),
)

metrics = Table('metrics', metadata,
    Column('metric_id', Integer, primary_key=True, autoincrement=True),
    Column('metric_name', String, nullable=False, unique=True),
    Column('units', String),
    Column('description', String),
    Column('category', String, nullable=False)
)


sleep_data_table = Table('sleep_data', metadata,
    Column('sleep_data_id', Integer, primary_key=True, autoincrement=True),
    Column('common_data_id', Integer, ForeignKey('common_data.common_data_id'), nullable=False),
    Column('start_time', DateTime, nullable=False),
    Column('end_time', DateTime, nullable=False),
    Column('in_bed_duration_hours', Float),  # inBed from JSON
    Column('sleep_duration_hours', Float), # asleep from JSON
    Column('awake_duration_hours', Float),  # awake from JSON
    Column('rem_sleep_duration_hours', Float),    # rem from JSON
    Column('deep_sleep_duration_hours', Float),   # deep from JSON
    Column('core_sleep_duration_hours', Float), # core from JSON
    Column('in_bed_start', DateTime), 
    Column('in_bed_end', DateTime),   
    Column('created_at', DateTime),
    Column('updated_at', DateTime)
)

nutrition_data_table = Table(
    'nutrition_data', metadata,
    Column('nutrition_data_id', Integer, primary_key=True, autoincrement=True),
    Column('common_data_id', Integer, ForeignKey('common_data.common_data_id'), nullable=False),
    Column('calories', Float),
    Column('protein_g', Float),
    Column('carbohydrates_g', Float),
    Column('fat_g', Float),
    Column('dietary_caffeine', Float),
    Column('dietary_water', Float),
    Column('fiber_g', Float),
    Column('dietary_energy_kcal', Float),
    Column('potassium_mg', Float),
    Column('timestamp', DateTime, nullable=False),
    Column('created_at', DateTime),
    Column('updated_at', DateTime)
)

diet_cycles_table = Table(
    'diet_cycles', metadata,
    Column('cycle_id', Integer, primary_key=True, autoincrement=True),
    Column('common_data_id', Integer, ForeignKey('common_data.common_data_id'), nullable=False),
    Column('start_date', Date, nullable=False),
    Column('end_date', Date),
    Column('cycle_type', String, nullable=False),
    Column('notes', String),
    Column('created_at', DateTime),  # Added for consistency
    Column('updated_at', DateTime)  # Added for consistency
)

data_table = Table(
    'data', metadata,
    Column('data_id', Integer, primary_key=True, autoincrement=True),
    Column('common_data_id', Integer, ForeignKey('common_data.common_data_id'), nullable=False),
    Column('metric_id', Integer, ForeignKey('metrics.metric_id'), nullable=False),
    Column('qty', Float, nullable=True),
    Column('data_json', String), # to store the raw data
    Column('created_at', DateTime),
    Column('updated_at', DateTime)
)