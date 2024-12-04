import operator
import math
import json
import os
from datetime import datetime, timedelta
import logging
from botocore.exceptions import ClientError
from typing import List
from camp_finder.availability.api_requester import get_available_campsites
from camp_finder.utils.weather_utils import get_weather_for_future_date
import boto3

logging.basicConfig(format="%(asctime)s [%(levelname)8s]: %(message)s",
                    level=logging.INFO)


def convert_to_datetime(date_str, default_value):
    if isinstance(date_str, str):
        # Assuming the date string is in the format 'YYYY-MM-DD'
        return datetime.strptime(date_str, '%Y-%m-%d')
    return default_value


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth (specified in decimal degrees)
    using the Haversine formula.
    :param lat1: Latitude of the first point
    :param lon1: Longitude of the first point
    :param lat2: Latitude of the second point
    :param lon2: Longitude of the second point
    :return: Distance between the two points in miles
    """
    # Convert latitude and longitude from degrees to radians
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Radius of the Earth in miles
    radius_of_earth_miles = 3958.8  # Use 6371 for kilometers

    # Calculate the result
    distance = radius_of_earth_miles * c
    return distance



# aws ssm put-parameter \
#     --name "OPENWEATHER_API_KEY" \
#     --value "your-api-key-here" \
#     --type "SecureString" \
#     --region us-east-1

def get_parameter_from_ssm(parameter_name, region="us-east-1"):
    ssm = boto3.client('ssm', region_name=region)
    try:
        response = ssm.get_parameter(Name=parameter_name, WithDecryption=True)
        return response['Parameter']['Value']
    except ClientError as e:
        logging.info(f"Error fetching parameter {parameter_name}: {e}")
        return None

if not os.environ.get("OPENWEATHER_API_KEY"):
    openweather_api_key = get_parameter_from_ssm("OPENWEATHER_API_KEY")
    if openweather_api_key:
        os.environ["OPENWEATHER_API_KEY"] = openweather_api_key

OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")



class CampgroundData:
    def __init__(self, jsonl_file):
        self.campgrounds = []
        with open(jsonl_file, 'r') as file:
            for line in file:
                self.campgrounds.append(json.loads(line))

    def _apply_condition(self, value, condition):
        """Helper function to apply filtering conditions."""
        for op, op_val in condition.items():
            try:
                if op == 'eq' and value != op_val:
                    return False
                if op == 'gt' and value <= op_val:
                    return False
                if op == 'lt' and value >= op_val:
                    return False
                if op == 'ge' and value < op_val:
                    return False
                if op == 'le' and value > op_val:
                    return False
                if op == 'between' and not (op_val[0] <= value <= op_val[1]):
                    return False
            except TypeError:
                return False
        return True

    def _filter_campsites(self, campsite, conditions):
        """Helper function to filter campsites by attributes."""
        value = campsite
        for key_path, cond in conditions:
            for k in key_path.split('.')[1:]:
                value = value[k]

            if isinstance(value, list) and 'contains' in cond:
                # add the "next" thing to check if it contains
                # (if the cond[contains is not a dict, otherwise find the key
                # in that dict and check the value (condition) with the built
                # in checker!
                if isinstance(cond["contains"], dict):
                    #all of these conditions should match
                    match = all(
                        self._apply_condition(
                            next((val for (attr_name, val) in value if attr_name == key), None),
                            condition)
                        for key, condition in cond["contains"].items()
                    )
                elif isinstance(cond["contains"], list):
                    #all of these should be values in the attributes
                    list_of_attr_keys = set([attrb[0] for attrb in value])
                    match = all(item in list_of_attr_keys for item in cond['contains'])
                else:
                    #hopefully a scalar
                    list_of_attr_keys = set([attrb[0] for attrb in value])
                    match = (cond['contains'] in list_of_attr_keys)
                # if not all(item in value for item in cond['contains']):
                #     next((val for (attr_name, val) in campsite['attributes'] if attr_name == key)
                #     match = False
            else:
                # normal value condition check
                match = self._apply_condition(value, cond)
            if not match:
                return False




    def _filter_campgrounds(self, campground, filter_conditions):
        """Helper to filter campgrounds based on conditions."""
        match = True
        for field, condition in filter_conditions.items():
            if '.' in field:
                # Nested field, like rating.average_rating
                keys = field.split('.')
                value = campground
                for key in keys:
                    value = value.get(key)
                    if value is None:
                        match = False
                        break
                if not self._apply_condition(value, condition):
                    match = False
            else:
                # Non-nested field
                value = campground.get(field)
                if isinstance(value, list) and 'contains' in condition:
                    # Handle list checks like activities, amenities
                    if not all(item in value for item in condition['contains']):
                        match = False
                elif isinstance(value, list) and 'contains_any' in condition:
                    if not any(item in value for item in condition['contains_any']):
                        match = False
                elif not self._apply_condition(value, condition):
                    match = False
        return match

    def _get_nested_value(self, obj, key):
        """Helper to get nested values from a dictionary."""
        keys = key.split('.')
        for k in keys:
            obj = obj.get(k)
            if obj is None:
                return None
        return obj




    # # 37.765195,-122.454539 #301 carl
    # origin_lat = 37.765195
    # origin_lng = -122.454539
    # date = datetime(2024, 9, 22)

    def passes_weather_filter(self, weather, conds):
        return all([self._apply_condition(weather[k], condition) for k, condition in conds.items()])

    def filter_campsite_available_dates_by_weather(self, campsites, conds):
        for date_group, weather in zip(campsites["available"], campsites["weathers"]):
            print(conds, weather, self.passes_weather_filter(weather, conds))
        [date_group for date_group, weather in zip(campsites["available"], campsites["weathers"]) if self.passes_weather_filter(weather, conds)]
        campsites["available"] = [date_group for date_group, weather in zip(campsites["available"], campsites["weathers"]) if self.passes_weather_filter(weather, conds)]
        # {
    #                     "min_temp": day['temp']['min'],
    #                     "max_temp": day['temp']['max'],
    #                     "cloud_cover": day['clouds'],
    #                     "rain_amount_mm": day.get('rain', 0),
    #                     "humidity": day["humidity"]
    #                 }

    def filter_and_sort_campgrounds(self, filter_sort_dict):
        filters = filter_sort_dict.get("filters", {})
        sort = filter_sort_dict.get("sort", {})
        availability = filter_sort_dict.get("availability", {})
        location_filter = filter_sort_dict.get("location", None)
        today = datetime.today()
        two_weeks_from_today = today + timedelta(weeks=2)
        start_window_datetime = convert_to_datetime(availability.get("start_window_date"), today)
        end_window_datetime = convert_to_datetime(availability.get("end_window_date"), two_weeks_from_today)
        num_nights = int(availability.get("num_nights", 1))
        days_of_the_week = availability.get("days_of_the_week", None) #or [0,1,2,3,4,5,6] Monday is 0 and Sunday is 6

        and_conditions = filters.get('AND', [])
        or_conditions = filters.get('OR', [])
        weather_conditions = filters.get('weather', {})

        results = []
        for campground in self.campgrounds:

            # AND conditions
            if and_conditions:
                match = all(self._filter_campgrounds(campground, cond) for cond in and_conditions if not any("campsites" in cond_path for cond_path in cond))
                if not match:
                    continue

            # OR conditions
            if or_conditions:
                match = any(self._filter_campgrounds(campground, cond) for cond in or_conditions if not any("campsites" in cond_path for cond_path in cond))
                if not match:
                    continue

            # Location filtering (within radius)
            if location_filter:
                center_lat, center_lon = location_filter["center"]
                radius = location_filter["radius"]
                if not self.is_within_radius(campground, center_lat, center_lon, radius):
                    continue  # Skip campgrounds outside the radius

            # Campsite filtering
            campsite_filters = [cond for cond in and_conditions if 'campsites' in cond] + [cond for cond in or_conditions if all("campsites" in cond_path for cond_path in cond)]
            if campsite_filters:
                temp_campsites = []
                for campsite in campground['campsites']:
                    match = all(self._filter_campsites(campsite, cond) for cond in and_conditions if all("campsites" in cond_path for cond_path in cond))
                    if not match:
                        continue
                    match = any(
                        self._filter_campsites(campsite, cond) for cond in or_conditions if "campsites" in cond)
                    if not match:
                        continue
                    temp_campsites.append(campsite)
                campground['campsites'] = temp_campsites
                if not campground['campsites']:
                    continue  # Skip campgrounds with no matching campsites

            results.append(campground)


        campground_list = [campground["id"] for campground in results]

        print("Checking availability of following campgrounds: " + "\n".join(campground_list))
        print(len(campground_list))
        available_campsites = get_available_campsites(campground_list, start_window_datetime, end_window_datetime, num_nights=num_nights, days_of_the_week=days_of_the_week)
        cached_weather = {}
        available_filtered_campgrounds = []
        weather_filter = next((cond.get("weather") for cond in and_conditions if "weather" in cond), None)
        for campground in results:
            available_campsites_list = []
            for campsite in campground['campsites']:
                if (campground["id"], campsite["campsite_id"]) in available_campsites:
                    campsite["available"] = available_campsites[(campground["id"], campsite["campsite_id"])]
                    weathers = []
                    for date_group in campsite["available"]:
                        if (date_group[0], campground["latitude"], campground["longitude"]) not in cached_weather:
                            weather_dict = get_weather_for_future_date(date_group[0], campground["latitude"], campground["longitude"],
                                                        OPENWEATHER_API_KEY)
                            weathers.append(weather_dict)
                            #TODO: make this run on all days in group and filter all!
                            #TODO: cache this to ddb instead
                            cached_weather[(date_group[0], campground["latitude"], campground["longitude"])] = weather_dict
                        else:
                            weathers.append(cached_weather[(date_group[0], campground["latitude"], campground["longitude"])])
                    campsite["weathers"] = weathers
                    self.filter_campsite_available_dates_by_weather(campsite, weather_conditions)
                    if not campsite["available"]:
                        campsite.pop('available', None)
                        continue
                    available_campsites_list.append(campsite)
            campground['campsites'] = available_campsites_list
            if campground['campsites']:
                available_filtered_campgrounds.append(campground)


        # Sorting
        if sort:
            sort_key = sort.get("key")
            reverse = sort.get("reverse", False)
            available_filtered_campgrounds_sorted = sorted(available_filtered_campgrounds, key=lambda x: self._get_nested_value(x, sort_key), reverse=reverse)

        return available_filtered_campgrounds_sorted

    def is_within_radius(self, campground, center_latitude, center_longitude, radius_miles):
        """Helper function to check if the campground is within the given radius."""
        campground_lat = campground['latitude']
        campground_lon = campground['longitude']
        distance = haversine_distance(center_latitude, center_longitude, campground_lat, campground_lon)
        return distance <= radius_miles





# datetime(year=2024, month=11, day=1)
# datetime(year=2024, month=11, day=30)
# start_window_datetime
# end_window_datetime
# num_nights
# days_of_the_week = None, #or [0,1,2,3,4,5,6] Monday is 0 and Sunday is 6



# for match in matches:
# campsite_id
# booking_nights
# booking_date
# booking_end_date



# AvailableCampsite(campsite_id=42013, booking_date=datetime.datetime(2024, 11, 1, 0, 0), booking_end_date=datetime.datetime(2024, 11, 2, 0, 0), booking_nights=1, campsite_site_name='037', campsite_loop_name='A-WESA', campsite_type='STANDARD NONELECTRIC', campsite_occupancy=(1, 8), campsite_use_type='Overnight', availability_status='Available', recreation_area='New Hogan Lake, CA', recreation_area_id=476, facility_name='Acorn Campground', facility_id=233683, booking_url='https://www.recreation.gov/camping/campsites/42013', location=CampsiteLocation(latitude=np.float64(38.177261), longitude=np.float64(-120.799889)), permitted_equipment=[RecDotGovEquipment(equipment_name='Tent', max_length=4.0), RecDotGovEquipment(equipment_name='RV', max_length=40.0), RecDotGovEquipment(equipment_name='Trailer', max_length=36.0), RecDotGovEquipment(equipment_name='Large Tent Over 9X12`', max_length=0.0)], campsite_attributes=[RecDotGovAttribute(attribute_category='site_details', attribute_id=52, attribute_name='Max Num of People', attribute_value='8'), RecDotGovAttribute(attribute_category='site_details', attribute_id=10, attribute_name='Capacity/Size Rating', attribute_value='Single'), RecDotGovAttribute(attribute_category='site_details', attribute_id=11, attribute_name='Checkin Time', attribute_value='3:00 PM'), RecDotGovAttribute(attribute_category='site_details', attribute_id=56, attribute_name='Min Num of People', attribute_value='1'), RecDotGovAttribute(attribute_category='site_details', attribute_id=9, attribute_name='Campfire Allowed', attribute_value='Yes'), RecDotGovAttribute(attribute_category='site_details', attribute_id=12, attribute_name='Checkout Time', attribute_value='2:00 PM'), RecDotGovAttribute(attribute_category='site_details', attribute_id=65, attribute_name='Pets Allowed', attribute_value='Yes'), RecDotGovAttribute(attribute_category='site_details', attribute_id=77, attribute_name='Shade', attribute_value='Yes'), RecDotGovAttribute(attribute_category='equipment_details', attribute_id=23, attribute_name='Driveway Entry', attribute_value='Back-in'), RecDotGovAttribute(attribute_category='equipment_details', attribute_id=0, attribute_name='Driveway Length', attribute_value='43'), RecDotGovAttribute(attribute_category='equipment_details', attribute_id=0, attribute_name='Is Equipment Mandatory', attribute_value='true'), RecDotGovAttribute(attribute_category='equipment_details', attribute_id=54, attribute_name='Max Vehicle Length', attribute_value='20'), RecDotGovAttribute(attribute_category='equipment_details', attribute_id=53, attribute_name='Max Num of Vehicles', attribute_value='2'), RecDotGovAttribute(attribute_category='equipment_details', attribute_id=26, attribute_name='Driveway Surface', attribute_value='Paved'), RecDotGovAttribute(attribute_category='amenities', attribute_id=31, attribute_name='Fire Pit', attribute_value='Y'), RecDotGovAttribute(attribute_category='amenities', attribute_id=67, attribute_name='Picnic Table', attribute_value='Y'), RecDotGovAttribute(attribute_category='amenities', attribute_id=301, attribute_name='Map Y Coordinate', attribute_value='397.711853027344'), RecDotGovAttribute(attribute_category='amenities', attribute_id=314, attribute_name='Placed on Map', attribute_value='1'), RecDotGovAttribute(attribute_category='amenities', attribute_id=4, attribute_name='BBQ', attribute_value='Y'), RecDotGovAttribute(attribute_category='amenities', attribute_id=300, attribute_name='Map X Coordinate', attribute_value='189.919509887695')])

# matches[0].campsite_id
