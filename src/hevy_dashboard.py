import streamlit as st
import pandas as pd
from database_utils import *
from datetime import date

st.title("Hevy Workout Analytics")
st.subheader("Your Workout History")

# Date Range Filter for Workouts
st.sidebar.header("Filter Workouts")
start_date = st.sidebar.date_input("Start Date", value=date(2025, 1, 1))
end_date = st.sidebar.date_input("End Date", value=date.today())

# Create a database session
db = next(get_db())

# Get workout data based on the filter
workouts = get_all_workouts(db, start_date=start_date, end_date=end_date)

if workouts:
    df_workouts = pd.DataFrame(workouts)
    st.dataframe(df_workouts)
else:
    st.info("No workouts found for the selected date range.")

st.subheader("Most Frequent Exercises")

# Get exercise counts
exercise_counts = get_exercise_counts(db, start_date=start_date, end_date=end_date)

if exercise_counts:
    df_exercise_counts = pd.DataFrame(exercise_counts)
    st.dataframe(df_exercise_counts)
    st.bar_chart(df_exercise_counts.set_index('exercise_name'), height=500)
else:
    st.info("No exercise data found.")

st.title("Hevy Workout Analytics")

# ... (rest of your dashboard code - workout history, exercise frequency, etc.) ...

st.sidebar.header("Diet Cycle Management")

with st.sidebar.form("new_diet_cycle_form"):
    st.subheader("Start New Diet Cycle")
    start_date = st.date_input("Start Date", date.today())
    cycle_type = st.selectbox("Cycle Type", ["bulk", "cut"])
    notes = st.text_input("Notes (optional)")
    submitted_start = st.form_submit_button("Start Cycle")
    if submitted_start:
        db = next(get_db())
        result = insert_diet_cycle(db, start_date, cycle_type, notes=notes)
        st.success(result)
        db.close()
        st.experimental_rerun()  # Refresh the app to show updated data

with st.sidebar.form("end_current_cycle_form"):
    st.subheader("End Current Diet Cycle")
    db = next(get_db())
    current_cycle = get_current_diet_cycle(db)
    db.close()
    if current_cycle:
        cycle_id = current_cycle.cycle_id
        end_date = st.date_input("End Date", date.today())
        # Ensure the submit button is properly placed
        submitted_end = st.form_submit_button(f"End Cycle {cycle_id}")
        if submitted_end:
            db = next(get_db())
            result = end_diet_cycle(db, cycle_id, end_date)
            st.success(result)
            db.close()
            st.experimental_rerun()  # Refresh the app to show updated data
    else:
        st.info("No current diet cycle recorded.")

st.subheader("Current Diet Cycle")
db = next(get_db())
current_cycle_data = get_current_diet_cycle(db)
db.close()
if current_cycle_data:
    st.write(f"**Current Cycle:** {current_cycle_data.cycle_type.upper()}")
    st.write(f"**Start Date:** {current_cycle_data.start_date}")
    if current_cycle_data.end_date:
        st.write(f"**End Date:** {current_cycle_data.end_date}")
    if current_cycle_data.notes:
        st.write(f"**Notes:** {current_cycle_data.notes}")
else:
    st.info("No diet cycle information recorded yet.")

st.subheader("All Diet Cycles")
db = next(get_db())
all_cycles_data = get_all_diet_cycles(db)
db.close()
if all_cycles_data:
    st.dataframe(pd.DataFrame(all_cycles_data))
else:
    st.info("No diet cycle history recorded.")