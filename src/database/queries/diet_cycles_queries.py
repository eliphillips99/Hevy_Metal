from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session
from datetime import date, datetime  # Import `date` for date operations and `datetime` for timestamps
from src.database.schema import diet_cycles_table, diet_weeks_table, common_data  # Import the `common_data` table
from src.database.connection import engine  # Assuming `engine` is defined in a connection module
import pandas as pd  # Import pandas for CSV operations
import os  # Import os for file path operations
from src.database.database_utils import apply_date_filter

# Initialize the database session
db = Session(bind=engine)

DIET_CYCLES_CSV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/diet_cycles.csv"))
DIET_WEEKS_CSV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/diet_weeks.csv"))

def query_get_current_diet_cycle(reference_date=None):
    """
    Fetch the most recent ongoing diet cycle.
    :param reference_date: Optional. The date to check for an active cycle. Defaults to today.
    :return: Query result.
    """
    if reference_date is None:
        reference_date = date.today()  # Use `date.today()` to get the current date

    query = select(diet_cycles_table).where(
        or_(
            diet_cycles_table.c.end_date == None,
            diet_cycles_table.c.end_date >= reference_date
        ),
        diet_cycles_table.c.start_date <= reference_date
    ).order_by(diet_cycles_table.c.start_date.desc()).limit(1)

    return db.execute(query).fetchone()

def query_get_all_diet_cycles(start_date=None, end_date=None):
    """
    Fetch all diet cycles within the specified date range.
    :param start_date: The start date for filtering (inclusive).
    :param end_date: The end date for filtering (inclusive).
    :return: A list of diet cycles.
    """
    query = select(diet_cycles_table).order_by(diet_cycles_table.c.start_date.desc())
    query = apply_date_filter(query, diet_cycles_table, start_date, end_date, date_column='start_date')
    return db.execute(query).fetchall()  # Execute the query and fetch results as a list

def query_insert_common_data(record_date, source=None):
    """Insert a record into the common_data table or return the existing common_data_id."""

    try:
        # Debugging: Log the raw record_date
        print(f"Debug: Raw record_date: {record_date}")

        # Ensure the date is in the correct format
        if isinstance(record_date, date) and not isinstance(record_date, datetime):
            record_date = datetime.combine(record_date, datetime.min.time())  # Convert date to datetime
        elif not isinstance(record_date, datetime):
            raise ValueError(f"Invalid record_date: {record_date}. Must be a datetime or date object.")

        # Debugging: Log the formatted record_date
        print(f"Debug: Formatted record_date: {record_date}")

        # Check if the record already exists
        existing_record = db.execute(
            select(common_data.c.common_data_id).where(
                common_data.c.date == record_date,
                common_data.c.source == source
            )
        ).fetchone()

        if existing_record:
            # Debugging: Log that the record already exists
            print(f"Debug: Found existing common_data_id={existing_record.common_data_id}")
            return existing_record.common_data_id

        # Insert a new record if it doesn't exist
        print(f"Debug: Inserting into common_data with date={record_date}, source={source}")
        result = db.execute(
            common_data.insert(),
            {"date": record_date, "source": source}
        )
        db.commit()

        # Debugging: Log the newly inserted record
        print(f"Debug: Inserted new common_data_id={result.inserted_primary_key[0]}")
        return result.inserted_primary_key[0]
    except Exception as e:
        # Debugging: Log any errors
        print(f"Error in query_insert_common_data: {e}")
        db.rollback()
        raise

def update_diet_weeks_csv():
    """Fetch all diet weeks and update the diet_weeks.csv file."""
    try:
        # Debugging: Log the start of the CSV update process
        print("Debug: Starting CSV update for diet_weeks.")

        # Corrected select statement
        query = select(
            diet_weeks_table.c.week_id,
            diet_weeks_table.c.cycle_id,
            diet_weeks_table.c.common_data_id,
            diet_weeks_table.c.week_start_date,
            diet_weeks_table.c.calorie_target,
            common_data.c.source.label("common_data_source")  # Include common_data.source
        ).join(
            common_data, diet_weeks_table.c.common_data_id == common_data.c.common_data_id
        )
        result = db.execute(query).fetchall()

        # Debugging: Log the number of rows fetched
        print(f"Debug: Fetched {len(result)} rows from diet_weeks_table.")

        # Convert result to DataFrame
        df = pd.DataFrame(result, columns=[
            "week_id", "cycle_id", "common_data_id", "week_start_date", "calorie_target", 
            "common_data_source"
        ])

        # Write to CSV
        df.to_csv(DIET_WEEKS_CSV_FILE, index=False)

        # Debugging: Log successful CSV update
        print(f"Debug: CSV updated successfully at {DIET_WEEKS_CSV_FILE}.")
    except Exception as e:
        # Debugging: Log any errors during the CSV update process
        print(f"Error updating diet_weeks.csv: {e}")

def query_insert_diet_week(cycle_id, week_start_date, calorie_target, source=None):
    """Insert a new diet week into the diet_weeks table and update the CSV file."""
    try:
        # Generate a common_data_id
        print(f"Debug: week_start_date before calling query_insert_common_data: {week_start_date}")
        common_data_id = query_insert_common_data(record_date=week_start_date, source=source)

        # Insert into diet_weeks_table with timestamps
        current_time = datetime.utcnow()
        db.execute(
            diet_weeks_table.insert().values(
                cycle_id=cycle_id,
                common_data_id=common_data_id,
                week_start_date=week_start_date,
                calorie_target=calorie_target,
                source=source,  # Ensure source is populated
                created_at=current_time,
                updated_at=current_time
            )
        )
        db.commit()  # Ensure changes are committed to the database

        # Debugging: Log successful insertion
        print(f"Debug: Inserted diet week with cycle_id={cycle_id}, week_start_date={week_start_date}, calorie_target={calorie_target}, source={source}.")

        # Update the diet_weeks.csv file
        update_diet_weeks_csv()
    except Exception as e:
        # Debugging: Log any errors during the insertion process
        print(f"Error inserting diet week: {e}")
        db.rollback()  # Rollback in case of an error

def query_get_diet_weeks(diet_cycle_id):
    query = select(diet_weeks_table).where(diet_weeks_table.c.diet_cycle_id == diet_cycle_id)
    return db.execute(query).fetchall()
    return db.execute(query).fetchall()