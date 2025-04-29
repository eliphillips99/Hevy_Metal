from sqlalchemy import select, and_, or_
from src.database.schema import diet_cycles_table

def insert_diet_cycle_query(start_date, cycle_type, end_date=None, notes=None):
    return diet_cycles_table.insert().values(
        start_date=start_date,
        end_date=end_date,
        cycle_type=cycle_type,
        notes=notes
    )

def update_diet_cycle_end_date_query(cycle_id, end_date):
    return diet_cycles_table.update().where(
        diet_cycles_table.c.cycle_id == cycle_id
    ).values(end_date=end_date)

def get_current_diet_cycle_query(on_date=None):
    if on_date:
        return select(diet_cycles_table).where(
            and_(
                diet_cycles_table.c.start_date <= on_date,
                or_(
                    diet_cycles_table.c.end_date >= on_date,
                    diet_cycles_table.c.end_date == None
                )
            )
        )
    return select(diet_cycles_table).where(
        diet_cycles_table.c.end_date == None
    ).order_by(diet_cycles_table.c.start_date.desc()).limit(1)

def get_all_diet_cycles_query(start_date=None, end_date=None):
    query = select(diet_cycles_table).order_by(diet_cycles_table.c.start_date.desc())
    if start_date or end_date:
        conditions = []
        if start_date:
            conditions.append(diet_cycles_table.c.start_date >= start_date)
        if end_date:
            conditions.append(diet_cycles_table.c.start_date <= end_date)
        query = query.where(and_(*conditions))
    return query
