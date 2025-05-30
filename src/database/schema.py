# workout-analytics/database_schema.py
from sqlalchemy import MetaData, Table, Column, Integer, String, Float, DateTime, Date, ForeignKey, UniqueConstraint
from src.database.connection import engine

metadata = MetaData()

common_data = Table('common_data', metadata,
    Column('common_data_id', Integer, primary_key=True),
    Column('date', DateTime, nullable=False),
    Column('source', String),
    UniqueConstraint('date', 'source', name='uq_date_source')
)

workouts_table = Table('workouts', metadata,
    Column('common_data_id', Integer, ForeignKey('common_data.common_data_id'), nullable=False),
    Column('workout_id', Integer, primary_key=True, autoincrement=True),
    Column('hevy_workout_id', String, unique=True, nullable=False),
    Column('workout_name', String),
    Column('workout_description', String),
    Column('start_time', DateTime),
    Column('end_time', DateTime),
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

sleep_data_table = Table(
    'sleep_data', metadata,
    Column('sleep_data_id', Integer, primary_key=True, autoincrement=True),
    Column('common_data_id', Integer, ForeignKey('common_data.common_data_id'), nullable=False),
    Column('start_time', DateTime, nullable=False),
    Column('end_time', DateTime, nullable=False),
    Column('in_bed_duration_hours', Float),
    Column('sleep_duration_hours', Float),
    Column('awake_duration_hours', Float),
    Column('rem_sleep_duration_hours', Float),
    Column('deep_sleep_duration_hours', Float),
    Column('core_sleep_duration_hours', Float),  # Ensure this field exists
    Column('in_bed_start', DateTime),  # Ensure this field exists
    Column('in_bed_end', DateTime),  # Ensure this field exists
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
    Column('caffeine_mg', Float),
    Column('water_floz', Float),
    Column('fiber_g', Float),
    Column('potassium_mg', Float),
    Column('sodium_mg', Float),
    Column('sugar_g', Float),
    Column('timestamp', DateTime),
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
    Column('gain_rate_lbs_per_week', Float),
    Column('loss_rate_lbs_per_week', Float),
    Column('source', String),
    Column('notes', String),
    Column('created_at', DateTime),
    Column('updated_at', DateTime)
)

diet_weeks_table = Table(
    'diet_weeks', metadata,
    Column('week_id', Integer, primary_key=True, autoincrement=True),
    Column('cycle_id', Integer, ForeignKey('diet_cycles.cycle_id'), nullable=False),
    Column('common_data_id', Integer, ForeignKey('common_data.common_data_id'), nullable=False),  # Added column
    Column('week_start_date', Date, nullable=False),
    Column('calorie_target', Float),
    Column('source', String),
    Column('created_at', DateTime),
    Column('updated_at', DateTime)
)

health_markers_table = Table(
    'health_markers', metadata,
    Column('health_marker_id', Integer, primary_key=True, autoincrement=True),
    Column('common_data_id', Integer, ForeignKey('common_data.common_data_id'), nullable=False),
    Column('time_in_daylight_min', Float),
    Column('vo2_max', Float),
    Column('heart_rate_min', Float),  # New column for heart rate minimum
    Column('heart_rate_max', Float),  # New column for heart rate maximum
    Column('heart_rate_avg', Float),  # New column for heart rate average
    Column('heart_rate_variability', Float),
    Column('resting_heart_rate', Float),
    Column('respiratory_rate', Float),
    Column('blood_oxygen_saturation', Float),
    Column('body_weight_lbs', Float),
    Column('body_mass_index', Float),
    Column('created_at', DateTime),
    Column('updated_at', DateTime)
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

# Recreate the database schema
metadata.create_all(engine)