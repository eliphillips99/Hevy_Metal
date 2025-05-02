from src.database.queries.hevy_sql_queries import (
    query_get_all_workouts,
    query_get_exercises_in_workout,
    query_get_sets_for_exercise_in_workout,
    query_get_all_unique_exercise_names,
    query_get_exercise_counts
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

# Initialize the database session
db = Session(bind=engine)

def display_all_workouts(start_date=None, end_date=None):
    workouts = query_get_all_workouts(start_date, end_date)
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
    exercises = query_get_all_unique_exercise_names(start_date, end_date)
    for exercise in exercises:
        print(exercise.exercise_name)

def display_exercise_counts(start_date=None, end_date=None):
    counts = query_get_exercise_counts(start_date, end_date)
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
    cycles = query_get_all_diet_cycles(start_date, end_date)
    for cycle in cycles:
        print(cycle)

def add_diet_cycle(start_date, cycle_type, end_date=None, notes=None):
    query_insert_diet_cycle(start_date, cycle_type, end_date, notes)
    print("Diet cycle added successfully.")

def end_diet_cycle(cycle_id, end_date):
    query_update_diet_cycle_end_date(cycle_id, end_date)
    print(f"Diet cycle {cycle_id} ended on {end_date}.")
