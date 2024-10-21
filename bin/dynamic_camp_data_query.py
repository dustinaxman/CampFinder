


search camply campground list for stuff on date
quick lookup cached info
query driving time and weather for each result
return results with driving time and weather


import requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time



def get_weather_for_date(lat, lon, date, api_key):
    date_day = date.strftime('%Y-%m-%d')
    weather_url = f"https://api.openweathermap.org/data/3.0/onecall/day_summary?lat={lat}&lon={lon}&units=imperial&date={date_day}&appid={api_key}"
    response = requests.get(weather_url)
    return response.json()



def get_rain_likelihood(precipitation_mm):
    # Define cutoff points for the precipitation to probability mapping
    if precipitation_mm == 0:
        return 0.0  # No rain, 0% likelihood
    elif 0 < precipitation_mm <= 0.1:
        return 0.1  # Very low chance of rain
    elif 0.1 < precipitation_mm <= 1:
        # Scale between 0.1 (10%) to 0.4 (40%) likelihood
        return 0.1 + ((precipitation_mm - 0.1) / (1 - 0.1)) * (0.4 - 0.1)
    elif 1 < precipitation_mm <= 5:
        # Scale between 0.4 (40%) to 0.6 (60%) likelihood
        return 0.4 + ((precipitation_mm - 1) / (5 - 1)) * (0.6 - 0.4)
    elif 5 < precipitation_mm <= 10:
        # Scale between 0.6 (60%) to 0.8 (80%) likelihood
        return 0.6 + ((precipitation_mm - 5) / (10 - 5)) * (0.8 - 0.6)
    elif precipitation_mm > 10:
        # Scale beyond 10 mm: cap the likelihood at 1.0 (100%)
        return min(0.8 + ((precipitation_mm - 10) / (50 - 10)) * (1.0 - 0.8), 1.0)



# Function to calculate the average values
def calculate_averages(date, lat, lon, api_key):
    current_year = datetime.now().year
    total_min_temp = 0
    total_max_temp = 0
    total_cloud_cover = 0
    total_precipitation = 0
    total_humidity = 0
    num_years = 3  # Last 3 years
    # Get data for the last 3 years, excluding this year
    for year_offset in range(1, 4):
        historical_date = date - relativedelta(years=year_offset)
        weather_data = get_weather_for_date(lat, lon, historical_date, api_key)
        # Accumulate the values for averaging
        total_min_temp += weather_data["temperature"]["min"]
        total_max_temp += weather_data["temperature"]["max"]
        total_cloud_cover += weather_data["cloud_cover"]["afternoon"]
        total_precipitation += weather_data["precipitation"]["total"]
        total_humidity += weather_data["humidity"]["afternoon"]
    # Calculate the averages
    avg_min_temp = total_min_temp / num_years
    avg_max_temp = total_max_temp / num_years
    avg_cloud_cover = total_cloud_cover / num_years
    avg_precipitation = total_precipitation / num_years
    avg_humidity = total_humidity / num_years
    return {
        "min_temp": avg_min_temp,
        "max_temp": avg_max_temp,
        "cloud_cover": avg_cloud_cover,
        "rain_amount_mm": avg_precipitation,
        "humidity": avg_humidity
    }



def get_weather_for_future_date(date, lat, lon, api_key):
    current_date = datetime.now()
    eight_days_in_future = current_date + timedelta(days=8)
    print(f"Current date: {current_date}")
    print(f"Requested date: {date}")
    print(f"{lat}, {lon}")
    if date < eight_days_in_future:
        print("Using more accurate daily weather <8 days")
        weather_url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&units=imperial&exclude=current,minutely,hourly,alerts&appid={api_key}"
        response = requests.get(weather_url)
        weather_data = response.json()
        for day in weather_data['daily']:
            forecast_date = datetime.fromtimestamp(day['dt'])
            if forecast_date.date() == date.date():
            return {
                "min_temp": day['temp']['min'],
                "max_temp": day['temp']['max'],
                "cloud_cover": day['clouds'],
                "rain_amount_mm": day.get('rain', 0),
                "humidity": day["humidity"]
            }
        weather_data_str = str(weather_data)
        raise ValueError(f"{date} not in forecast {weather_data_str}")
    else:
        print("Using less accurate historical estimate for weather >=8 days")
        date_day = date.strftime('%Y-%m-%d')
        return calculate_averages(date_day, lat, lon, api_key=api_key)


def get_drive_time(api_key, origin_lat, origin_lng, dest_lat, dest_lng):
    # Define the API endpoint and parameters
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    # Specify the origin and destination
    origin = f"{origin_lat},{origin_lng}"
    destination = f"{dest_lat},{dest_lng}"
    # Set the parameters for the request
    params = {
        "origins": origin,
        "destinations": destination,
        "mode": "driving",  # You can change this to "walking", "bicycling", etc.
        "key": api_key
    }
    # Make the request
    response = requests.get(url, params=params)
    data = response.json()
    # Check if the request was successful
    if data['status'] == 'OK':
        # Extract the travel time from the response (in seconds)
        duration = data['rows'][0]['elements'][0]['duration']['text']
        return duration
    else:
        print("Error:", data['status'])
        return None




#37.765195,-122.454539 #301 carl
origin_lat = 37.765195
origin_lng = -122.454539
date = datetime(2024, 9, 22)



OPENWEATHER_API_KEY = os.environ["OPENWEATHER_API_KEY"]
RECREATION_GOV_API_KEY = os.environ["RECREATION_GOV_API_KEY"]
GOOGLE_SEARCH_API_KEY = os.environ["GOOGLE_SEARCH_API_KEY"]



lat, lon = get_lat_lon_of_campground(campground_id, RECREATION_GOV_API_KEY)

campground_info = get_weather_for_future_date(date, lat, lon, OPENWEATHER_API_KEY)

drive_time = get_drive_time(GOOGLE_SEARCH_API_KEY, origin_lat, origin_lng, lat, lon)
campground_info.update({"drive_time: {drive_time}"})








# ALERTS (DYNAMIC)

from datetime import datetime

@rate_limited_site
def get_campground_alerts(campground_id)
    url = f"https://www.recreation.gov/api/communication/external/alert?location_id={campground_id}&location_type=Campground"
    headers = {
        'accept': 'application/json, text/plain, */*',
        'User-Agent': random.choice(user_agents)
    }
    response = requests.get(url, headers=headers)

    active_alerts = []
    for alert in response.json():
        # Convert the ISO string with "Z" to UTC timezone datetime
        end_at = datetime.fromisoformat(alert["end_at"].replace("Z", "+00:00"))
        begin_at = datetime.fromisoformat(alert["begin_at"].replace("Z", "+00:00"))
        # Check if end_at is in the future and begin_at is in the past
        is_valid = datetime.utcnow() < end_at and datetime.utcnow() > begin_at
        if is_valid and alert["canceled_at"] is None:
            active_alerts.append(alert['body'])
    return active_alerts






#{'campground': {'facility_id': '234382', 'parent_asset_id': '1070', 'inventory_type_id': '3', 'facility_type': 'STANDARD', 'order_components': {'camping_equipment': True, 'group_leader_details': True, 'group_size': True, 'num_vehicles': True, 'pass': True}, 'facility_lookups': None, 'facility_description_map': {'Facilities': 'Spanish Creek campground offers several single-family campsites that accommodate both tent and RV camping, however hookups are not available.<br/><br/>\n Each site is equipped with tables and campfire rings with grills. Vault toilets and drinking water are also provided. A full-service store, gas and phone service is available less than 10 miles away.\n', 'Natural Features': 'This campground is located in the Plumas National Forest, which is attractive to outdoor enthusiasts because of its many streams and lakes, beautiful deep canyons, rich mountain valleys, meadows, and lofty peaks. Spanish Creek is in the Feather River Canyon, at an elevation of 2,000 feet.\n', 'Nearby Attractions': 'Within the Plumas National Forest, Spanish Creek campground is just a few short miles from Indian Falls. This is one attraction not to miss. Some have said that the mist created by the falls resembles a feather -- thus naming the Feather River. Just southeast on Highway 70 from Spanish Creek Campground is the quaint high Sierra town of Quincy. We recommend walking around the town if you get a chance. Very close to the campground is the Butterfly Valley Botanical Area. This is also a neat spot to explore. Before you get to the town of Quincy you will pass the Mount Hough Ranger District - a wonderful stop to discover more information about local area attractions. ', 'Overview': 'Spanish Creek Campground is located on Highway 70 just east of the Highway 89 intersection; just east of where Banish Creek and Indian Creek merge together to create the east branch of the North Fork Feather River. The campground is right on Spanish Creek with a very popular swimming hole. Although the campground has been recently upgraded, it still holds the charm that it did in years past. ', 'Recreation': 'Anglers enjoy a healthy supply of rainbow trout in the nearby Feather River, which is within walking distance from the campground. The river and nearby Spanish Creek are also popular for swimming and wading activities.\n', 'contact_info': 'For facility specific information, please call (530) 927-7878.'}, 'facility_name': 'SPANISH CREEK CAMPGROUND', 'city': 'Belden', 'state': 'California', 'facility_adaaccess': 'N', 'facility_directions': 'From Oroville, travel east on Highway 70 for 75 miles. The turnoff to the campground is two miles past Highway 89. From Quincy, travel west on Highway 70 for 8 miles. Campground is across the Spanish Creek bridge.\n', 'facility_email': '', 'facility_email_display': False, 'facility_map_url': '', 'facility_latitude': 40.0269444, 'facility_longitude': -120.9644444, 'facility_pho












