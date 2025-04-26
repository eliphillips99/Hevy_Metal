import os
import json
import sqlite3
from datetime import datetime

DATABASE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/hevy_metal.db"))
JSON_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/HealthAutoExport-2023-06-17-2025-04-26.json"))

def get_or_create_common_data_id(cursor, date, source):
    """
    Get or create a common_data_id for a given date and source.
    """
    cursor.execute("""
        SELECT common_data_id FROM common_data WHERE date = ? AND source = ?
    """, (date, source))
    result = cursor.fetchone()
    if result:
        return result[0]
    
    # Insert new common_data entry
    cursor.execute("""
        INSERT INTO common_data (date, source)
        VALUES (?, ?)
    """, (date, source))
    return cursor.lastrowid

def get_or_create_metric_id(cursor, metric_name, units, category="general"):
    """
    Get or create a metric_id for a given metric name.
    """
    cursor.execute("""
        SELECT metric_id FROM metrics WHERE metric_name = ?
    """, (metric_name,))
    result = cursor.fetchone()
    if result:
        return result[0]
    
    # Insert new metric entry
    cursor.execute("""
        INSERT INTO metrics (metric_name, units, category)
        VALUES (?, ?, ?)
    """, (metric_name, units, category))
    return cursor.lastrowid

def import_daily_data(data, conn):
    """
    Imports one day's worth of health data into the database.
    :param data: A dictionary containing the data for one day.
    :param conn: SQLite connection object.
    """
    cursor = conn.cursor()

    # Import metrics data
    for metric in data.get("metrics", []):
        metric_name = metric.get("name")
        metric_units = metric.get("units")
        metric_data = metric.get("data", [])

        # Get or create the metric_id
        metric_id = get_or_create_metric_id(cursor, metric_name, metric_units)

        # Insert each data entry for the metric
        for entry in metric_data:
            date = entry.get("date")
            qty = entry.get("qty")
            source = entry.get("source", "Unknown")

            # Convert date to a datetime object
            try:
                timestamp = datetime.strptime(date, "%Y-%m-%d %H:%M:%S %z")
            except ValueError as e:
                print(f"Error parsing date '{date}': {e}")
                continue

            # Get or create the common_data_id
            common_data_id = get_or_create_common_data_id(cursor, timestamp, source)

            # Insert into the data table
            try:
                cursor.execute("""
                    INSERT INTO data (common_data_id, metric_id, qty, data_json, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (common_data_id, metric_id, qty, json.dumps(entry), datetime.now(), datetime.now()))
            except sqlite3.IntegrityError as e:
                print(f"Error inserting data for metric '{metric_name}': {e}")

    # Import sleep cycle data
    for sleep_entry in data.get("sleep_cycles", []):
        start_time = sleep_entry.get("start_time")
        end_time = sleep_entry.get("end_time")
        sleep_type = sleep_entry.get("type")
        source = sleep_entry.get("source", "Unknown")

        # Convert times to datetime objects
        try:
            start_timestamp = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S %z")
            end_timestamp = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S %z")
        except ValueError as e:
            print(f"Error parsing sleep cycle times: {e}")
            continue

        # Get or create the common_data_id
        common_data_id = get_or_create_common_data_id(cursor, start_timestamp, source)

        # Insert into the sleep_records table
        try:
            cursor.execute("""
                INSERT INTO sleep_records (common_data_id, start_time, end_time, sleep_type, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (common_data_id, start_timestamp, end_timestamp, sleep_type, datetime.now(), datetime.now()))
        except sqlite3.IntegrityError as e:
            print(f"Error inserting sleep cycle data: {e}")

    # Import nutrition data
    for nutrition_entry in data.get("nutrition", []):
        date = nutrition_entry.get("date")
        calories = nutrition_entry.get("calories")
        protein_g = nutrition_entry.get("protein_g")
        carbohydrates_g = nutrition_entry.get("carbohydrates_g")
        fat_g = nutrition_entry.get("fat_g")
        source = nutrition_entry.get("source", "Unknown")

        # Convert date to a datetime object
        try:
            timestamp = datetime.strptime(date, "%Y-%m-%d %H:%M:%S %z")
        except ValueError as e:
            print(f"Error parsing nutrition date '{date}': {e}")
            continue

        # Get or create the common_data_id
        common_data_id = get_or_create_common_data_id(cursor, timestamp, source)

        # Insert into the nutrition_data table
        try:
            cursor.execute("""
                INSERT INTO nutrition_data (common_data_id, calories, protein_g, carbohydrates_g, fat_g, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (common_data_id, calories, protein_g, carbohydrates_g, fat_g, datetime.now(), datetime.now()))
        except sqlite3.IntegrityError as e:
            print(f"Error inserting nutrition data: {e}")

    # Commit the changes
    conn.commit()

def import_historical_data(json_file_path):
    """
    Loops through the JSON file and imports all historical data into the database.
    :param json_file_path: Path to the JSON file containing historical data.
    """
    if not os.path.exists(json_file_path):
        print(f"JSON file not found: {json_file_path}")
        return

    # Load the JSON file
    with open(json_file_path, "r") as file:
        health_data = json.load(file)

    # Connect to the database
    conn = sqlite3.connect(DATABASE_NAME)

    # Import the data
    print("Importing historical health data...")
    import_daily_data(health_data["data"], conn)

    # Close the connection
    conn.close()
    print("Historical data import complete.")

if __name__ == "__main__":
    # Import historical data
    import_historical_data(JSON_FILE_PATH)