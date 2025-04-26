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
    # Ensure date is stored as a string
    date_str = date.strftime("%Y-%m-%d %H:%M:%S %z") if isinstance(date, datetime) else date
    cursor.execute("""
        SELECT common_data_id FROM common_data WHERE date = ? AND source = ?
    """, (date_str, source))
    result = cursor.fetchone()
    if result:
        return result[0]
    
    # Insert new common_data entry
    cursor.execute("""
        INSERT INTO common_data (date, source)
        VALUES (?, ?)
    """, (date_str, source))
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

def insert_raw_data(cursor, metric_name, metric_units, metric_data):
    metric_id = get_or_create_metric_id(cursor, metric_name, metric_units)

    print(f"Processing metric: {metric_name}, Units: {metric_units}, Entries: {len(metric_data)}")


    for entry in metric_data:
        date = entry.get("date")
        qty = entry.get("qty")
        source = entry.get("source", "Unknown")

        #print(f"Inserting metric entry: Date: {date}, Qty: {qty}, Source: {source}")

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
            """, (common_data_id, metric_id, qty, json.dumps(entry), 
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        except sqlite3.IntegrityError as e:
            print(f"Error inserting data for metric '{metric_name}': {e}")   

def pull_sleep_from_json(metric_data, cursor):

    for sleep_entry in metric_data:
                start_time = sleep_entry.get("sleepStart")
                end_time = sleep_entry.get("sleepEnd")
                in_bed_duration = sleep_entry.get("inBed")
                sleep_duration = sleep_entry.get("asleep")
                awake_duration = sleep_entry.get("awake")
                rem_duration = sleep_entry.get("rem")
                deep_duration = sleep_entry.get("deep")
                core_duration = sleep_entry.get("core")
                in_bed_start = sleep_entry.get("inBedStart")
                in_bed_end = sleep_entry.get("inBedEnd")
                source = sleep_entry.get("source", "Unknown")


                # Convert times to datetime objects
                try:
                    start_timestamp = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S %z")
                    end_timestamp = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S %z")
                    in_bed_start_timestamp = datetime.strptime(in_bed_start, "%Y-%m-%d %H:%M:%S %z") if in_bed_start else None
                    in_bed_end_timestamp = datetime.strptime(in_bed_end, "%Y-%m-%d %H:%M:%S %z") if in_bed_end else None
                except ValueError as e:
                    print(f"Error parsing sleep cycle times: {e}")
                    continue

                # Get or create the common_data_id
                common_data_id = get_or_create_common_data_id(cursor, start_timestamp, source)

                # Insert into the sleep_data table
                try:
                    cursor.execute("""
                        INSERT INTO sleep_data (
                            common_data_id, start_time, end_time, in_bed_duration_hours, sleep_duration_hours,
                            awake_duration_hours, rem_sleep_duration_hours, deep_sleep_duration_hours,
                            core_sleep_duration_hours, in_bed_start, in_bed_end, created_at, updated_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        common_data_id,
                        start_timestamp.strftime("%Y-%m-%d %H:%M:%S %z"),
                        end_timestamp.strftime("%Y-%m-%d %H:%M:%S %z"),
                        in_bed_duration,
                        sleep_duration,
                        awake_duration,
                        rem_duration,
                        deep_duration,
                        core_duration,
                        in_bed_start_timestamp.strftime("%Y-%m-%d %H:%M:%S %z") if in_bed_start_timestamp else None,
                        in_bed_end_timestamp.strftime("%Y-%m-%d %H:%M:%S %z") if in_bed_end_timestamp else None,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ))
                    #print(f"Inserted sleep cycle: Start: {start_time}, End: {end_time}, Source: {source}")
                except sqlite3.IntegrityError as e:
                    print(f"Error inserting sleep cycle data: {e}")

def pull_nutrition_from_json(metric_data, metric_name, cursor, nutrition_data_grouped):
     for entry in metric_data:
                date = entry.get("date")
                qty = entry.get("qty")
                source = entry.get("source", "Unknown")

                # Group nutrition data by date and source
                key = (date, source)
                if key not in nutrition_data_grouped:
                    nutrition_data_grouped[key] = {"calories": None, "protein": None, "carbohydrates": None, "fat": None}
                nutrition_data_grouped[key][metric_name] = qty
        
     for (date, source), nutrition_values in nutrition_data_grouped.items():
        calories = nutrition_values.get("calories")
        protein_g = nutrition_values.get("protein")
        carbohydrates_g = nutrition_values.get("carbohydrates")
        fat_g = nutrition_values.get("fat")

        print(f"Processing grouped nutrition entry: Date: {date}, Calories: {calories}, Protein: {protein_g}, Carbs: {carbohydrates_g}, Fat: {fat_g}, Source: {source}")

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
            """, (common_data_id, calories, protein_g, carbohydrates_g, fat_g, 
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            print(f"Inserted grouped nutrition entry: Date: {date}, Calories: {calories}")
        except sqlite3.IntegrityError as e:
            print(f"Error inserting grouped nutrition data: {e}")   

def import_daily_data(data, conn):
    """
    Imports one day's worth of health data into the database.
    """
    cursor = conn.cursor()

    nutrition_metrics = ["protein", "dietary_energy", "dietary_caffeine", "dietary_water", "fiber", "potassium", "carbohydrates", "body_mass_index", "weight_body_mass"]

    nutrition_data_grouped = {}
    # Import metrics data
    for metric in data.get("metrics", []):
        metric_name = metric.get("name")
        metric_units = metric.get("units")
        metric_data = metric.get("data", [])
        insert_raw_data(cursor, metric_name, metric_units, metric_data)
        # Handle sleep_analysis specifically
        if metric_name == "sleep_analysis":
            pull_sleep_from_json(metric_data, cursor)

        elif metric_name in nutrition_metrics:
            pull_nutrition_from_json(metric_data, metric_name, cursor, nutrition_data_grouped)


    # Import nutrition data
    for nutrition_entry in data.get("nutrition_data_table", []):
        date = nutrition_entry.get("date")
        calories = nutrition_entry.get("calories")
        protein_g = nutrition_entry.get("protein_g")
        carbohydrates_g = nutrition_entry.get("carbohydrates_g")
        fat_g = nutrition_entry.get("fat_g")
        source = nutrition_entry.get("source", "Unknown")

        print(f"Processing nutrition entry: Date: {date}, Calories: {calories}, Protein: {protein_g}, Carbs: {carbohydrates_g}, Fat: {fat_g}, Source: {source}")

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
            """, (common_data_id, calories, protein_g, carbohydrates_g, fat_g, 
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                  datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            print(f"Inserted nutrition entry: Date: {date}, Calories: {calories}")
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


