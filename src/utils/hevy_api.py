# scripts/hevy_api.py
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

HEVY_API_KEY = os.getenv("HEVY_API_KEY")
BASE_URL = os.getenv("HEVY_BASE_URL") # Replace with the actual base URL

# Validate environment variables
if not HEVY_API_KEY:
    raise ValueError("Error: HEVY_API_KEY is not set in the environment variables.")
if not BASE_URL:
    raise ValueError("Error: HEVY_BASE_URL is not set in the environment variables.")

# Fallback: Allow manual input of API key if not valid
if not HEVY_API_KEY or len(HEVY_API_KEY) < 20:  # Assuming a valid key is at least 20 characters
    print("The API key seems invalid or missing. Please input your API key manually:")
    HEVY_API_KEY = input("Enter your HEVY_API_KEY: ").strip()
    if not HEVY_API_KEY:
        raise ValueError("No API key provided. Exiting.")

# Ensure BASE_URL ends with the correct path
if not BASE_URL.endswith("/v1"):
    print("Warning: BASE_URL does not end with '/v1'. Please verify the API base URL.")
    BASE_URL = input("Enter the correct BASE_URL (e.g., https://api.hevyapp.com/v1): ").strip()
    if not BASE_URL:
        raise ValueError("No BASE_URL provided. Exiting.")

def validate_api_key():
    """Validates the API key by making a test request to the Hevy API."""
    test_endpoint = f"{BASE_URL}/workouts?page=1&pageSize=1"
    headers = {
        "api-key": HEVY_API_KEY
    }
    try:
        response = requests.get(test_endpoint, headers=headers)
        if response.status_code == 401:
            print("Invalid API key: Unauthorized access.")
            print("Please check your API key and update the HEVY_API_KEY environment variable.")
            return False
        response.raise_for_status()
        print("API key validation successful.")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error validating API key: {e}")
        return False

# Validate the API key at startup
if not validate_api_key():
    print("Exiting program due to invalid API key.")
    exit(1)

def get_workouts(page_num=1, page_size=10):
    """Retrieves workout data from the Hevy API, with optional limit and ordering."""
    if not HEVY_API_KEY:
        print("Error: HEVY_API_KEY not found in environment variables.")
        return None

    headers = {
        "api-key": HEVY_API_KEY
    }

    endpoint = f"{BASE_URL}/workouts?page={page_num}&pageSize={page_size}"

    try:
        response = requests.get(endpoint, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        if response.status_code == 401:
            print("Check if the API key is valid and has the required permissions.")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    return None

if __name__ == "__main__":
    recent_workouts = get_workouts(page_num=1, page_size=5)
    if recent_workouts:
        print("Successfully retrieved recent workout data:")
        print(recent_workouts)
    else:
        print("Failed to retrieve recent workout data.")