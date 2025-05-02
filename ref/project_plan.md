# Hevy Metal Project Plan

## Overview
The Hevy Metal project is a comprehensive health and fitness tracking system that integrates workout data, nutrition, sleep, and health markers into a unified database. The project includes data ingestion, storage, querying, and visualization through a dashboard.

## Milestones
1. **Database Schema Design and Implementation**
   - Define tables for workouts, exercises, sets, sleep data, nutrition data, health markers, and diet cycles.
   - Implement relationships between tables using SQLAlchemy.

2. **Data Ingestion**
   - Develop utilities to import historical health data from JSON files.
   - Implement functions to process and store metrics, sleep data, nutrition data, and health markers.

3. **Query Development**
   - Create SQLAlchemy queries for retrieving data from the database.
   - Implement filtering and aggregation for workouts, nutrition, sleep, and health markers.

4. **Dashboard Development**
   - Build a Streamlit-based dashboard for visualizing data.
   - Include pages for workouts, nutrition, sleep, health markers, and diet cycles.

5. **Testing and Debugging**
   - Test database schema and queries for accuracy and performance.
   - Debug data ingestion and dashboard functionality.

6. **Documentation**
   - Document the database schema, utility functions, and dashboard usage.
   - Provide a user guide for importing data and navigating the dashboard.

## Project Steps

### Step 1: Database Schema Design
- Define tables in `src/database/schema.py`:
  - `common_data`: Stores shared metadata like date and source.
  - `workouts`, `exercises`, `workout_exercises`, `sets`: Track workout details.
  - `sleep_data`, `nutrition_data`, `health_markers`: Store health-related metrics.
  - `diet_cycles`, `diet_weeks`: Manage diet plans and weekly targets.
- Use SQLAlchemy to create and manage the schema.

### Step 2: Data Ingestion Utilities
- Implement functions in `src/utils/historical_health.py`:
  - `import_historical_data`: Load and process JSON health data.
  - `insert_raw_data`: Insert raw metric data into the database.
  - `pull_sleep_from_json`, `pull_nutrition_from_json`, `pull_markers_from_json`: Process specific data types.
- Ensure data integrity and handle errors during ingestion.

### Step 3: Query Development
- Develop queries in `src/database/queries`:
  - `hevy_sql_queries.py`: Queries for workouts and exercises.
  - `health_markers_queries.py`: Queries for health markers.
  - `diet_cycles_queries.py`: Queries for diet cycles and weeks.
- Implement filtering by date and aggregation for metrics.

### Step 4: Dashboard Development
- Build a Streamlit dashboard in `src/dashboard/hevy_dashboard.py`:
  - Create pages for workouts, nutrition, sleep, health markers, and diet cycles.
  - Use queries to fetch data and display it in tables and charts.
  - Add forms for user input, such as starting a new diet cycle or adding a diet week.

### Step 5: Testing and Debugging
- Test database schema by inserting and querying sample data.
- Validate data ingestion functions with various JSON files.
- Debug dashboard interactions and ensure accurate visualizations.

### Step 6: Documentation
- Create a user guide for:
  - Setting up the database and importing data.
  - Using the dashboard to view and analyze health metrics.
- Document the codebase for developers.

## Deliverables
1. Fully functional database schema.
2. Utilities for importing and processing health data.
3. SQLAlchemy queries for retrieving and aggregating data.
4. Streamlit dashboard for data visualization and user interaction.
5. Comprehensive documentation and user guide.
