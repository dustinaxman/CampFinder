import json
from camp_finder.filter.campground_selector import CampgroundData
from datetime import datetime


def custom_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # Convert datetime to ISO 8601 string format
    # Add other custom serialization cases if needed
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


# Define the path to your campground data file (replace with the actual file path)
jsonl_file = "/Users/deaxman/Downloads/recgov_all_converted_100824.jsonl"

# Instantiate the CampgroundData class
campground_data = CampgroundData(jsonl_file)

# Define the filter and sort parameters for your search
filter_sort_dict = {
    "availability": {
        "start_window_date": "2024-11-07", 
        "end_window_date": "2024-11-11", 
        "num_nights": 2, 
        "days_of_the_week": [4, 5]
    },
    "filters": {
        "AND": [
            {"rating.average_rating": {"gt": 3.5}},
            {"rating.number_of_ratings": {"gt": 200}},
            {"location": {"within_radius": {"center": [37.759244, -122.451855], "radius": 170}}}
        ]
    },
    "sort": {
        "key": "rating.average_rating",
        "reverse": True
    }
}

# Call the filter_and_sort_campgrounds method
results = campground_data.filter_and_sort_campgrounds(filter_sort_dict)

# Output the filtered and sorted campgrounds
json_string = json.dumps(results, indent=2, default=custom_serializer)
print(json_string)