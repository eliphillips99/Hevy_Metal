import os
import json
import sqlite3
from datetime import datetime
from datetime import date
from sqlalchemy import func
from src.database.schema import health_markers_table, common_data
from sqlalchemy.orm import Session

DATABASE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/hevy_metal.db"))
JSON_FILE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/HealthAutoExport-2023-06-17-2025-04-26.json"))

# Metric name mapping
METRIC_NAME_MAPPING = {
    "weight_body_mass": "body_weight_lbs",
    "dietary_energy": "calories",
    "dietary_caffeine": "caffeine_mg",
    "dietary_water": "water_floz",
    "sodium": "sodium_mg",
    "fiber": "fiber_g",
    "potassium": "potassium_mg",
    "carbohydrates": "carbohydrates_g",
    "dietary_sugar": "sugar_g",
    "total_fat": "fat_g",
    "time_in_daylight": "time_in_daylight",
    "vo2_max": "vo2_max",
    "heart_rate": "heart_rate",
    "heart_rate_variability": "heart_rate_variability",
    "resting_heart_rate": "resting_heart_rate",
    "respiratory_rate": "respiratory_rate",
    "blood_oxygen_saturation": "blood_oxygen_saturation",
    "body_mass_index": "body_mass_index"
}

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


                cursor.execute("""
                    SELECT 1 FROM sleep_data
                    WHERE common_data_id = ? AND start_time = ? AND end_time = ?
                """, (common_data_id, start_timestamp, end_timestamp))

                if cursor.fetchone() is None:
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
        #print(f"Grouping Key: {key}, Metric Name: {metric_name}, Qty: {qty}")
        if key not in nutrition_data_grouped:
            nutrition_data_grouped[key] = {
                "calories": None,
                "protein": None,
                "carbohydrates_g": None,
                "fat_g": None,
                "water_floz": None,
                "caffeine_mg": None,
                "potassium_mg": None,
                "fiber_g": None,
                "sodium_mg": None,
                "sugar_g": None
            }
        nutrition_data_grouped[key][metric_name] = qty
        #print(f"Grouped Key: {key}, Metric: {metric_name}, Qty: {qty}")  # Debug stateme

    for (date, source), nutrition_values in nutrition_data_grouped.items():
        calories = nutrition_values.get("calories")
        protein_g = nutrition_values.get("protein")
        carbohydrates_g = nutrition_values.get("carbohydrates_g")
        fat_g = nutrition_values.get("fat_g")
        water_floz = nutrition_values.get("water_floz")
        caffeine_mg = nutrition_values.get("caffeine_mg")
        potassium_mg = nutrition_values.get("potassium_mg")
        fiber_g = nutrition_values.get("fiber_g")
        sodium_mg = nutrition_values.get("sodium_mg")
        sugar_g = nutrition_values.get("sugar_g")

        try:
            timestamp = datetime.strptime(date, "%Y-%m-%d %H:%M:%S %z")
        except ValueError as e:
            print(f"Error parsing nutrition date '{date}': {e}")
            continue

        # Get or create the common_data_id
        common_data_id = get_or_create_common_data_id(cursor, timestamp, source)

        cursor.execute("""
            SELECT 1 FROM nutrition_data WHERE common_data_id = ?
        """, (common_data_id,))
        if cursor.fetchone() is None:
            # Insert a new row
            cursor.execute("""
                INSERT INTO nutrition_data (
                    common_data_id, calories, protein_g, carbohydrates_g, fat_g, water_floz, caffeine_mg,
                    potassium_mg, fiber_g, sodium_mg, sugar_g, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                common_data_id, calories, protein_g, carbohydrates_g, fat_g, water_floz, caffeine_mg,
                potassium_mg, fiber_g, sodium_mg, sugar_g,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
        else:
            # Update the existing row
            cursor.execute("""
                UPDATE nutrition_data
                SET calories = COALESCE(?, calories),
                    protein_g = COALESCE(?, protein_g),
                    carbohydrates_g = COALESCE(?, carbohydrates_g),
                    fat_g = COALESCE(?, fat_g),
                    water_floz = COALESCE(?, water_floz),
                    caffeine_mg = COALESCE(?, caffeine_mg),
                    potassium_mg = COALESCE(?, potassium_mg),
                    fiber_g = COALESCE(?, fiber_g),
                    sodium_mg = COALESCE(?, sodium_mg),
                    sugar_g = COALESCE(?, sugar_g),
                    updated_at = ?
                WHERE common_data_id = ?
            """, (
                calories, protein_g, carbohydrates_g, fat_g, water_floz, caffeine_mg,
                potassium_mg, fiber_g, sodium_mg, sugar_g,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), common_data_id
            ))

def pull_markers_from_json(metric_data, metric_name, cursor, markers_data_grouped):
    for entry in metric_data:
        date = entry.get("date")
        qty = entry.get("qty")
        source = entry.get("source", "Unknown")

        # Group health marker data by date and source
        key = (date, source)
        if key not in markers_data_grouped:
            markers_data_grouped[key] = {
                "time_in_daylight": None,
                "vo2_max": None,
                "heart_rate": None,
                "heart_rate_variability": None,
                "resting_heart_rate": None,
                "respiratory_rate": None,
                "blood_oxygen_saturation": None,
                "body_weight_lbs": None,
                "body_mass_index": None,
            }
        markers_data_grouped[key][metric_name] = qty

    for (date, source), marker_values in markers_data_grouped.items():
        # Skip entries where all marker values are None
        if all(value is None for value in marker_values.values()):
            continue

        time_in_daylight = marker_values.get("time_in_daylight")
        vo2_max = marker_values.get("vo2_max")
        heart_rate = marker_values.get("heart_rate")
        heart_rate_variability = marker_values.get("heart_rate_variability")
        resting_heart_rate = marker_values.get("resting_heart_rate")
        respiratory_rate = marker_values.get("respiratory_rate")
        blood_oxygen_saturation = marker_values.get("blood_oxygen_saturation")
        body_weight_lbs = marker_values.get("body_weight_lbs")
        body_mass_index = marker_values.get("body_mass_index")

        # Convert date to a datetime object
        try:
            timestamp = datetime.strptime(date, "%Y-%m-%d %H:%M:%S %z")
        except ValueError as e:
            print(f"Error parsing marker date '{date}': {e}")
            continue

        # Get or create the common_data_id
        common_data_id = get_or_create_common_data_id(cursor, timestamp, source)

        # Check if a row already exists for this common_data_id
        cursor.execute("""
        SELECT 1 FROM health_markers WHERE common_data_id = ?
        """, (common_data_id,))
        if cursor.fetchone() is None:
            # Insert a new row
            cursor.execute("""
                INSERT INTO health_markers (
                    common_data_id, time_in_daylight_min, vo2_max, heart_rate, heart_rate_variability,
                    resting_heart_rate, respiratory_rate, blood_oxygen_saturation, body_mass_index, body_weight_lbs,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                common_data_id, time_in_daylight, vo2_max, heart_rate, heart_rate_variability,
                resting_heart_rate, respiratory_rate, blood_oxygen_saturation, body_mass_index, body_weight_lbs,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
        else:
            # Update the existing row
            cursor.execute("""
                UPDATE health_markers
                SET time_in_daylight_min = COALESCE(?, time_in_daylight_min),
                    vo2_max = COALESCE(?, vo2_max),
                    heart_rate = COALESCE(?, heart_rate),
                    heart_rate_variability = COALESCE(?, heart_rate_variability),
                    resting_heart_rate = COALESCE(?, resting_heart_rate),
                    respiratory_rate = COALESCE(?, respiratory_rate),
                    blood_oxygen_saturation = COALESCE(?, blood_oxygen_saturation),
                    body_mass_index = COALESCE(?, body_mass_index),
                    body_weight_lbs = COALESCE(?, body_weight_lbs),
                    updated_at = ?
                WHERE common_data_id = ?
            """, (
                time_in_daylight, vo2_max, heart_rate, heart_rate_variability, resting_heart_rate,
                respiratory_rate, blood_oxygen_saturation, body_mass_index, body_weight_lbs,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), common_data_id
            ))

def import_daily_data(data, conn):
    """
    Imports one day's worth of health data into the database.
    """
    cursor = conn.cursor()

    nutrition_metrics = [
        "calories", "protein", "carbohydrates_g", "fat_g", "water_floz", "caffeine_mg",
        "potassium_mg", "fiber_g", "sodium_mg", "sugar_g"]
    nutrition_data_grouped = {}

    markers_metrics = [
        "time_in_daylight", "vo2_max", "heart_rate", "heart_rate_variability", "resting_heart_rate",
        "respiratory_rate", "blood_oxygen_saturation", "body_weight_lbs", "body_mass_index"]
    markers_data_grouped = {}

    # Import metrics data
    for metric in data.get("metrics", []):
        metric_name = metric.get("name")
        metric_units = metric.get("units")
        metric_data = metric.get("data", [])
        # Translate metric name using the mapping
        metric_name = METRIC_NAME_MAPPING.get(metric_name, metric_name)
        print(f"Mapped Metric Name: {metric_name}, Original Name: {metric.get('name')}")
        insert_raw_data(cursor, metric_name, metric_units, metric_data)
        # Handle sleep_analysis specifically
        if metric_name == "sleep_analysis":
            pull_sleep_from_json(metric_data, cursor)

        elif metric_name in nutrition_metrics:
            print(f"Calling pull_nutrition_from_json for Metric: {metric_name}")
            pull_nutrition_from_json(metric_data, metric_name, cursor, nutrition_data_grouped)

        elif metric_name in markers_metrics:
            pull_markers_from_json(metric_data, metric_name, cursor, markers_data_grouped)

    # Commit the changes
    conn.commit()

def import_historical_data(json_file_path, target_date=None):
    """
    Loops through the JSON file and imports all historical data or data for a specific date into the database.
    :param json_file_path: Path to the JSON file containing historical data.
    :param target_date: Optional. A datetime.date object to filter data for a specific day.
    """
    if not os.path.exists(json_file_path):
        print(f"JSON file not found: {json_file_path}")
        return

    # Load the JSON file
    with open(json_file_path, "r") as file:
        health_data = json.load(file)

    # Filter data for the target date if provided
    if target_date:
        filtered_data = {
            "metrics": [
                {
                    "name": metric["name"],
                    "units": metric["units"],
                    "data": [
                        entry for entry in metric["data"]
                        if datetime.strptime(entry["date"], "%Y-%m-%d %H:%M:%S %z").date() == target_date
                    ],
                }
                for metric in health_data["data"]["metrics"]
            ]
        }
        health_data["data"] = filtered_data

    # Connect to the database
    conn = sqlite3.connect(DATABASE_NAME)

    # Import the data
    print(f"Importing health data for {target_date if target_date else 'all dates'}...")
    import_daily_data(health_data["data"], conn)

    # Close the connection
    conn.close()
    print("Data import complete.")

def import_historical_health_data(session: Session, health_data: list):
    """
    Imports historical health data into the database, aggregating by date.
    :param session: SQLAlchemy session object.
    :param health_data: List of health marker records to import.
    """
    # Step 1: Aggregate data by date
    aggregated_data = {}
    for record in health_data:
        date = record["date"]
        if date not in aggregated_data:
            aggregated_data[date] = {
                "heart_rate": [],
                "vo2_max": [],
                "body_weight_lbs": [],
                "body_mass_index": [],
                "respiratory_rate": [],
                "blood_oxygen_saturation": []
            }
        for key in aggregated_data[date]:
            if record.get(key) is not None:
                aggregated_data[date][key].append(record[key])

    # Step 2: Calculate averages for each date
    for date, metrics in aggregated_data.items():
        aggregated_data[date] = {
            "date": date,
            "heart_rate": sum(metrics["heart_rate"]) / len(metrics["heart_rate"]) if metrics["heart_rate"] else None,
            "vo2_max": sum(metrics["vo2_max"]) / len(metrics["vo2_max"]) if metrics["vo2_max"] else None,
            "body_weight_lbs": sum(metrics["body_weight_lbs"]) / len(metrics["body_weight_lbs"]) if metrics["body_weight_lbs"] else None,
            "body_mass_index": sum(metrics["body_mass_index"]) / len(metrics["body_mass_index"]) if metrics["body_mass_index"] else None,
            "respiratory_rate": sum(metrics["respiratory_rate"]) / len(metrics["respiratory_rate"]) if metrics["respiratory_rate"] else None,
            "blood_oxygen_saturation": sum(metrics["blood_oxygen_saturation"]) / len(metrics["blood_oxygen_saturation"]) if metrics["blood_oxygen_saturation"] else None,
        }

    # Step 3: Insert aggregated data into the database
    for date, metrics in aggregated_data.items():
        # Insert into common_data table
        common_data_id = session.execute(
            common_data.insert().values(date=metrics["date"]).returning(common_data.c.common_data_id)
        ).scalar()

        # Insert into health_markers_table
        session.execute(
            health_markers_table.insert().values(
                common_data_id=common_data_id,
                heart_rate=metrics["heart_rate"],
                vo2_max=metrics["vo2_max"],
                body_weight_lbs=metrics["body_weight_lbs"],
                body_mass_index=metrics["body_mass_index"],
                respiratory_rate=metrics["respiratory_rate"],
                blood_oxygen_saturation=metrics["blood_oxygen_saturation"]
            )
        )

    session.commit()

if __name__ == "__main__":
    # Import historical data
    target_date = date(2024, 4, 25)  # Set to a specific date if needed
    import_historical_data(JSON_FILE_PATH)


