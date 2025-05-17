from sqlalchemy import select, and_, func
from sqlalchemy.orm import Session
from src.database.schema import health_markers_table, common_data
from src.database.connection import engine  # Assuming `engine` is defined in a connection module

# Initialize the database session
db = Session(bind=engine)

def query_get_health_markers(start_date=None, end_date=None):
    # Join health_markers_table with common_data to filter by date
    query = select(
        common_data.c.date.label("Date"),
        health_markers_table.c.heart_rate_min.label("Heart Rate Min"),
        health_markers_table.c.heart_rate_max.label("Heart Rate Max"),
        health_markers_table.c.heart_rate_avg.label("Heart Rate Avg"),
        health_markers_table.c.vo2_max.label("VO2 Max"),
        health_markers_table.c.body_weight_lbs.label("Body Weight (lbs)"),
        health_markers_table.c.body_mass_index.label("BMI"),
        health_markers_table.c.respiratory_rate.label("Respiratory Rate"),
        health_markers_table.c.blood_oxygen_saturation.label("Blood Oxygen Saturation"),
        health_markers_table.c.time_in_daylight_min.label("Time in Daylight (min)")
    ).join(
        common_data, health_markers_table.c.common_data_id == common_data.c.common_data_id
    ).order_by(
        common_data.c.date
    )

    if start_date or end_date:
        conditions = []
        if start_date:
            conditions.append(common_data.c.date >= start_date)
        if end_date:
            conditions.append(common_data.c.date <= end_date)
        query = query.where(and_(*conditions))

    return db.execute(query).fetchall()

def query_get_aggregated_health_markers(start_date=None, end_date=None):
    """
    Aggregates health marker data by date, combining data from multiple sources.
    """
    query = select(
        func.date(common_data.c.date).label("Date"),
        func.avg(health_markers_table.c.heart_rate_avg).label("Heart Rate Avg"),
        func.min(health_markers_table.c.heart_rate_min).label("Heart Rate Min"),
        func.max(health_markers_table.c.heart_rate_max).label("Heart Rate Max"),
        func.avg(health_markers_table.c.vo2_max).label("VO2 Max"),
        func.avg(health_markers_table.c.body_weight_lbs).label("Body Weight (lbs)"),
        func.avg(health_markers_table.c.body_mass_index).label("BMI"),
        func.avg(health_markers_table.c.respiratory_rate).label("Respiratory Rate"),
        func.avg(health_markers_table.c.blood_oxygen_saturation).label("Blood Oxygen Saturation"),
        func.sum(health_markers_table.c.time_in_daylight_min).label("Time in Daylight (min)")
    ).join(
        common_data, health_markers_table.c.common_data_id == common_data.c.common_data_id
    ).group_by(
        func.date(common_data.c.date)
    ).order_by(
        func.date(common_data.c.date)
    )

    if start_date or end_date:
        conditions = []
        if start_date:
            conditions.append(common_data.c.date >= start_date)
        if end_date:
            conditions.append(common_data.c.date <= end_date)
        query = query.where(and_(*conditions))

    return db.execute(query).fetchall()
