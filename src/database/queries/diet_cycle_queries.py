from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, select, func
from sqlalchemy.types import DateTime, Date  # Correct import for DateTime and Date
import datetime
from src.database.schema import metadata, diet_cycles_table
from sqlalchemy import and_

def insert_diet_cycle_query(start_date, cycle_type, end_date=None, notes=None):
    return diet_cycles_table.insert().values(
        start_date=start_date,
        end_date=end_date,
        cycle_type=cycle_type,
        notes=notes
    )

def update_diet_cycle_end_date_query(cycle_id, end_date):
    return diet_cycles_table.update().where(diet_cycles_table.c.cycle_id == cycle_id).values(end_date=end_date)

def get_current_diet_cycle_query(on_date=None):
    from sqlalchemy import or_
    if on_date:
        return select(diet_cycles_table).\
            where(and_(diet_cycles_table.c.start_date <= on_date,
                       or_(diet_cycles_table.c.end_date >= on_date,
                           diet_cycles_table.c.end_date == None)))
    else:
        return select(diet_cycles_table).\
            where(diet_cycles_table.c.end_date == None).\
            order_by(diet_cycles_table.c.start_date.desc()).limit(1)

def get_all_diet_cycles_query(start_date=None, end_date=None):
    query = select(diet_cycles_table).order_by(diet_cycles_table.c.start_date.desc())
    conditions = []
    if start_date:
        conditions.append(diet_cycles_table.c.start_date >= start_date)
    if end_date:
        conditions.append(diet_cycles_table.c.start_date <= end_date)  # Assuming you filter by cycle start
    if conditions:
        query = query.where(and_(*conditions))
    return query

__all__ = [
    "insert_diet_cycle_query",
    "update_diet_cycle_end_date_query",
    "get_current_diet_cycle_query",
    "get_all_diet_cycles_query",
    # Add other functions here as needed
]