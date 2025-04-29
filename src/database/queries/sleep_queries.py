from sqlalchemy import select, and_
from src.database.schema import sleep_data_table, common_data

def get_sleep_data_query(start_date=None, end_date=None):
    # Debugging: Log the input parameters
    print(f"get_sleep_data_query called with start_date={start_date}, end_date={end_date}")

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

    return query
