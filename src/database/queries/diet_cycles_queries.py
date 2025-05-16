from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session
from datetime import date, datetime  # Import `date` for date operations and `datetime` for timestamps
from src.database.schema import diet_cycles_table, diet_weeks_table, common_data  # Import the `common_data` table
from src.database.connection import engine  # Assuming `engine` is defined in a connection module
import pandas as pd  # Import pandas for CSV operations
import os  # Import os for file path operations

# Initialize the database session
db = Session(bind=engine)

DIET_CYCLES_CSV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/diet_cycles.csv"))
DIET_WEEKS_CSV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/diet_weeks.csv"))

def query_insert_diet_cycle(start_date, cycle_type, end_date=None, notes=None):
    return db.execute(
        diet_cycles_table.insert().values(
            start_date=start_date,
            end_date=end_date,
            cycle_type=cycle_type,
            notes=notes
        )
    )

def query_update_diet_cycle_end_date(cycle_id, end_date):
    return db.execute(
        diet_cycles_table.update().where(
            diet_cycles_table.c.cycle_id == cycle_id
        ).values(end_date=end_date)
    )

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
    query = select(diet_cycles_table).order_by(diet_cycles_table.c.start_date.desc())
    if start_date or end_date:
        conditions = []
        if start_date:
            conditions.append(diet_cycles_table.c.start_date >= start_date)
        if end_date:
            conditions.append(diet_cycles_table.c.start_date <= end_date)
        query = query.where(and_(*conditions))
    return db.execute(query).fetchall()

def query_insert_common_data(date, source=None):
    """Insert a record into the common_data table and return the generated common_data_id."""
    result = db.execute(
        common_data.insert().values(
            date=date,
            source=source
        )
    )
    db.commit()
    return result.inserted_primary_key[0]

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
        common_data_id = query_insert_common_data(date=week_start_date, source=source)

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