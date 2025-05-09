import streamlit as st
import pandas as pd
from datetime import date
import sys
import os

# Dynamically add the project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

DIET_CYCLES_CSV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/diet_cycles.csv"))
DIET_WEEKS_CSV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/diet_weeks.csv"))


from src.database.queries.hevy_sql_queries import (
    query_get_all_workouts,
    query_get_exercises_in_workout,
    query_get_sets_for_exercise_in_workout,
    query_get_all_unique_exercise_names,
    query_get_exercise_counts
)
from src.database.queries.sleep_queries import query_get_sleep_data
from src.database.queries.nutrition_queries import query_get_nutrition_data
from src.database.queries.health_markers_queries import query_get_health_markers
from src.database.queries.diet_cycles_queries import (
    query_get_current_diet_cycle,
    query_get_all_diet_cycles,
    query_insert_diet_cycle,
    query_insert_diet_week
)
from sqlalchemy.orm import Session
from src.database.connection import engine

# Create a database session
db = Session(bind=engine)

def set_query_params(**params):
    """Helper function to set query parameters."""
    st.query_params(**params)  # Updated to use st.query_params

'''def append_to_diet_weeks_csv(cycle_id, week_id, week_start_date, calorie_target, source):
    """Append a new diet week to the CSV file."""

    weeks_pd = pd.read_csv(DIET_WEEKS_CSV_FILE)
    new_row = {
        "cycle_id": cycle_id,
        "week_id": week_id,
        "week_start_date": week_start_date,
        "calorie_target": calorie_target,
        "common_data_source": source
    }
    '''

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Workouts", "Nutrition", "Sleep", "Health Markers", "Diet Cycles", "Data Input"])

if page == "Workouts":
    st.title("Workout Counts")
    start_date = st.sidebar.date_input("Start Date", value=date(2025, 1, 1))
    end_date = st.sidebar.date_input("End Date", value=date.today())
    workouts = query_get_all_workouts(start_date=start_date, end_date=end_date)
    if workouts:
        df_workouts = pd.DataFrame(workouts, columns=["Workout ID", "Title", "Start Time", "End Time"])
        st.dataframe(df_workouts)
    else:
        st.info("No workouts found for the selected date range.")

elif page == "Nutrition":
    st.title("Protein Per Day")
    start_date = st.sidebar.date_input("Start Date", value=date(2025, 1, 1))
    end_date = st.sidebar.date_input("End Date", value=date.today())
    nutrition_data = query_get_nutrition_data(start_date=start_date, end_date=end_date)

    if nutrition_data:
        column_names = ["Date", "Protein (g)", "Calories", "Carbohydrates (g)", "Fat (g)"]
        df_nutrition = pd.DataFrame(nutrition_data, columns=column_names)
        st.dataframe(df_nutrition)
        st.line_chart(df_nutrition.set_index("Date")["Protein (g)"])
    else:
        st.info("No nutrition data found for the selected date range.")

elif page == "Sleep":
    st.title("Sleep Analysis")
    start_date = st.sidebar.date_input("Start Date", value=date(2025, 1, 1))
    end_date = st.sidebar.date_input("End Date", value=date.today())
    sleep_data = query_get_sleep_data(start_date=start_date, end_date=end_date)

    if sleep_data:
        column_names = [
            "Date", "Source", "Start Time", "End Time", "In Bed Duration (hrs)", "Sleep Duration (hrs)",
            "Awake Duration (hrs)", "REM Sleep (hrs)", "Deep Sleep (hrs)", "Core Sleep (hrs)",
            "In Bed Start", "In Bed End"
        ]
        df_sleep = pd.DataFrame(sleep_data, columns=column_names)
        st.dataframe(df_sleep)
    else:
        st.info("No sleep data found for the selected date range.")

elif page == "Health Markers":
    st.title("Daily Health Markers")
    start_date = st.sidebar.date_input("Start Date", value=date(2025, 1, 1))
    end_date = st.sidebar.date_input("End Date", value=date.today())
    health_markers = query_get_health_markers(start_date=start_date, end_date=end_date)

    if health_markers:
        column_names = [
            "Date", "Heart Rate", "VO2 Max", "Body Weight (lbs)", "BMI",
            "Respiratory Rate", "Blood Oxygen Saturation"
        ]
        df_health = pd.DataFrame(health_markers, columns=column_names)
        st.dataframe(df_health)
    else:
        st.info("No health marker data found for the selected date range.")

elif page == "Diet Cycles":
    st.title("Diet Cycles")
    diet_cycles = query_get_all_diet_cycles()
    if diet_cycles:
        column_names = [
            "Cycle ID", "Common Data ID", "Start Date", "End Date", "Cycle Type",
            "Gain Rate (lbs/week)", "Loss Rate (lbs/week)", "Notes", "Created At", "Updated At"
        ]
        df_cycles = pd.DataFrame(diet_cycles, columns=column_names)
        st.dataframe(df_cycles)
    else:
        st.info("No diet cycle data found.")

elif page == "Data Input":
    st.title("Data Input")

    st.header("Start New Diet Cycle")
    with st.form("new_diet_cycle_form"):
        start_date = st.date_input("Start Date", date.today())
        cycle_type = st.selectbox("Cycle Type", ["bulk", "cut", "maintenance"])
        end_date = st.date_input("End Date (optional)", value=None)
        gain_rate = st.number_input("Gain Rate (lbs/week)", value=0.0, step=0.1)
        loss_rate = st.number_input("Loss Rate (lbs/week)", value=0.0, step=0.1)
        notes = st.text_input("Notes (optional)")
        submitted_start = st.form_submit_button("Start Cycle")
        if submitted_start:
            query_insert_diet_cycle(start_date, cycle_type, notes=notes)
            st.success("Diet cycle added successfully.")
            set_query_params(page="Data Input")  # Use helper function

    st.header("Add Diet Week")
    with st.form("add_diet_week_form"):
        week_start_date = st.date_input("Week Start Date", date.today())
        calorie_target = st.number_input("Calorie Target", value=0.0, step=1.0)
        source = 'streamlit form'
        submitted_week = st.form_submit_button("Add Week")
        if submitted_week:
            current_cycle = query_get_current_diet_cycle()
            if current_cycle:
                cycle_id = current_cycle.cycle_id

                # Check if the common_data entry already exists
                existing_common_data = db.execute(
                    "SELECT common_data_id FROM common_data WHERE date = :date AND source = :source",
                    {"date": week_start_date.strftime("%Y-%m-%d %H:%M:%S"), "source": source}
                ).fetchone()

                if existing_common_data:
                    st.error("A diet week with the same date and source already exists.")
                else:
                    query_insert_diet_week(
                        cycle_id=cycle_id,
                        week_start_date=week_start_date,
                        calorie_target=calorie_target,
                        source=source
                    )
                    st.success("Diet week added successfully.")
                    set_query_params(page="Data Input")  # Use helper function
            else:
                st.error("No ongoing diet cycle found. Please start a new cycle first.")

db.close()