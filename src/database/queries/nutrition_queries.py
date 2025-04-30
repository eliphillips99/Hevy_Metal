from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from src.database.schema import nutrition_data_table, common_data
from src.database.connection import engine  # Assuming `engine` is defined in a connection module

# Initialize the database session
db = Session(bind=engine)

def query_get_nutrition_data(start_date=None, end_date=None):
    # Join nutrition_data_table with common_data to filter by date
    query = select(
        common_data.c.date.label("Date"),
        nutrition_data_table.c.protein_g.label("Protein (g)"),
        nutrition_data_table.c.calories.label("Calories"),
        nutrition_data_table.c.carbohydrates_g.label("Carbohydrates (g)"),
        nutrition_data_table.c.fat_g.label("Fat (g)")
    ).join(
        common_data, nutrition_data_table.c.common_data_id == common_data.c.common_data_id
    ).order_by(common_data.c.date)

    if start_date or end_date:
        conditions = []
        if start_date:
            conditions.append(common_data.c.date >= start_date)
        if end_date:
            conditions.append(common_data.c.date <= end_date)
        query = query.where(and_(*conditions))

    return db.execute(query).fetchall()
