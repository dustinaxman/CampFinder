import requests
from datetime import datetime, timedelta, timezone
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
    if isinstance(date, str):
        # Convert string to datetime
        date = datetime.strptime(date, '%Y-%m-%d')
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
    current_date = datetime.now(timezone.utc)
    eight_days_in_future = current_date + timedelta(days=8)
    print(f"Current date: {current_date}")
    print(f"Requested date: {date}")
    print(f"{lat}, {lon}")
    date = datetime.fromisoformat(date.replace("Z", "+00:00"))
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

