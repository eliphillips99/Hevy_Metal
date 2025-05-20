from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session
from src.database.schema import sleep_data_table, common_data
from src.database.connection import engine  # Assuming `engine` is defined in a connection module

# Initialize the database session
db = Session(bind=engine)

def query_get_sleep_data(start_date=None, end_date=None):
    # Debugging: Log the input parameters
    print(f"query_get_sleep_data called with start_date={start_date}, end_date={end_date}")

    # Join sleep_data_table with common_data to include the source column
    query = select(
        common_data.c.date.label("Date"),
        common_data.c.source.label("Source"),
        sleep_data_table.c.start_time.label("Start Time"),
        sleep_data_table.c.end_time.label("End Time"),
        sleep_data_table.c.in_bed_duration_hours.label("In Bed Duration (hrs)"),
        sleep_data_table.c.sleep_duration_hours.label("Sleep Duration (hrs)"),
        sleep_data_table.c.awake_duration_hours.label("Awake Duration (hrs)"),
        sleep_data_table.c.rem_sleep_duration_hours.label("REM Sleep (hrs)"),
        sleep_data_table.c.deep_sleep_duration_hours.label("Deep Sleep (hrs)"),
        sleep_data_table.c.core_sleep_duration_hours.label("Core Sleep (hrs)"),
        sleep_data_table.c.in_bed_start.label("In Bed Start"),
        sleep_data_table.c.in_bed_end.label("In Bed End")
    ).join(
        common_data, sleep_data_table.c.common_data_id == common_data.c.common_data_id
    ).order_by(
        common_data.c.date, common_data.c.source
    )

    if start_date or end_date:
        conditions = []
        if start_date:
            conditions.append(common_data.c.date >= start_date)
        if end_date:
            conditions.append(common_data.c.date <= end_date)
        query = query.where(and_(*conditions))

    # Debugging: Log the generated query
    print("Generated Sleep Data Query:")
    print(query)

    return db.execute(query).fetchall()

def query_get_sleep_stats(start_date=None, end_date=None):
    """
    Query to calculate average duration for each sleep cycle and average total sleep time.
    """
    query = select(
        func.avg(sleep_data_table.c.rem_sleep_duration_hours).label("Avg REM Sleep (hrs)"),
        func.avg(sleep_data_table.c.deep_sleep_duration_hours).label("Avg Deep Sleep (hrs)"),
        func.avg(sleep_data_table.c.core_sleep_duration_hours).label("Avg Core Sleep (hrs)"),
        func.avg(sleep_data_table.c.awake_duration_hours).label("Avg Awake Time (hrs)"),
        func.avg(sleep_data_table.c.sleep_duration_hours).label("Avg Total Sleep (hrs)")  # Average of sleep_duration_hours
    ).join(
        common_data, sleep_data_table.c.common_data_id == common_data.c.common_data_id
    )

    if start_date or end_date:
        conditions = []
        if start_date:
            conditions.append(common_data.c.date >= start_date)
        if end_date:
            conditions.append(common_data.c.date <= end_date)
        query = query.where(and_(*conditions))

    # Debugging: Log the generated query
    print("Generated Sleep Stats Query:")
    print(query)

    return db.execute(query).fetchone()

def query_get_sleep_cycle_percentages(start_date=None, end_date=None):
    """
    Query to calculate the average percentage of time spent in each sleep cycle per night.
    """
    query = select(
        func.avg((sleep_data_table.c.rem_sleep_duration_hours / sleep_data_table.c.sleep_duration_hours) * 100).label("Avg REM Sleep (%)"),
        func.avg((sleep_data_table.c.deep_sleep_duration_hours / sleep_data_table.c.sleep_duration_hours) * 100).label("Avg Deep Sleep (%)"),
        func.avg((sleep_data_table.c.core_sleep_duration_hours / sleep_data_table.c.sleep_duration_hours) * 100).label("Avg Core Sleep (%)"),
        func.avg((sleep_data_table.c.awake_duration_hours / sleep_data_table.c.sleep_duration_hours) * 100).label("Avg Awake Time (%)")
    ).join(
        common_data, sleep_data_table.c.common_data_id == common_data.c.common_data_id
    ).where(
        sleep_data_table.c.sleep_duration_hours > 0  # Avoid division by zero
    )

    if start_date or end_date:
        conditions = []
        if start_date:
            conditions.append(common_data.c.date >= start_date)
        if end_date:
            conditions.append(common_data.c.date <= end_date)
        query = query.where(and_(*conditions))

    # Debugging: Log the generated query
    print("Generated Sleep Cycle Percentages Query:")
    print(query)

    return db.execute(query).fetchone()
