import streamlit as st
import pandas as pd
from database_utils import get_db, get_all_workouts, get_exercise_counts
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