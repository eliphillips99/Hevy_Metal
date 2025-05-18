import streamlit as st
import pandas as pd
from datetime import date, timedelta
import sys
import os
import altair as alt
import datetime  # Add this import for handling datetime objects

# Dynamically add the project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

DIET_CYCLES_CSV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/diet_cycles.csv"))
DIET_WEEKS_CSV_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data/diet_weeks.csv"))


from src.database.queries.hevy_sql_queries import *
from src.database.queries.sleep_queries import *
from src.database.queries.nutrition_queries import query_get_nutrition_data
from src.database.queries.health_markers_queries import *
from src.database.queries.diet_cycles_queries import (
    query_get_current_diet_cycle,
    query_get_all_diet_cycles,
    query_insert_diet_cycle,
    query_insert_diet_week
)
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.database.connection import engine

from src.database.queries.hevy_sql_queries import (
    query_get_all_workouts,
    query_get_primary_muscle_volume,
    query_get_secondary_muscle_volume,
    query_get_all_unique_muscle_groups,  # New query to fetch all unique muscle groups
    query_debug_sets_data,  # Ensure this is included
    query_debug_exercises_data,
    query_debug_workout_exercises_data,
    query_debug_workouts_data,
    query_debug_unique_muscle_groups,  # Ensure this is included
    query_debug_raw_sets_data,  # Ensure this is included
    query_debug_primary_muscle_matching,  # Ensure this is included
    query_debug_secondary_muscle_matching,  # Ensure this is included
    query_debug_joined_sets_exercises_workouts,  # Ensure this is included
    query_debug_no_date_filter,  # Ensure this is included
    query_debug_all_sets,  # Ensure this is included
    query_debug_all_exercises,  # Ensure this is included
    query_debug_all_workout_exercises,  # Ensure this is included
    query_debug_all_workouts,  # Ensure this is included
    query_debug_broken_relationships,  # Ensure this is included
    query_debug_broken_workout_relationships,  # Ensure this is included
    query_debug_broken_set_relationships  # Ensure this is included
)

# Create a database session
db = Session(bind=engine)

def set_query_params(**params):
    """Helper function to set query parameters."""
    st.experimental_set_query_params(**params)  # Use the correct Streamlit function

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

# Add quick access buttons for date ranges
st.sidebar.title("Quick Date Range")
today = date.today()
quick_ranges = {
    "Current Day": (today, today),
    "Last Week": (today - timedelta(days=7), today),
    "Last Month": (today - timedelta(days=30), today),
    "Last 3 Months": (today - timedelta(days=90), today),
    "Last 6 Months": (today - timedelta(days=180), today),
    "Last Year": (today - timedelta(days=365), today),
    "All Time": (date(2023, 6, 1), today)  # Data starts from June 2023
}

selected_range = st.sidebar.radio("Select Date Range", list(quick_ranges.keys()))
start_date, end_date = quick_ranges[selected_range]

# Allow manual override of the date range
st.sidebar.title("Custom Date Range")
start_date = st.sidebar.date_input("Start Date", value=start_date)
end_date = st.sidebar.date_input("End Date", value=end_date)

import json  # Import JSON module for formatting debug outputs

if page == "Workouts":
    st.title("Workout Counts")
    workouts = query_get_all_workouts(start_date=start_date, end_date=end_date)
    if workouts:
        df_workouts = pd.DataFrame(workouts, columns=["Workout ID", "Title", "Start Time", "End Time"])
        st.dataframe(df_workouts)
    else:
        st.info("No workouts found for the selected date range.")

    st.title("Muscle Group Volume")

    # Fetch all unique muscle groups from the database
    all_muscle_groups_query = query_get_all_unique_muscle_groups()
    all_muscle_groups = [row[0] for row in db.execute(all_muscle_groups_query).fetchall() if row[0]]

    # Set default muscle groups
    default_muscle_groups = ["chest", "back", "quads", "biceps"]

    # Multi-select widget for muscle groups
    selected_muscle_groups = st.multiselect(
        "Select Muscle Groups",
        options=all_muscle_groups,
        default=[muscle for muscle in default_muscle_groups if muscle in all_muscle_groups]
    )

    if selected_muscle_groups:
        # Initialize data for the bar chart
        volume_data = []

        for muscle_name in selected_muscle_groups:
            # Fetch primary and secondary muscle volumes
            primary_volume_query = query_get_primary_muscle_volume(muscle_name, start_date, end_date)
            secondary_volume_query = query_get_secondary_muscle_volume(muscle_name, start_date, end_date)

            primary_volume = db.execute(primary_volume_query).scalar() or 0
            secondary_volume = db.execute(secondary_volume_query).scalar() or 0

            # Append data for the chart
            volume_data.append({"Muscle Group": muscle_name, "Muscle Role": "Primary Muscle", "Volume": primary_volume})
            volume_data.append({"Muscle Group": muscle_name, "Muscle Role": "Secondary Muscle", "Volume": secondary_volume})

        # Check if there is any data to display
        if volume_data:
            # Create a DataFrame for the chart
            volume_df = pd.DataFrame(volume_data)

            # Create bar chart
            volume_chart = alt.Chart(volume_df).mark_bar().encode(
                x=alt.X("Muscle Group:N", title="Muscle Group"),
                y=alt.Y("Volume:Q", title="Volume (Weight x Reps)"),
                color=alt.Color("Muscle Role:N", title="Muscle Role"),
                tooltip=["Muscle Group", "Muscle Role", "Volume"]
            ).properties(
                title=f"Volume for Selected Muscle Groups ({start_date} to {end_date})"
            )

            st.altair_chart(volume_chart, use_container_width=True)
        else:
            st.info("No volume data available for the selected muscle groups and date range.")
    else:
        st.info("Select at least one muscle group to view its volume.")

elif page == "Nutrition":
    st.title("Protein Per Day")
    nutrition_data = query_get_nutrition_data(start_date=start_date, end_date=end_date)

    # Hardcoded protein target values
    protein_target_min = 145  # Minimum protein target
    protein_target_max = 180  # Maximum protein target

    # Create a DataFrame for the target lines
    target_lines_df = pd.DataFrame({
        'Protein Target': [protein_target_min, protein_target_max],
        'Target Type': ['Min', 'Max']
    })

    # Add horizontal dotted lines for the protein targets
    target_lines = alt.Chart(target_lines_df).mark_rule(
        strokeDash=[5, 5],  # Dotted line
        color='green',
        size=2  # Thicker line
    ).encode(
        y=alt.Y('Protein Target:Q', title='Protein Target'),
        tooltip=['Target Type:N', 'Protein Target:Q']  # Add tooltips for the target lines
    )

    # Ensure the start_date and end_date are datetime objects
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    # Filter data based on the selected date range
    if nutrition_data:
        column_names = ["Date", "Protein (g)", "Calories", "Carbohydrates (g)", "Fat (g)"]
        df_nutrition = pd.DataFrame(nutrition_data, columns=column_names)

        # Convert the Date column to datetime format
        df_nutrition['Date'] = pd.to_datetime(df_nutrition['Date'])

        filtered_data = df_nutrition[(df_nutrition['Date'] >= start_date) & 
                                     (df_nutrition['Date'] <= end_date)]

        # this line is necessary to keep filtering operational for the chart, will need fixed later
        st.sidebar.write('Filtered Data:', filtered_data)

        # Ensure the filtered data is not empty
        if not filtered_data.empty:
            # Create the base protein chart
            protein_chart = alt.Chart(filtered_data).mark_bar().encode(
                x=alt.X('Date:T', title='Date', type='temporal'),  # Explicitly set type to temporal
                y=alt.Y(
                    'Protein (g):Q',
                    title='Protein (g)',
                    scale=alt.Scale(domain=[0, max(filtered_data['Protein (g)'].max(), protein_target_max) + 20])  # Add padding to the max value
                ),
            ).properties(
                title='Protein Intake Over Time'
            )

            # Combine the charts
            combined_chart = protein_chart + target_lines
            st.altair_chart(combined_chart, use_container_width=True)
        else:
            # Show only the target lines if no data is available
            st.info("No nutrition data found for the selected date range.")
            st.altair_chart(target_lines.properties(title="Protein Intake Over Time"), use_container_width=True)
    else:
        st.info("No nutrition data found for the selected date range.")
        # Always show the target lines even if no data is available
        st.altair_chart(target_lines.properties(title="Protein Intake Over Time"), use_container_width=True)

elif page == "Sleep":
    st.title("Sleep Analysis")
    sleep_data = query_get_sleep_data(start_date=start_date, end_date=end_date)

    if sleep_data:
        column_names = [
            "Date", "Source", "Start Time", "End Time", "In Bed Duration (hrs)", "Sleep Duration (hrs)",
            "Awake Duration (hrs)", "REM Sleep (hrs)", "Deep Sleep (hrs)", "Core Sleep (hrs)",
            "In Bed Start", "In Bed End"
        ]
        df_sleep = pd.DataFrame(sleep_data, columns=column_names)
        st.dataframe(df_sleep)

        # Query sleep stats
        sleep_stats = query_get_sleep_stats(start_date=start_date, end_date=end_date)
        if sleep_stats:
            avg_rem, avg_deep, avg_core, avg_awake, avg_total_sleep = sleep_stats

            # Prepare data for the chart
            sleep_stats_df = pd.DataFrame({
                "Sleep Cycle": ["REM Sleep", "Deep Sleep", "Core Sleep", "Awake Time", "Total Sleep"],
                "Duration (hrs)": [avg_rem, avg_deep, avg_core, avg_awake, avg_total_sleep]
            })

            # Create a bar chart for sleep stats
            sleep_stats_chart = alt.Chart(sleep_stats_df).mark_bar().encode(
                x=alt.X("Sleep Cycle:N", title="Sleep Cycle"),
                y=alt.Y("Duration (hrs):Q", title="Duration (hrs)"),
                color=alt.Color("Sleep Cycle:N", title="Sleep Cycle")
            ).properties(
                title="Sleep Stats (Filtered Date Range)"
            )

            st.altair_chart(sleep_stats_chart, use_container_width=True)
        else:
            st.info("No sleep stats available for the selected date range.")
    else:
        st.info("No sleep data found for the selected date range.")

    sleep_percentages = query_get_sleep_cycle_percentages(start_date=start_date, end_date=end_date)
    if sleep_percentages:
        # Extract percentages from the query result
        avg_rem, avg_deep, avg_core, avg_awake = sleep_percentages

        # Prepare data for the pie chart
        pie_chart_data = pd.DataFrame({
            "Sleep Stage": ["REM Sleep", "Deep Sleep", "Core Sleep", "Awake Time"],
            "Average Percentage (%)": [avg_rem, avg_deep, avg_core, avg_awake]
        })

        # Create a pie chart
        pie_chart = alt.Chart(pie_chart_data).mark_arc().encode(
            theta=alt.Theta(field="Average Percentage (%)", type="quantitative"),
            color=alt.Color(field="Sleep Stage", type="nominal"),
            tooltip=["Sleep Stage", "Average Percentage (%)"]
        ).properties(
            title="Average Sleep Stage Distribution (%)"
        )

        st.altair_chart(pie_chart, use_container_width=True)
    else:
        st.info("No sleep percentage data available for the selected date range.")

elif page == "Health Markers":
    
    st.title("Daily Health Markers")
    # Use the new aggregated query
    health_markers = query_get_aggregated_health_markers(start_date=start_date, end_date=end_date)

    if health_markers:
        column_names = [
            "Date", "Heart Rate Avg", "Heart Rate Min", "Heart Rate Max", "VO2 Max", "Body Weight (lbs)", "BMI",
            "Respiratory Rate", "Blood Oxygen Saturation", "Time in Daylight (min)"
        ]
        df_health = pd.DataFrame(health_markers, columns=column_names)
        st.dataframe(df_health)
    else:
        st.info("No health marker data found for the selected date range.")

    st.title("Body Weight Over Time")

    body_weight = query_get_body_weight_over_time(start_date=start_date, end_date=end_date)
    cycle_start_dates = query_get_all_diet_cycles(start_date=start_date, end_date=end_date)

    if cycle_start_dates:
        df_diet_cycles = pd.DataFrame(cycle_start_dates, columns=[
            "Cycle ID", "Common Data ID", "Start Date", "End Date", "Cycle Type", 
            "Gain Rate", "Loss Rate", "Source", "Notes", "Created At", "Updated At"
        ])
        start_dates = df_diet_cycles["Start Date"]
        cycle_types = df_diet_cycles["Cycle Type"]
    else:
        df_diet_cycles = None  # Ensure df_diet_cycles is defined

    if body_weight:
        column_names = ["Date", "Body Weight (lbs)"]
        df_body_weight = pd.DataFrame(body_weight, columns=column_names)

        body_weight_chart = alt.Chart(df_body_weight).mark_line().encode(
            x=alt.X('Date:T', title='Date'),
            y=alt.Y('Body Weight (lbs):Q', title='Body Weight (lbs)', scale=alt.Scale(domain=[df_body_weight['Body Weight (lbs)'].min()-5, df_body_weight['Body Weight (lbs)'].max()+10])),
        ).properties(
            title='Body Weight Over Time'
        )

        if df_diet_cycles is not None and not df_diet_cycles.empty:
            cycle_chart = alt.Chart(df_diet_cycles).mark_bar(size=5).encode(
                x=alt.X('Start Date:T', title='Diet Cycle Start Date'),
                color=alt.Color('Cycle Type:N', title='Cycle Type', scale=alt.Scale(domain=['bulk', 'cut', 'maintenance'], range=['yellow', 'red', 'orange'])),
                tooltip=['Start Date:T', 'End Date:T', 'Cycle Type:N', 'Gain Rate:Q', 'Loss Rate:Q']
            )
            combined_chart = body_weight_chart + cycle_chart
        else:
            combined_chart = body_weight_chart

        st.altair_chart(combined_chart, use_container_width=True)
    else:
        st.info("No body weight data found for the selected date range.")

        

elif page == "Diet Cycles":
    st.title("Diet Cycles")
    diet_cycles = query_get_all_diet_cycles()
    if diet_cycles:
        column_names = [
            "Cycle ID", "Common Data ID", "Start Date", "End Date", "Cycle Type",
            "Gain Rate (lbs/week)", "Loss Rate (lbs/week)", "Source", "Notes", "Created At", "Updated At"
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
                    text("SELECT common_data_id FROM common_data WHERE date = :date AND source = :source"),
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