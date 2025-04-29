from sqlalchemy import select, and_
from src.database.schema import health_markers_table, common_data  # Use the correct table name

def get_health_markers_query(start_date=None, end_date=None):
    # Debugging: Log the input parameters
    print(f"get_health_markers_query called with start_date={start_date}, end_date={end_date}")

    # Join health_markers_table with common_data to filter by date
    query = select(
        common_data.c.date.label("Date"),
        health_markers_table.c.heart_rate.label("Heart Rate"),
        health_markers_table.c.vo2_max.label("VO2 Max"),
        health_markers_table.c.body_weight_lbs.label("Body Weight (lbs)"),
        health_markers_table.c.body_mass_index.label("BMI"),
        health_markers_table.c.respiratory_rate.label("Respiratory Rate"),
        health_markers_table.c.blood_oxygen_saturation.label("Blood Oxygen Saturation")
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

    # Debugging: Log the generated query
    print("Generated Health Markers Query:")
    print(query)

    return query
