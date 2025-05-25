from src.database.queries.hevy_sql_queries import (
    query_get_all_workouts,
    query_get_exercises_in_workout,
    query_get_sets_for_exercise_in_workout,
    query_get_all_unique_exercise_names,
    query_get_exercise_counts,
    query_get_primary_muscle_volume,
    query_get_secondary_muscle_volume
)
from src.database.queries.sleep_queries import query_get_sleep_data
from src.database.queries.nutrition_queries import query_get_nutrition_data
from src.database.queries.health_markers_queries import query_get_health_markers
from src.database.queries.diet_cycles_queries import (
    query_get_current_diet_cycle,
    query_get_all_diet_cycles,
    query_insert_diet_cycle,
    query_update_diet_cycle_end_date
)
from sqlalchemy.orm import Session
from src.database.connection import engine
import matplotlib.pyplot as plt
from src.database.database_utils import apply_date_filter

# Initialize the database session
db = Session(bind=engine)

def display_all_workouts(start_date=None, end_date=None):
    workouts_query = query_get_all_workouts(start_date, end_date)
    workouts = db.execute(workouts_query).fetchall()
    for workout in workouts:
        print(workout)

def display_exercises_in_workout(workout_id):
    exercises = query_get_exercises_in_workout(workout_id)
    for exercise in exercises:
        print(exercise)

def display_sets_for_exercise(workout_id, exercise_name):
    sets = query_get_sets_for_exercise_in_workout(workout_id, exercise_name)
    for set_data in sets:
        print(set_data)

def display_unique_exercise_names(start_date=None, end_date=None):
    exercises_query = query_get_all_unique_exercise_names(start_date, end_date)
    exercises = db.execute(exercises_query).fetchall()
    for exercise in exercises:
        print(exercise.exercise_name)

def display_exercise_counts(start_date=None, end_date=None):
    counts_query = query_get_exercise_counts(start_date, end_date)
    counts = db.execute(counts_query).fetchall()
    for count in counts:
        print(f"{count.exercise_name}: {count.occurrence_count}")

def display_sleep_data(start_date=None, end_date=None):
    sleep_data = query_get_sleep_data(start_date, end_date)
    for record in sleep_data:
        print(record)

def display_nutrition_data(start_date=None, end_date=None):
    nutrition_data = query_get_nutrition_data(start_date, end_date)
    for record in nutrition_data:
        print(record)

def display_health_markers(start_date=None, end_date=None):
    health_markers = query_get_health_markers(start_date, end_date)
    for record in health_markers:
        print(record)

def display_current_diet_cycle():
    current_cycle = query_get_current_diet_cycle()
    print(current_cycle)

def display_all_diet_cycles(start_date=None, end_date=None):
    cycles_query = query_get_all_diet_cycles(start_date, end_date)
    cycles = db.execute(cycles_query).fetchall()
    for cycle in cycles:
        print(cycle)

def add_diet_cycle(start_date, cycle_type, end_date=None, notes=None):
    query_insert_diet_cycle(start_date, cycle_type, end_date, notes)
    print("Diet cycle added successfully.")

def end_diet_cycle(cycle_id, end_date):
    query_update_diet_cycle_end_date(cycle_id, end_date)
    print(f"Diet cycle {cycle_id} ended on {end_date}.")

def display_muscle_group_volume(muscle_name, start_date=None, end_date=None):
    """Displays a bar chart of exercise volume for a muscle group."""
    primary_volume_query = query_get_primary_muscle_volume(muscle_name, start_date, end_date)
    secondary_volume_query = query_get_secondary_muscle_volume(muscle_name, start_date, end_date)

    primary_volume_kg = db.execute(primary_volume_query).scalar() or 0
    secondary_volume_kg = db.execute(secondary_volume_query).scalar() or 0

    # Convert volumes to pounds
    primary_volume_lbs = primary_volume_kg * 2.20462
    secondary_volume_lbs = secondary_volume_kg * 2.20462

    # Create bar chart
    labels = ['Primary Muscle', 'Secondary Muscle']
    volumes = [primary_volume_lbs, secondary_volume_lbs]

    plt.bar(labels, volumes, color=['blue', 'orange'])
    plt.title(f"Exercise Volume for {muscle_name.capitalize()} ({start_date} to {end_date})")
    plt.ylabel("Volume (Weight x Reps in lbs)")
    plt.show()
