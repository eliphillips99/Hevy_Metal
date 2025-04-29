from sqlalchemy import select, and_
from src.database.schema import sleep_data_table

def get_sleep_data_query(start_date=None, end_date=None):
    query = select(
        sleep_data_table.c.start_time.label("Date"),
        sleep_data_table.c.awake_duration_hours.label("Awake Duration (hrs)"),
        sleep_data_table.c.rem_sleep_duration_hours.label("REM Sleep (hrs)"),
        sleep_data_table.c.deep_sleep_duration_hours.label("Deep Sleep (hrs)"),
        sleep_data_table.c.core_sleep_duration_hours.label("Core Sleep (hrs)"),
        sleep_data_table.c.in_bed_duration_hours.label("In Bed Duration (hrs)"),
        sleep_data_table.c.in_bed_start.label("In Bed Start"),
        sleep_data_table.c.in_bed_end.label("In Bed End")
    )
    # Apply conditions for start_date and end_date if provided
    if start_date or end_date:
        conditions = []
        if start_date:
            conditions.append(sleep_data_table.c.start_time >= start_date)
        if end_date:
            conditions.append(sleep_data_table.c.start_time <= end_date)
        query = query.where(and_(*conditions))
    return query.order_by(sleep_data_table.c.start_time)
