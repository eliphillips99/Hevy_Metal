from sqlalchemy import select, and_, or_
from sqlalchemy.orm import Session
from src.database.schema import diet_cycles_table, diet_weeks_table
from src.database.connection import engine  # Assuming `engine` is defined in a connection module

# Initialize the database session
db = Session(bind=engine)

def query_insert_diet_cycle(start_date, cycle_type, end_date=None, notes=None):
    return db.execute(
        diet_cycles_table.insert().values(
            start_date=start_date,
            end_date=end_date,
            cycle_type=cycle_type,
            notes=notes
        )
    )

def query_update_diet_cycle_end_date(cycle_id, end_date):
    return db.execute(
        diet_cycles_table.update().where(
            diet_cycles_table.c.cycle_id == cycle_id
        ).values(end_date=end_date)
    )

def query_get_current_diet_cycle(reference_date=None):
    """
    Fetch the most recent ongoing diet cycle.
    :param reference_date: Optional. The date to check for an active cycle. Defaults to today.
    :return: Query result.
    """
    if reference_date is None:
        reference_date = date.today()

    query = select(diet_cycles_table).where(
        or_(
            diet_cycles_table.c.end_date == None,
            diet_cycles_table.c.end_date >= reference_date
        ),
        diet_cycles_table.c.start_date <= reference_date
    ).order_by(diet_cycles_table.c.start_date.desc()).limit(1)

    return db.execute(query).fetchone()

def query_get_all_diet_cycles(start_date=None, end_date=None):
    query = select(diet_cycles_table).order_by(diet_cycles_table.c.start_date.desc())
    if start_date or end_date:
        conditions = []
        if start_date:
            conditions.append(diet_cycles_table.c.start_date >= start_date)
        if end_date:
            conditions.append(diet_cycles_table.c.start_date <= end_date)
        query = query.where(and_(*conditions))
    return db.execute(query).fetchall()

def query_insert_diet_week(diet_cycle_id, week_start_date, calorie_target):
    return db.execute(
        diet_weeks_table.insert().values(
            diet_cycle_id=diet_cycle_id,
            week_start_date=week_start_date,
            calorie_target=calorie_target
        )
    )

def query_get_diet_weeks(diet_cycle_id):
    query = select(diet_weeks_table).where(diet_weeks_table.c.diet_cycle_id == diet_cycle_id)
    return db.execute(query).fetchall()