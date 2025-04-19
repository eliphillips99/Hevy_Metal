# workout-analytics/database_utils.py
import sqlite3
import os

# Dynamically construct the path to the database file in the 'data' directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_NAME = os.path.join(BASE_DIR, "data", "hevy_metal.db")

def get_connection():
    """Establishes and returns a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        conn.row_factory = sqlite3.Row  # Access columns by name
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def close_connection(conn):
    """Closes the database connection."""
    if conn:
        conn.close()

def execute_query(query, params=()):
    """Executes an SQL query and returns the results."""
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            conn.commit()  # For INSERT, UPDATE, DELETE
            return results
        except sqlite3.Error as e:
            print(f"Database query error: {e}")
            return None
        finally:
            close_connection(conn)
    return None

def fetch_one(query, params=()):
    """Executes an SQL query and returns the first result."""
    results = execute_query(query, params)
    if results:
        return results[0]
    return None

def fetch_all(query, params=()):
    """Executes an SQL query and returns all results."""
    return execute_query(query, params)

if __name__ == "__main__":
    # Example usage (optional)
    unique_exercises = fetch_all("SELECT DISTINCT exercise_name FROM exercises;")
    if unique_exercises:
        print("Unique Exercises:")
        for row in unique_exercises:
            print(row['exercise_name'])