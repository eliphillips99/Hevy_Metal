from sqlalchemy import select, and_
from src.database.schema import health_markers_table

def get_health_markers_query(start_date=None, end_date=None):
    query = select(
        health_markers_table.c.created_at.label("Date"),
        health_markers_table.c.heart_rate.label("Heart Rate"),
        health_markers_table.c.vo2_max.label("VO2 Max"),
        health_markers_table.c.body_weight_lbs.label("Body Weight (lbs)"),
        health_markers_table.c.body_mass_index.label("BMI")
    ).order_by(health_markers_table.c.created_at)

    if start_date or end_date:
        conditions = []
        if start_date:
            conditions.append(health_markers_table.c.created_at >= start_date)
        if end_date:
            conditions.append(health_markers_table.c.created_at <= end_date)
        query = query.where(and_(*conditions))

    return query
