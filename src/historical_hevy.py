# scripts/store_hevy_data.py
import requests
import os
import sqlite3
import json
from dotenv import load_dotenv

load_dotenv()
HEVY_API_KEY = os.getenv("HEVY_API_KEY")
BASE_URL = os.getenv("HEVY_BASE_URL")
DATABASE_NAME = "hevy_metal.db"  # Name of our SQLite database file

def fetch_all_hevy_workouts():
    """Fetches all workouts from the Hevy API with pagination."""
    if not HEVY_API_KEY:
        print("Error: HEVY_API_KEY not found in environment variables.")
        return []

    headers = {
        "api-key": HEVY_API_KEY  # Correct header for API key
    }

    all_workouts = []
    next_page_url = f"{BASE_URL}/workouts"  # Start with the initial endpoint

    while next_page_url:
        print(f"Fetching data from: {next_page_url}")  # Log the current page URL
        try:
            response = requests.get(next_page_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Log the structure of the response for debugging
            print(f"API response: {json.dumps(data, indent=2)[:500]}")  # Log the first 500 characters

            # Correctly access the 'workouts' key in the response
            workouts = data.get("workouts", [])
            if not isinstance(workouts, list):
                print("Unexpected data format: 'workouts' is not a list.")
                break

            all_workouts.extend(workouts)
            print(f"Fetched {len(workouts)} workouts.")  # Log the number of workouts fetched

            # Handle pagination
            current_page = data.get("page")
            page_count = data.get("page_count")
            if current_page and page_count and current_page < page_count:
                next_page_url = f"{BASE_URL}/workouts?page={current_page + 1}"
            else:
                next_page_url = None

            import time
            time.sleep(0.1)  # Avoid hitting API rate limits

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from Hevy API: {e}")
            break

    if not all_workouts:
        print("No workouts found or an error occurred.")
    else:
        print(f"Finished fetching all workout data. Total workouts: {len(all_workouts)}")

    return all_workouts

def store_workouts_in_sqlite(workouts):
    """Stores Hevy workout data in a SQLite database with relational tables."""
    if not workouts:
        print("No workouts to store in the database.")
        return

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Create workouts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workouts (
        workout_id TEXT PRIMARY KEY,
        title TEXT,
        description TEXT,
        start_time TEXT,
        end_time TEXT,
        routine_title TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    """)
    conn.commit()

    # Create exercises table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS exercises (
        exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
        hevy_exercise_template_id TEXT UNIQUE NOT NULL,
        exercise_name TEXT NOT NULL
    )
    """)
    conn.commit()

    # Create workout_exercises junction table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS workout_exercises (
        workout_exercise_id INTEGER PRIMARY KEY AUTOINCREMENT,
        workout_id TEXT NOT NULL,
        exercise_id INTEGER NOT NULL,
        exercise_index INTEGER NOT NULL,
        exercise_notes TEXT,
        superset_id INTEGER,
        FOREIGN KEY (workout_id) REFERENCES workouts(workout_id),
        FOREIGN KEY (exercise_id) REFERENCES exercises(exercise_id)
    )
    """)
    conn.commit()

    # Create sets table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sets (
        set_id INTEGER PRIMARY KEY AUTOINCREMENT,
        workout_exercise_id INTEGER NOT NULL,
        set_index INTEGER NOT NULL,
        set_type TEXT,
        weight_kg REAL,
        reps INTEGER,
        distance_meters REAL,
        duration_seconds REAL,
        rpe REAL,
        custom_metric TEXT,
        FOREIGN KEY (workout_exercise_id) REFERENCES workout_exercises(workout_exercise_id)
    )
    """)
    conn.commit()

    for workout in workouts:
        if not isinstance(workout, dict):
            print(f"Skipping invalid workout data: {workout}")
            continue

        workout_id = workout.get("id")
        title = workout.get("title")
        description = workout.get("description")
        start_time = workout.get("start_time")
        end_time = workout.get("end_time")
        created_at = workout.get("created_at")
        updated_at = workout.get("updated_at")
        routine_title = workout.get("title")  # Assuming title often is routine name

        try:
            cursor.execute("""
            INSERT OR IGNORE INTO workouts (workout_id, title, description, start_time, end_time, routine_title, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (workout_id, title, description, start_time, end_time, routine_title, created_at, updated_at))
        except sqlite3.IntegrityError:
            pass

        for exercise_data in workout.get("exercises", []):
            if not isinstance(exercise_data, dict):
                print(f"Skipping invalid exercise data: {exercise_data}")
                continue

            hevy_exercise_template_id = exercise_data.get("exercise_template_id")
            exercise_name = exercise_data.get("title")
            exercise_index = exercise_data.get("index")
            exercise_notes = exercise_data.get("notes")
            superset_id = exercise_data.get("superset_id")

            cursor.execute("""
            INSERT OR IGNORE INTO exercises (hevy_exercise_template_id, exercise_name)
            VALUES (?, ?)
            """, (hevy_exercise_template_id, exercise_name))
            cursor.execute("SELECT exercise_id FROM exercises WHERE hevy_exercise_template_id = ?", (hevy_exercise_template_id,))
            exercise_record = cursor.fetchone()
            if exercise_record:
                exercise_id = exercise_record[0]

                cursor.execute("""
                INSERT INTO workout_exercises (workout_id, exercise_id, exercise_index, exercise_notes, superset_id)
                VALUES (?, ?, ?, ?, ?)
                """, (workout_id, exercise_id, exercise_index, exercise_notes, superset_id))
                workout_exercise_id = cursor.lastrowid

                for set_info in exercise_data.get("sets", []):
                    if not isinstance(set_info, dict):
                        print(f"Skipping invalid set data: {set_info}")
                        continue

                    set_index = set_info.get("index")
                    set_type = set_info.get("type")
                    weight_kg = set_info.get("weight_kg")
                    reps = set_info.get("reps")
                    distance_meters = set_info.get("distance_meters")
                    duration_seconds = set_info.get("duration_seconds")
                    rpe = set_info.get("rpe")
                    custom_metric = set_info.get("custom_metric")

                    cursor.execute("""
                    INSERT INTO sets (workout_exercise_id, set_index, set_type, weight_kg, reps, distance_meters, duration_seconds, rpe, custom_metric)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (workout_exercise_id, set_index, set_type, weight_kg, reps, distance_meters, duration_seconds, rpe, custom_metric))

    conn.commit()
    conn.close()
    print(f"Successfully stored {len(workouts)} workouts in {DATABASE_NAME}")

def main():
    # Fetch all workouts from Hevy API
    workouts = fetch_all_hevy_workouts()
    if not workouts:
        print("No workout data found.")
        return

    # Store the fetched workouts in SQLite database
    store_workouts_in_sqlite(workouts)
    print(f"Stored {len(workouts)} workouts in the database.")

if __name__ == "__main__":
    print("Starting the Hevy data fetch and store process...")  # Log script start
    main()
    print("Process completed.")  # Log script completion
