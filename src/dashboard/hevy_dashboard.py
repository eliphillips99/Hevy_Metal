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

from src.database.database_utils import *

# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Workouts", "Nutrition", "Sleep", "Health Markers", "Diet Cycles"])

# Create a database session
db = next(get_db())

if page == "Workouts":
    st.title("Workout Counts")
    start_date = st.sidebar.date_input("Start Date", value=date(2025, 1, 1))
    end_date = st.sidebar.date_input("End Date", value=date.today())
    workouts = get_all_workouts(db, start_date=start_date, end_date=end_date)
    if workouts:
        df_workouts = pd.DataFrame(workouts, columns=["Workout ID", "Title", "Start Time", "End Time"])
        st.dataframe(df_workouts)
    else:
        st.info("No workouts found for the selected date range.")

elif page == "Nutrition":
    st.title("Protein Per Day")
    start_date = st.sidebar.date_input("Start Date", value=date(2025, 1, 1))
    end_date = st.sidebar.date_input("End Date", value=date.today())
    nutrition_data = get_nutrition_data(db, start_date=start_date, end_date=end_date)

    # Debugging: Log raw query results
    st.write("Debug: Raw Nutrition Data", nutrition_data)

    if nutrition_data:
        # Ensure all columns from the query are included
        column_names = ["Date", "Protein (g)", "Calories", "Carbohydrates (g)", "Fat (g)"]
        if len(nutrition_data[0]) != len(column_names):
            st.error(f"Mismatch in column count: Expected {len(column_names)}, but got {len(nutrition_data[0])}")
        else:
            df_nutrition = pd.DataFrame(nutrition_data, columns=column_names)
            st.dataframe(df_nutrition)
            st.line_chart(df_nutrition.set_index("Date")["Protein (g)"])
    else:
        st.info("No nutrition data found for the selected date range.")

elif page == "Sleep":
    st.title("Sleep Analysis")
    start_date = st.sidebar.date_input("Start Date", value=date(2025, 1, 1))
    end_date = st.sidebar.date_input("End Date", value=date.today())
    sleep_data = get_sleep_data(db, start_date=start_date, end_date=end_date)

    # Debugging the structure of the returned data
    st.write("Debug: Sleep Data Structure", sleep_data[0])

    if sleep_data:
        # Updated column names to include Date, Start Time, and End Time
        column_names = [
            "Date", "Source", "Start Time", "End Time", "In Bed Duration (hrs)", "Sleep Duration (hrs)",
            "Awake Duration (hrs)", "REM Sleep (hrs)", "Deep Sleep (hrs)", "Core Sleep (hrs)",
            "In Bed Start", "In Bed End"
        ]
        if len(sleep_data[0]) != len(column_names):
            st.error(f"Mismatch in column count: Expected {len(column_names)}, but got {len(sleep_data[0])}")
        else:
            df_sleep = pd.DataFrame(sleep_data, columns=column_names)
            st.dataframe(df_sleep)
    else:
        st.info("No sleep data found for the selected date range.")

elif page == "Health Markers":
    st.title("Daily Health Markers")
    start_date = st.sidebar.date_input("Start Date", value=date(2025, 1, 1))
    end_date = st.sidebar.date_input("End Date", value=date.today())
    health_markers = get_health_markers(db, start_date=start_date, end_date=end_date)

    # Debugging: Log raw query results
    st.write("Debug: Raw Health Markers Data", health_markers)

    if health_markers:
        # Ensure all columns from the query are included
        column_names = [
            "Date", "Time in Daylight (min)", "Heart Rate", "VO2 Max", "Body Weight (lbs)", "BMI",
            "Heart Rate Variability", "Resting Heart Rate", "Respiratory Rate", "Blood Oxygen Saturation"
        ]
        if len(health_markers[0]) != len(column_names):
            st.error(f"Mismatch in column count: Expected {len(column_names)}, but got {len(health_markers[0])}")
        else:
            df_health = pd.DataFrame(health_markers, columns=column_names)
            st.dataframe(df_health)
    else:
        st.info("No health marker data found for the selected date range.")

elif page == "Diet Cycles":
    st.title("Diet Cycles")
    diet_cycles = get_all_diet_cycles(db)
    if diet_cycles:
        # Log the structure of the data for debugging

        # Explicitly define the columns based on the schema structure
        column_names = [
            "cycle_id", "start_date", "end_date", "cycle_type",
            "gain_rate_lbs_per_week", "loss_rate_lbs_per_week", "notes",
            "created_at", "updated_at", "source"  # Add any additional columns here
        ]
        df_cycles = pd.DataFrame(diet_cycles, columns=column_names)
        # Rename columns for display purposes
        df_cycles.rename(columns={
            "cycle_id": "Cycle ID",
            "start_date": "Start Date",
            "end_date": "End Date",
            "cycle_type": "Cycle Type",
            "gain_rate_lbs_per_week": "Gain Rate (lbs/week)",
            "loss_rate_lbs_per_week": "Loss Rate (lbs/week)",
            "notes": "Notes",
            "created_at": "Created At",
            "updated_at": "Updated At",
            "source": "Source"  # Rename additional columns as needed
        }, inplace=True)
        st.dataframe(df_cycles)
    else:
        st.info("No diet cycle data found.")

    st.sidebar.header("Manage Diet Cycles")
    with st.sidebar.form("new_diet_cycle_form"):
        st.subheader("Start New Diet Cycle")
        start_date = st.date_input("Start Date", date.today())
        cycle_type = st.selectbox("Cycle Type", ["bulk", "cut"])
        gain_rate = st.number_input("Gain Rate (lbs/week)", value=0.0, step=0.1)
        loss_rate = st.number_input("Loss Rate (lbs/week)", value=0.0, step=0.1)
        notes = st.text_input("Notes (optional)")
        submitted_start = st.form_submit_button("Start Cycle")
        if submitted_start:
            result = insert_diet_cycle(db, start_date, cycle_type, notes=notes)
            st.success(result)
            st.experimental_rerun()

    with st.sidebar.form("end_current_cycle_form"):
        st.subheader("End Current Diet Cycle")
        current_cycle = get_current_diet_cycle(db)
        if current_cycle:
            cycle_id = current_cycle.cycle_id
            end_date = st.date_input("End Date", date.today())
            submitted_end = st.form_submit_button(f"End Cycle {cycle_id}")
            if submitted_end:
                result = end_diet_cycle(db, cycle_id, end_date)
                st.success(result)
                st.experimental_rerun()
        else:
            st.info("No current diet cycle recorded.")

db.close()