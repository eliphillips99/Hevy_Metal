# workout-analytics/database_utils.py
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

DATABASE_NAME = "hevy_metal.db"
engine = create_engine(f'sqlite:///{DATABASE_NAME}')
metadata = MetaData() # You might define your tables here or in queries.py

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def execute_sqlalchemy_query(db, query):
    """Executes a SQLAlchemy query object."""
    result = db.execute(query).fetchall()
    return result

# Import all functions from hevy_sql_queries
from hevy_sql_queries import *

# Example usage
if __name__ == "__main__":
    db = next(get_db())
    exercise_counts_results = execute_sqlalchemy_query(db, get_exercise_counts_query())
    if exercise_counts_results:
        print("Exercise Counts:")
        for row in exercise_counts_results:
            print(f"{row.exercise_name}: {row.occurrence_count}")