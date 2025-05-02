import pandas as pd
import sqlite3
from datetime import datetime
import os
import uuid  # Add this import for generating unique IDs
from dateutil.parser import parse  # Add this import for flexible date parsing
from src.database.database_utils import get_or_create_common_data_id

# Path to your SQLite database
DATABASE_NAME = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/hevy_metal.db"))

# Function to import diet cycles from a CSV file
def import_diet_cycles_from_csv(csv_file_path):
    # Read the CSV file into a pandas DataFrame
    try:
        df = pd.read_csv(csv_file_path)
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # Ensure required columns are present
    required_columns = ["common_data_id", "start_date", "cycle_type"]
    for col in required_columns:
        if col not in df.columns:
            if (col == "common_data_id"):
                print("common_data_id column is missing. Generating unique IDs for each row.")
                df["common_data_id"] = [str(uuid.uuid4()) for _ in range(len(df))]
            else:
                print(f"Missing required column: {col}")
                return

    # Optional columns
    optional_columns = ["end_date", "gain_rate_lbs_per_week", "loss_rate_lbs_per_week", "notes"]

    # Connect to the SQLite database
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Iterate through the DataFrame and insert rows into the diet_cycles table
    for _, row in df.iterrows():
        try:
            # Parse dates using dateutil.parser.parse for flexibility
            start_date = parse(row["start_date"]).date()
            end_date = parse(row["end_date"]).date() if "end_date" in row and not pd.isna(row["end_date"]) else None

            # Get or create common_data_id
            common_data_id = get_or_create_common_data_id(cursor, start_date)

            # Prepare the SQL query
            cursor.execute("""
                INSERT INTO diet_cycles (
                    common_data_id, start_date, end_date, cycle_type, gain_rate_lbs_per_week,
                    loss_rate_lbs_per_week, notes, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                common_data_id,
                start_date,
                end_date,
                row["cycle_type"],
                row.get("gain_rate_lbs_per_week"),
                row.get("loss_rate_lbs_per_week"),
                row.get("notes"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
        except Exception as e:
            print(f"Error inserting row: {row.to_dict()}, Error: {e}")

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()
    print("Diet cycles imported successfully.")

# Example usage
if __name__ == "__main__":
    csv_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/diet_cycles.csv"))  # Replace with the path to your CSV file
    import_diet_cycles_from_csv(csv_file_path)