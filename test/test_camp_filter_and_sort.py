import pytest
from datetime import datetime
from campground_selector import CampgroundData


@pytest.fixture(scope="module")
def campground_data():
    # Setup fixture for CampgroundData instance from a sample JSONL file
    jsonl_file = '/path/to/your/test_json_file.jsonl'  # Replace with your path
    return CampgroundData(jsonl_file)


def test_convert_to_datetime(campground_data):
    # Test datetime conversion
    date_str = "2024-11-07"
    result = campground_data.convert_to_datetime(date_str, None)
    expected = datetime(2024, 11, 7)
    assert result == expected


def test_apply_condition(campground_data):
    # Test _apply_condition with various conditions
    condition = {"gt": 4.0}
    value = 4.5
    assert campground_data._apply_condition(value, condition)

    condition = {"lt": 3.0}
    value = 4.5
    assert not campground_data._apply_condition(value, condition)


def test_filter_campgrounds(campground_data):
    # Test filtering of campgrounds using sample data
    filter_conditions = {
        "rating.average_rating": {"gt": 4.0},
        "rating.number_of_ratings": {"gt": 100}
    }
    matching_campgrounds = [
        campground for campground in campground_data.campgrounds
        if campground_data._filter_campgrounds(campground, filter_conditions)
    ]
    assert len(matching_campgrounds) > 0


def test_is_within_radius(campground_data):
    # Test that the campgrounds are correctly filtered by distance
    center_latitude = 37.759244
    center_longitude = -122.451855
    radius_miles = 200
    campground = {
        "latitude": 37.7,
        "longitude": -122.4
    }
    assert campground_data.is_within_radius(campground, center_latitude, center_longitude, radius_miles)


def test_filter_and_sort_campgrounds(campground_data):
    # Test the main filtering and sorting functionality
    filter_sort_dict = {
        "availability": {
            "start_window_date": "2024-11-07", 
            "end_window_date": "2024-11-11", 
            "num_nights": 2, 
            "days_of_the_week": [4, 5]
        },
        "filters": {
            "AND": [
                {"rating.average_rating": {"gt": 4.0}},
                {"rating.number_of_ratings": {"gt": 100}},
                {"location": {"within_radius": {"center": [37.759244, -122.451855], "radius": 200}}}
            ]
        },
        "sort": {
            "key": "rating.average_rating",
            "reverse": True
        }
    }
    results = campground_data.filter_and_sort_campgrounds(filter_sort_dict)
    assert len(results) > 0
    assert results[0]['rating']['average_rating'] > 4.0
