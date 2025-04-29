# workout-analytics/database_utils.py
from sqlalchemy import create_engine, MetaData, select, and_
from sqlalchemy.orm import sessionmaker, Session
from datetime import date
import os
from src.database.queries.hevy_sql_queries import *
from src.database.schema import (
    nutrition_data_table,
    sleep_data_table,
    health_markers_table,
    diet_cycles_table,
    workouts_table,
    exercises_table,
    workout_exercises_table,
    sets_table
)
from src.database.queries.nutrition_queries import get_nutrition_data_query
from src.database.queries.sleep_queries import get_sleep_data_query
from src.database.queries.health_markers_queries import get_health_markers_query
from src.database.queries.diet_cycles_queries import (
    insert_diet_cycle_query,
    update_diet_cycle_end_date_query,
    get_current_diet_cycle_query,
    get_all_diet_cycles_query
)

#DATABASE_NAME = os.path.join("data", "hevy_metal.db")  # Updated to point to the data directory
DATABASE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/hevy_metal.db"))
engine = create_engine(f'sqlite:///{DATABASE_NAME}')
metadata = MetaData() # You might define your tables in a separate schema file

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def execute_query(db: Session, query):
    """Executes a SQLAlchemy query object."""
    return db.execute(query).fetchall()

def fetch_one(db: Session, query):
    """Executes a SQLAlchemy query and returns the first result."""
    return db.execute(query).fetchone()

def fetch_all(db: Session, query):
    """Executes a SQLAlchemy query and returns all results."""
    return db.execute(query).fetchall()

def get_all_workouts(db: Session, start_date: date = None, end_date: date = None):
    query = select(
        workouts_table.c.workout_id,
        workouts_table.c.workout_name.label("Title"),
        workouts_table.c.start_time,
        workouts_table.c.end_time
    ).where(
        and_(
            workouts_table.c.start_time >= start_date,
            workouts_table.c.start_time <= end_date
        )
    ).order_by(workouts_table.c.start_time.desc())
    return fetch_all(db, query)

def get_exercises_in_workout(db: Session, workout_id: str):
    query = get_exercises_in_workout_query(workout_id)
    return fetch_all(db, query)

def get_sets_for_exercise_in_workout(db: Session, workout_id: str, exercise_name: str):
    query = get_sets_for_exercise_in_workout_query(workout_id, exercise_name)
    return fetch_all(db, query)

def get_all_unique_exercise_names(db: Session, start_date: date = None, end_date: date = None):
    query = get_all_unique_exercise_names_query(start_date, end_date)
    return fetch_all(db, query)

def get_exercise_counts(db: Session, start_date: date = None, end_date: date = None):
    query = get_exercise_counts_query(start_date, end_date)
    return fetch_all(db, query)

# Diet Cycle related functions
def insert_diet_cycle(db: Session, start_date: date, cycle_type: str, end_date: date = None, notes: str = None):
    query = insert_diet_cycle_query(start_date, cycle_type, end_date, notes)
    db.execute(query)
    db.commit()
    return "Diet cycle recorded."

def end_diet_cycle(db: Session, cycle_id: int, end_date: date):
    query = update_diet_cycle_end_date_query(cycle_id, end_date)
    result = db.execute(query)
    db.commit()
    return f"Diet cycle {cycle_id} ended on {end_date}."

def submit_end_diet_cycle(db: Session, cycle_id: int, end_date: date):
    """
    Submits the end date for a diet cycle and updates the database.
    """
    try:
        result = end_diet_cycle(db, cycle_id, end_date)
        print(result)  # Replace with appropriate logging or UI feedback
    except Exception as e:
        print(f"Error ending diet cycle: {e}")  # Replace with appropriate error handling

def get_current_diet_cycle(db: Session, on_date: date = None):
    query = get_current_diet_cycle_query(on_date)
    return fetch_one(db, query)

def get_all_diet_cycles(db: Session, start_date: date = None, end_date: date = None):
    query = get_all_diet_cycles_query(start_date, end_date)
    return fetch_all(db, query)

# Add corresponding functions for other queries in queries.py here
# Example for sleep records (assuming you'll create these queries):
# def get_latest_sleep_record(db: Session, start_date: date = None, end_date: date = None):
#     query = get_latest_sleep_record_query(start_date, end_date)
#     return fetch_one(db, query)
#
# def get_nutrition_on_date(db: Session, target_date: date = None, start_date: date = None, end_date: date = None):
#     query = get_nutrition_on_date_query(target_date, start_date, end_date)
#     return fetch_all(db, query)

def get_nutrition_data(db: Session, start_date: date = None, end_date: date = None):
    # Debugging: Log the input parameters
    print(f"get_nutrition_data called with start_date={start_date}, end_date={end_date}")

    query = get_nutrition_data_query(start_date, end_date)

    # Debugging: Log the SQL query and parameters

    results = fetch_all(db, query)

    return results

def get_sleep_data(db: Session, start_date: date = None, end_date: date = None):
    query = get_sleep_data_query(start_date, end_date)
    return fetch_all(db, query)

def get_health_markers(db: Session, start_date: date = None, end_date: date = None):
    query = get_health_markers_query(start_date, end_date)
    return fetch_all(db, query)

if __name__ == "__main__":
    from sqlalchemy.orm import Session

    def main():
        metadata.create_all(engine)

        db: Session = next(get_db())
        try:

            '''
            print("--- All Workouts ---")
            workouts = get_all_workouts(db)
            for workout in workouts:
                print(workout)'''

            '''print("\n--- Exercises in a Specific Workout (replace with a valid workout_id) ---")
            workout_exercises = get_exercises_in_workout(db, "your_workout_id_here")
            for exercise in workout_exercises:
                print(exercise)'''

            '''print("\n--- Sets for an Exercise in a Workout (replace with valid IDs and name) ---")
            exercise_sets = get_sets_for_exercise_in_workout(db, "your_workout_id_here", "Bench Press (Barbell)")
            for set_data in exercise_sets:
                print(set_data)'''

            '''print("\n--- All Unique Exercise Names ---")
            unique_exercises = get_all_unique_exercise_names(db)
            for exercise_name in unique_exercises:
                print(exercise_name.exercise_name)'''

            print("\n--- Exercise Counts ---")
            exercise_counts = get_exercise_counts(db)
            for row in exercise_counts:
                print(f"{row.exercise_name}: {row.occurrence_count}")

        finally:
            db.close()

    main()