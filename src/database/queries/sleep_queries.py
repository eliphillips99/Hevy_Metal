from sqlalchemy import select, and_
from src.database.schema import sleep_data_table

def get_sleep_data_query(start_date=None, end_date=None):
    query = select(
        sleep_data_table.c.start_time.label("Date"),
        sleep_data_table.c.sleep_duration_hours.label("Sleep Duration (hrs)"),
        sleep_data_table.c.rem_sleep_duration_hours.label("REM Sleep (hrs)"),
        sleep_data_table.c.deep_sleep_duration_hours.label("Deep Sleep (hrs)")
    ).order_by(sleep_data_table.c.start_time)

    if start_date or end_date:
        conditions = []
        if start_date:
            conditions.append(sleep_data_table.c.start_time >= start_date)
        if end_date:
            conditions.append(sleep_data_table.c.start_time <= end_date)
        query = query.where(and_(*conditions))

    return query
