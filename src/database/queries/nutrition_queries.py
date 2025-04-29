from sqlalchemy import select, and_
from src.database.schema import nutrition_data_table

def get_nutrition_data_query(start_date=None, end_date=None):
    query = select(
        nutrition_data_table.c.timestamp.label("Date"),
        nutrition_data_table.c.protein_g.label("Protein (g)")
    ).order_by(nutrition_data_table.c.timestamp)

    if start_date or end_date:
        conditions = []
        if start_date:
            conditions.append(nutrition_data_table.c.timestamp >= start_date)
        if end_date:
            conditions.append(nutrition_data_table.c.timestamp <= end_date)
        query = query.where(and_(*conditions))

    return query
