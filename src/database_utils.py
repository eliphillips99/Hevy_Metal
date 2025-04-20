# workout-analytics/database_utils.py
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, Session
from datetime import date
from hevy_sql_queries import * # Import all query functions
import os

DATABASE_NAME = os.path.join("data", "hevy_metal.db")  # Updated to point to the data directory
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
    query = get_all_workouts_query(start_date, end_date)
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

# Add corresponding functions for other queries in queries.py here
# Example for sleep records (assuming you'll create these queries):
# def get_latest_sleep_record(db: Session, start_date: date = None, end_date: date = None):
#     query = get_latest_sleep_record_query(start_date, end_date)
#     return fetch_one(db, query)
#
# def get_nutrition_on_date(db: Session, target_date: date = None, start_date: date = None, end_date: date = None):
#     query = get_nutrition_on_date_query(target_date, start_date, end_date)
#     return fetch_all(db, query)

if __name__ == "__main__":
    from sqlalchemy.orm import Session

    def main():
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