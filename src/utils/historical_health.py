import os
import json
import sqlite3

def import_apple_health_data(json_file_path, db_path):
    # Load JSON data
    with open(json_file_path, 'r') as file:
        health_data = json.load(file)

    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Ensure the table exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS apple_health_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            value REAL,
            unit TEXT,
            start_date TEXT,
            end_date TEXT
        )
    ''')

    # Insert data into the table
    for record in health_data:
        cursor.execute('''
            INSERT INTO apple_health_data (type, value, unit, start_date, end_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (record.get('type'), record.get('value'), record.get('unit'), record.get('start_date'), record.get('end_date')))

    # Commit changes and close the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    # Define paths
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    json_file_path = os.path.join(data_dir, 'apple_health_data.json')
    db_path = os.path.join(os.path.dirname(__file__), '..', 'hevy_metal.db')

    # Import data
    import_apple_health_data(json_file_path, db_path)
