# Hevy Metal Project Plan

## Updated 5/17/25

## Overview
The Hevy Metal project is a comprehensive health and fitness tracking system that integrates workout data, nutrition, sleep, and health markers into a unified database. The project includes data ingestion, storage, querying, and visualization through a dashboard.

## Milestones
1. **Database Schema Design and Implementation**
   - Define tables for workouts, exercises, sets, sleep data, nutrition data, health markers, and diet cycles.
   - Implement relationships between tables using SQLAlchemy.
   - **Status**: Schema has been implemented in `schema.py` and includes all required tables and relationships.

2. **Data Ingestion**
   - Develop utilities to import historical health data from JSON files.
   - Implement functions to process and store metrics, sleep data, nutrition data, and health markers.
   - **Status**: Historical data import utilities for the Hevy API, health JSON, and diet cycles/weeks CSVs are mostly functional but may require minor tweaks as issues arise.

3. **Query Development**
   - Create SQLAlchemy queries for retrieving data from the database.
   - Implement filtering and aggregation for workouts, nutrition, sleep, and health markers.
   - **Status**: Baseline functionality queries are implemented, but additional queries will be needed to provide deeper data insights.

4. **Dashboard Development**
   - Build a Streamlit-based dashboard for visualizing data.
   - Include pages for workouts, nutrition, sleep, health markers, and diet cycles.
   - **Status**: Baseline functionality is available for testing but will need updates as new queries are created.

5. **Testing and Debugging**
   - Test database schema and queries for accuracy and performance.
   - Debug data ingestion and dashboard functionality.
   - **Status**: Working towards an MVP with basic testing. A more robust test suite will be created later.

6. **Documentation**
   - Document the database schema, utility functions, and dashboard usage.
   - Provide a user guide for importing data and navigating the dashboard.
   - **Status**: Git commits and issue tracking are helping document the process. More thorough documentation will be created after the MVP is ready.

## Project Steps

### Step 1: Database Schema Design
- Define tables in `src/database/schema.py`:
  - `common_data`: Stores shared metadata like date and source.
  - `workouts`, `exercises`, `workout_exercises`, `sets`: Track workout details.
  - `sleep_data`, `nutrition_data`, `health_markers`: Store health-related metrics.
  - `diet_cycles`, `diet_weeks`: Manage diet plans and weekly targets.
- Use SQLAlchemy to create and manage the schema.
- **Status**: Completed.

### Step 2: Data Ingestion Utilities
- Implement functions in `src/utils/historical_health.py` and `src/utils/historical_hevy.py`:
  - `import_historical_data`: Load and process JSON health data.
  - `store_workouts_in_sqlite`: Store Hevy API workout data in the database.
  - `pull_sleep_from_json`, `pull_nutrition_from_json`, `pull_markers_from_json`: Process specific data types.
- Implement CSV import utilities for diet cycles and diet weeks.
- Ensure data integrity and handle errors during ingestion.
- **Status**: Mostly functional, with minor tweaks expected.

### Step 3: Query Development
- Develop queries in `src/database/queries`:
  - `hevy_sql_queries.py`: Queries for workouts and exercises.
  - `nutrition_queries.py`: Queries for nutrition data.
  - `sleep_queries.py`: Queries for sleep data.
  - `diet_cycles_queries.py`: Queries for diet cycles and weeks.
- Implement filtering by date and aggregation for metrics.
- **Status**: Baseline queries are implemented, but additional queries will be added for deeper insights.

### Step 4: Dashboard Development
- Build a Streamlit dashboard in `src/dashboard/hevy_dashboard.py`:
  - Create pages for workouts, nutrition, sleep, health markers, and diet cycles.
  - Use queries to fetch data and display it in tables and charts.
  - Add forms for user input, such as starting a new diet cycle or adding a diet week.
- **Status**: Baseline functionality is available for testing but will evolve as new queries are added.

### Step 5: Testing and Debugging
- Test database schema by inserting and querying sample data.
- Validate data ingestion functions with various JSON files.
- Debug dashboard interactions and ensure accurate visualizations.
- **Status**: Focused on MVP testing. A more robust test suite will be developed later.

### Step 6: Documentation
- Create a user guide for:
  - Setting up the database and importing data.
  - Using the dashboard to view and analyze health metrics.
- Document the codebase for developers.
- **Status**: Git commits and issue tracking are documenting the process. Comprehensive documentation will follow the MVP.

## Deliverables
1. Fully functional database schema.
2. Utilities for importing and processing health data.
3. SQLAlchemy queries for retrieving and aggregating data.
4. Streamlit dashboard for data visualization and user interaction.
5. Comprehensive documentation and user guide.

### Summary of Changes to Reimplement

#### 1. Schema Adjustments
- **workout_exercises Table**:
  - Ensure the table includes the following columns:
    - `workout_exercise_id` (Primary Key, Integer, Auto-increment)
    - `hevy_workout_id` (Foreign Key referencing `workouts.hevy_workout_id`)
    - `exercise_id` (Foreign Key referencing `exercises.exercise_id`)
    - `exercise_index` (Integer, Nullable)
    - `exercise_notes` (String, Nullable)
    - `superset_id` (Integer, Nullable)

- **sets Table**:
  - Ensure the table uses `workout_exercise_id` (Foreign Key referencing `workout_exercises.workout_exercise_id`) instead of `workout_id`.

#### 2. Data Insertion Logic
- **`store_workouts_in_sqlite` Function**:
  - Insert data into the `workouts`, `pumps`, `fatigue`, `exercises`, `workout_exercises`, and `sets` tables.
  - Use `hevy_workout_id` as the primary identifier for workouts.
  - Ensure `workout_exercise_id` is retrieved from the `workout_exercises` table before inserting data into the `sets` table.
  - Parse workout descriptions to extract `pumps`, `fatigue`, `notes`, and `listened_to` using the `parse_workout_description` function.

#### 3. Parsing Enhancements
- **`parse_workout_description` Function**:
  - Extract `pumps` and `fatigue` ratings from structured text in workout descriptions.
  - Normalize ratings using a predefined scale (e.g., `Poor` = 1, `Fair` = 2, etc.).
  - Handle unstructured notes and audio data (e.g., `What I Listened To`).

#### 4. API Integration
- **`fetch_exercise_details` Function**:
  - Cache exercise details to minimize redundant API calls.
  - Extract and store primary/secondary muscles, equipment, custom flags, and exercise types.

#### 5. Performance Improvements
- Use `time.perf_counter()` for accurate timing in `store_workouts_in_sqlite`.
- Deduplicate workouts in `fetch_all_hevy_workouts` by using a dictionary keyed by `workout_id`.

#### 6. Error Handling and Logging
- Add error handling for database insertions (e.g., `sqlite3.IntegrityError`).
- Log successful insertions and errors for debugging purposes.

#### 7. General Methodology
- Ensure all foreign key relationships are respected (e.g., `hevy_workout_id`, `workout_exercise_id`).
- Use `get_or_create_common_data_id` to manage `common_data` entries.
- Validate and format timestamps (e.g., `start_time`, `created_at`) before database insertion.

#### 8. Testing and Validation
- Verify that all tables (`workouts`, `pumps`, `fatigue`, `exercises`, `workout_exercises`, `sets`) are populated correctly.
- Test with a variety of workout data to ensure parsing and insertion logic handles edge cases.

### Instructions for Reimplementation
1. Revert to the previous commit to restore the original `store_workouts_in_sqlite` function and related logic.
2. Apply the schema adjustments listed above.
3. Update the `store_workouts_in_sqlite` function to include the enhanced data insertion logic.
4. Test the changes thoroughly to ensure all tables are populated as expected.
5. Log any errors or issues encountered during testing for further debugging.
