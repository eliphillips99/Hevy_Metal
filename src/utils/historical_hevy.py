import requests
import os
import sqlite3
import json
from datetime import datetime
from dotenv import load_dotenv
from database.database_utils import get_or_create_common_data_id
import re
import time  # Add timing to measure performance

load_dotenv()
HEVY_API_KEY = os.getenv("HEVY_API_KEY")
BASE_URL = os.getenv("HEVY_BASE_URL")
DATABASE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/hevy_metal.db"))

# Fix deduplication in fetch_all_hevy_workouts

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

# Cache for exercise details to avoid redundant API calls
exercise_details_cache = {}

# Update fetch_exercise_details to use cache
def fetch_exercise_details(exercise_template_id):
    """Fetches detailed information about an exercise, including muscle groups, equipment, is_custom, and type."""
    if exercise_template_id in exercise_details_cache:
        return exercise_details_cache[exercise_template_id]

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

        # Cache the details
        exercise_details_cache[exercise_template_id] = (primary_muscles, secondary_muscles, equipment, is_custom, exercise_type)
        return primary_muscles, secondary_muscles, equipment, is_custom, exercise_type
    except requests.exceptions.RequestException as e:
        print(f"Error fetching exercise details for {exercise_template_id}: {e}")
        return None, None, None, None, None

# Update the parsing logic for pumps to normalize ratings and split into rows
def parse_workout_description(description):
    """Parses the workout description to extract pumps, fatigue, notes, and listened_to."""
    pumps = []
    fatigue = []
    notes = None
    listened_to = None

    # Define rating scales
    rating_scale = {
        "Poor": 1,
        "Fair": 2,
        "Good": 3,
        "Great": 4,
        "Dead": 1,
        "Tired": 2,
        "Fresh": 3,
        "Hyped": 4
    }

    # Extract Pumps
    pumps_match = re.search(r"Pumps\n- Scale:.*?\n(.*?)\n", description, re.DOTALL)
    if pumps_match:
        pumps_lines = pumps_match.group(1).split(",")
        for line in pumps_lines:
            if ":" in line:
                muscle_group, rating = line.split(":", 1)  # Split only on the first colon
                muscle_group = muscle_group.strip("- ").strip()
                rating = rating.strip()
                numeric_rating = rating_scale.get(rating, int(rating) if rating.isdigit() else None)
                if numeric_rating is not None:
                    pumps.append({"muscle_group": muscle_group, "rating": numeric_rating})

    # Add logging to debug fatigue parsing and insertion
    # Update the fatigue parsing logic to handle the example format
    # Extract Fatigue
    fatigue_match = re.search(r"Fatigue\n- Scale:.*?\n((?:- .*?: .*?\n)+)", description, re.DOTALL)
    if fatigue_match:
        fatigue_lines = fatigue_match.group(1).split("\n")
        for line in fatigue_lines:
            if ":" in line:
                fatigue_type, rating = line.split(":", 1)  # Split only on the first colon
                fatigue_type = fatigue_type.strip("- ").strip()
                rating = rating.strip()
                numeric_rating = rating_scale.get(rating, int(rating) if rating.isdigit() else None)
                if numeric_rating is not None:
                    fatigue.append({"fatigue_type": fatigue_type, "rating": numeric_rating})
                    print(f"Parsed fatigue entry: {fatigue_type} - {numeric_rating}")  # Debug log

    # Extract What I Listened To
    listened_to_match = re.search(r"What I Listened To\n- (.*?)\n", description)
    if listened_to_match:
        listened_to = listened_to_match.group(1).strip()

    # Extract Notes
    notes_match = re.search(r"Notes\n- (.*?)\n", description, re.DOTALL)
    if notes_match:
        notes = notes_match.group(1).strip()
    else:
        notes = description.strip()  # If no structured data, use the entire description

    return pumps, fatigue, notes, listened_to

# Optimize skipping logic and fix timing issue in store_workouts_in_sqlite
import time

# Update store_workouts_in_sqlite to handle common_data_id and add logging

def store_workouts_in_sqlite(workouts):
    """Stores Hevy workout data in the SQLite database using the updated schema."""
    if not workouts:
        print("No workouts to store in the database.")
        return

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    process_start_time = time.perf_counter()  # Use a unique variable name for tracking elapsed time

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

        # Use get_or_create_common_data_id to ensure correct common_data_id
        try:
            timestamp = datetime.fromisoformat(workout.get("start_time")) if workout.get("start_time") else None
            if not timestamp:
                print(f"Skipping workout {hevy_workout_id} due to missing start_time.")
                continue

            common_data_id = get_or_create_common_data_id(cursor, timestamp, "Hevy API")
        except Exception as e:
            print(f"Error getting or creating common_data_id for workout {hevy_workout_id}: {e}")
            continue

        # Insert into workouts
        workout_name = workout.get("title")
        workout_description = workout.get("description")
        start_time = datetime.fromisoformat(workout.get("start_time")) if workout.get("start_time") else None
        end_time = datetime.fromisoformat(workout.get("end_time")) if workout.get("end_time") else None
        created_at = datetime.fromisoformat(workout.get("created_at").replace("Z", "+00:00")) if workout.get("created_at") else None
        updated_at = datetime.fromisoformat(workout.get("updated_at").replace("Z", "+00:00")) if workout.get("updated_at") else None

        try:
            cursor.execute(
                """
                INSERT INTO workouts (common_data_id, hevy_workout_id, workout_name, workout_description, start_time, end_time, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (common_data_id, hevy_workout_id, workout_name, workout_description, start_time, end_time, created_at, updated_at)
            )
        except sqlite3.IntegrityError as e:
            print(f"Error inserting workout {hevy_workout_id}: {e}")
            continue

        # Process exercises
        for exercise_data in workout.get("exercises", []):
            exercise_template_id = exercise_data.get("exercise_template_id")

            # Fetch exercise details
            primary_muscles, secondary_muscles, equipment, is_custom, exercise_type = fetch_exercise_details(exercise_template_id)

            # Insert exercise details into the database
            cursor.execute(
                """
                INSERT OR IGNORE INTO exercises (hevy_exercise_template_id, exercise_name, primary_muscles, secondary_muscles, equipment, is_custom, type)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (exercise_template_id, exercise_data.get("title"), primary_muscles, secondary_muscles, equipment, is_custom, exercise_type)
            )

            # Get exercise_id
            cursor.execute("SELECT exercise_id FROM exercises WHERE hevy_exercise_template_id = ?", (exercise_template_id,))
            exercise_id = cursor.fetchone()[0]

            # Insert into workout_exercises
            try:
                cursor.execute(
                    """
                    INSERT INTO workout_exercises (hevy_workout_id, exercise_id, exercise_index, exercise_notes, superset_id)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (hevy_workout_id, exercise_id, exercise_data.get("index"), exercise_data.get("notes"), exercise_data.get("superset_id"))
                )
                workout_exercise_id = cursor.lastrowid
            except sqlite3.IntegrityError as e:
                print(f"Error inserting workout_exercise for workout {hevy_workout_id}: {e}")
                continue

            # Insert sets
            for set_data in exercise_data.get("sets", []):
                try:
                    cursor.execute(
                        """
                        INSERT INTO sets (workout_exercise_id, set_index, set_type, weight_kg, reps, duration_seconds, rpe, custom_metric)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (workout_exercise_id, set_data.get("index"), set_data.get("type"), set_data.get("weight_kg"),
                         set_data.get("reps"), set_data.get("duration_seconds"), set_data.get("rpe"), set_data.get("custom_metric"))
                    )
                except sqlite3.IntegrityError as e:
                    print(f"Error inserting set for workout_exercise_id {workout_exercise_id}: {e}")
                    continue

    conn.commit()
    conn.close()
    print(f"Finished processing all workouts in {time.perf_counter() - process_start_time:.2f} seconds.")

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