import requests
import os
import sqlite3
import json
from datetime import datetime
from dotenv import load_dotenv
from database.database_utils import get_or_create_common_data_id

load_dotenv()
HEVY_API_KEY = os.getenv("HEVY_API_KEY")
BASE_URL = os.getenv("HEVY_BASE_URL")
DATABASE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/hevy_metal.db"))

def fetch_all_hevy_workouts():
    """Fetches all workouts from the Hevy API with pagination."""
    if not HEVY_API_KEY:
        print("Error: HEVY_API_KEY not found in environment variables.")
        return []

    headers = {"api-key": HEVY_API_KEY}
    all_workouts = []
    next_page_url = f"{BASE_URL}/workouts"

    while next_page_url:
        try:
            response = requests.get(next_page_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            workouts = data.get("workouts", [])
            all_workouts.extend(workouts)

            # Handle pagination
            current_page = data.get("page")
            page_count = data.get("page_count")
            next_page_url = f"{BASE_URL}/workouts?page={current_page + 1}" if current_page < page_count else None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from Hevy API: {e}")
            break

    # Deduplicate workouts by ID
    unique_workouts = {workout["id"]: workout for workout in all_workouts}.values()
    return list(unique_workouts)

def fetch_exercise_details(exercise_template_id):
    """Fetches detailed information about an exercise, including muscle groups, equipment, is_custom, and type."""
    url = f"{BASE_URL}/exercise_templates/{exercise_template_id}"
    headers = {"api-key": HEVY_API_KEY}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Extract primary and secondary muscle groups
        primary_muscles = data.get("primary_muscle_group", "")  # Single string for primary muscle
        secondary_muscles = ", ".join(data.get("secondary_muscle_groups", []))  # List of secondary muscles
        equipment = data.get("equipment", "")  # Extract equipment
        is_custom = 1 if data.get("is_custom", False) else 0  # Convert boolean to integer (1 for True, 0 for False)
        exercise_type = data.get("type", "")  # Extract type of exercise

        return primary_muscles, secondary_muscles, equipment, is_custom, exercise_type
    except requests.exceptions.RequestException as e:
        print(f"Error fetching exercise details for {exercise_template_id}: {e}")
        return None, None, None, None, None

def store_workouts_in_sqlite(workouts):
    """Stores Hevy workout data in the SQLite database using the updated schema."""
    
    if not workouts:
        print("No workouts to store in the database.")
        return

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    for workout in workouts:
        hevy_workout_id = workout.get("id")

        # Check if the workout already exists in the database
        cursor.execute("SELECT COUNT(*) FROM workouts WHERE hevy_workout_id = ?", (hevy_workout_id,))
        if cursor.fetchone()[0] > 0:
            print(f"Skipping duplicate workout {hevy_workout_id}.")
            continue

        if not isinstance(workout, dict):
            print(f"Skipping invalid workout data: {workout}")
            continue

        # Insert into common_data
        common_data_id = None
        try:
            cursor.execute("""
                INSERT INTO common_data (date, source)
                VALUES (?, ?)
            """, (workout.get("start_time"), "Hevy API"))
            common_data_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            print("Error inserting into common_data.")
            continue

        # Insert into workouts
        workout_name = workout.get("title")
        workout_description = workout.get("description")
        start_time = datetime.fromisoformat(workout.get("start_time")) if workout.get("start_time") else None
        end_time = datetime.fromisoformat(workout.get("end_time")) if workout.get("end_time") else None
        created_at = datetime.fromisoformat(workout.get("created_at").replace("Z", "+00:00")) if workout.get("created_at") else None
        updated_at = datetime.fromisoformat(workout.get("updated_at").replace("Z", "+00:00")) if workout.get("updated_at") else None

        #print(f"Inserting workout: {hevy_workout_id}, {workout_name}, {start_time}, {end_time}")

        try:
            cursor.execute("""
                INSERT INTO workouts (common_data_id, hevy_workout_id, workout_name, workout_description, start_time, end_time, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (common_data_id, hevy_workout_id, workout_name, workout_description, start_time, end_time, created_at, updated_at))
        except sqlite3.IntegrityError as e:
            print(f"Error inserting workout {hevy_workout_id}: {e}")
            continue
        except sqlite3.OperationalError as e:
            print(f"Operational error inserting workout {hevy_workout_id}: {e}")
            continue

        # Insert exercises and workout_exercises
        for exercise_data in workout.get("exercises", []):
            hevy_exercise_template_id = exercise_data.get("exercise_template_id")

            # Check if the exercise already exists in the database
            cursor.execute("SELECT COUNT(*) FROM exercises WHERE hevy_exercise_template_id = ?", (hevy_exercise_template_id,))
            if cursor.fetchone()[0] > 0:
                #print(f"Skipping duplicate exercise {hevy_exercise_template_id}.")
                continue

            exercise_name = exercise_data.get("title")
            primary_muscles, secondary_muscles, equipment, is_custom, exercise_type = fetch_exercise_details(hevy_exercise_template_id)

            # Insert into exercises
            exercise_id = None
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO exercises (hevy_exercise_template_id, exercise_name, primary_muscles, secondary_muscles, equipment, is_custom, type)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (hevy_exercise_template_id, exercise_name, primary_muscles, secondary_muscles, equipment, is_custom, exercise_type))
                cursor.execute("SELECT exercise_id FROM exercises WHERE hevy_exercise_template_id = ?", (hevy_exercise_template_id,))
                exercise_id = cursor.fetchone()[0]
            except sqlite3.IntegrityError:
                print(f"Error inserting exercise {exercise_name}.")
                continue

            # Insert into workout_exercises
            try:
                cursor.execute("""
                    INSERT INTO workout_exercises (workout_id, exercise_id, exercise_index, exercise_notes, superset_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (hevy_workout_id, exercise_id, exercise_data.get("index"), exercise_data.get("notes"), exercise_data.get("superset_id")))
            except sqlite3.IntegrityError:
                print(f"Error inserting workout_exercise for workout {hevy_workout_id}.")
                continue

            # Insert sets
            for set_data in exercise_data.get("sets", []):
                set_key = (
                    hevy_exercise_template_id,
                    set_data.get("index"),
                    set_data.get("type"),
                    set_data.get("weight_kg"),
                    set_data.get("reps"),
                    set_data.get("duration_seconds"),
                    set_data.get("rpe"),
                    set_data.get("custom_metric"),
                )

                # Check if the set already exists in the database
                cursor.execute("""
                    SELECT COUNT(*) FROM sets
                    WHERE exercise_id = (SELECT exercise_id FROM exercises WHERE hevy_exercise_template_id = ?)
                    AND set_index = ? AND set_type = ? AND weight_kg = ? AND reps = ? AND duration_seconds = ? AND rpe = ? AND custom_metric = ?
                """, set_key)
                if cursor.fetchone()[0] > 0:
                    print(f"Skipping duplicate set for exercise {hevy_exercise_template_id}.")
                    continue

                set_index = set_data.get("index")
                set_type = set_data.get("type")
                weight_kg = set_data.get("weight_kg")
                reps = set_data.get("reps")
                duration_seconds = set_data.get("duration_seconds")
                rpe = set_data.get("rpe")
                custom_metric = set_data.get("custom_metric")

                # Check if the set already exists
                try:
                    cursor.execute("""
                        SELECT COUNT(*) FROM sets
                        WHERE exercise_id = ? AND set_index = ? AND set_type = ? AND weight_kg = ? AND reps = ? AND duration_seconds = ? AND rpe = ? AND custom_metric = ?
                    """, (exercise_id, set_index, set_type, weight_kg, reps, duration_seconds, rpe, custom_metric))
                    if cursor.fetchone()[0] > 0:
                        print(f"Skipping duplicate set for exercise {exercise_name}.")
                        continue
                except sqlite3.Error as e:
                    print(f"Error checking for duplicate set: {e}")
                    continue

                # Insert the set if it does not exist
                try:
                    cursor.execute("""
                        INSERT INTO sets (exercise_id, set_index, set_type, weight_kg, reps, duration_seconds, rpe, custom_metric)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (exercise_id, set_index, set_type, weight_kg, reps, duration_seconds, rpe, custom_metric))
                except sqlite3.IntegrityError:
                    print(f"Error inserting set for exercise {exercise_name}.")
                    continue

    conn.commit()
    conn.close()
    print(f"Successfully stored {len(workouts)} workouts in {DATABASE_NAME}.")


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
    main()