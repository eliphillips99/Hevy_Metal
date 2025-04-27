import json
from collections import defaultdict

HEALTH_JSON_FILE = "c:/Users/eligp/OneDrive/Documents/Coding Projects/Hevy_Metal/data/HealthAutoExport-2023-06-17-2025-04-26.json"

def check_for_duplicates(json_file_path):
    with open(json_file_path, "r") as file:
        data = json.load(file)

    duplicates = defaultdict(list)

    # Iterate through metrics
    for metric in data.get("metrics", []):
        metric_name = metric.get("name")
        metric_data = metric.get("data", [])

        # Use a set to track unique entries
        seen_entries = set()

        for entry in metric_data:
            date = entry.get("date")
            qty = entry.get("qty")
            source = entry.get("source", "Unknown")

            # Create a unique key for each entry
            key = (date, source, qty)

            if key in seen_entries:
                duplicates[metric_name].append(entry)
            else:
                seen_entries.add(key)

    # Print duplicates
    if duplicates:
        print("Duplicates found in the JSON file:")
        for metric_name, entries in duplicates.items():
            print(f"Metric: {metric_name}")
            for entry in entries:
                print(f"  Duplicate Entry: {entry}")
    else:
        print("No duplicates found in the JSON file.")

if __name__ == "__main__":
    check_for_duplicates(HEALTH_JSON_FILE)