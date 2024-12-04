import requests
from datetime import datetime
from collections import defaultdict
import random
import asyncio
import aiohttp
from aiolimiter import AsyncLimiter
from yarl import URL
import urllib.parse
from urllib.parse import urlparse, parse_qs, quote, urlencode
from dateutil.relativedelta import relativedelta

API_PER_MINUTE_REQUEST_RATE_LIMIT = 20

def encode_params(params):
    return '&'.join([f"{key}={quote(str(value), safe='')}" for key, value in params.items()])


def find_matching_date_periods(start_date, end_date, num_nights, days_of_the_week, all_campsite_availabilities):
    campsite_available_dates = {}
    for k, v in all_campsite_availabilities.items():
        available_dates = [date for date, availability in v.items() if availability == "Available"]
        if available_dates:
            campsite_available_dates[k] = available_dates
    # Prepare a dictionary to store the final bookings
    bookings = {}
    # Iterate over each campsite and its available dates
    for campsite, available_dates in campsite_available_dates.items():
        # Convert available dates to datetime objects for comparison
        available_dates = [datetime.fromisoformat(date.replace("Z", "")) for date in available_dates]
        # Filter dates that are within the start and end date range
        filtered_dates = [date for date in available_dates if start_date <= date <= end_date]
        # Filter dates based on the days of the week condition
        filtered_dates = [date for date in filtered_dates if date.weekday() in days_of_the_week]
        # Sort the dates just to be sure
        filtered_dates.sort()
        # Now group dates into sets of consecutive nights
        campsite_bookings = []
        for i in range(len(filtered_dates) - num_nights + 1):
            group = filtered_dates[i:i + num_nights]
            # Check if the dates in this group are consecutive
            if all((group[j+1] - group[j]).days == 1 for j in range(num_nights - 1)):
                # Add the group of dates to the bookings for this campsite
                campsite_bookings.append(group)
        # Convert datetime objects back to ISO format strings
        campsite_bookings = [[date.isoformat() + "Z" for date in group] for group in campsite_bookings]
        # Add the bookings to the final result if any valid groups were found
        if campsite_bookings:
            bookings[campsite] = campsite_bookings
    return bookings


def get_calls_for_campgrounds_in_date_range(campground_list, start_date, end_date):
    base_url = "https://www.recreation.gov/api/camps/availability/campground/{}/month"
    headers_list = [
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Referer": "https://www.recreation.gov"
        },
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Referer": "https://www.recreation.gov"
        },
        {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            "Accept": "application/json",
            "Referer": "https://www.recreation.gov"
        }
    ]
    call_info_list = []
    for campground in campground_list:
        current_date = datetime(start_date.year, start_date.month, 1)
        while current_date <= end_date:
            formatted_month = current_date.strftime("%Y-%m-01T00:00:00.000Z")
            query_params = {"start_date": formatted_month}  
            call_info = {
                "campground": campground,
                "url": base_url.format(campground),
                "headers": random.choice(headers_list),
                "params": query_params,
                "timeout": 30
            }
            call_info_list.append(call_info)
            current_date += relativedelta(months=1)
    return call_info_list



async def make_request(session, call_info):
    all_campsite_availabilities = defaultdict(dict)
    try:
        # Manually encode the query parameters (keep %3A for colons)
        encoded_query = encode_params(call_info["params"])
        url = call_info["url"]
        aiohttp_url = URL(f"{url}?{encoded_query}", encoded=True)
        headers = call_info["headers"]
        timeout = aiohttp.ClientTimeout(total=call_info["timeout"])
        print(f"Sending request to: {url}")
        print(f"Headers: {headers}")
        async with session.get(aiohttp_url, headers=headers, timeout=timeout, ssl=False) as response:
            print(f"Response status: {response.status}")
            print(f"Response headers: {response.headers}")
            response_text = await response.text()
            print(f"Response body: {response_text[:200]}...")  # Print first 200 characters
            response.raise_for_status()
            data = await response.json()
            campsites = data.get("campsites", {})
            for campsite_id, campsite_data in campsites.items():
                all_campsite_availabilities[(call_info["campground"], campsite_id)].update(campsite_data.get("availabilities", {}))
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        print(f"Error making request for campground {call_info['campground']}: {str(e)}")
    return all_campsite_availabilities

import time
async def call_and_merge(call_info_list, request_rate_per_minute=30):
    all_campsite_availabilities = defaultdict(dict)
    limiter = AsyncLimiter(request_rate_per_minute, 60)
    async with aiohttp.ClientSession(trust_env=True) as session:
        for call_info in call_info_list:
            async with limiter:
                print(time.time())
                result = await make_request(session, call_info)
                for (campground_id, campsite_id), date_availability_dict in result.items():
                   all_campsite_availabilities[(campground_id, campsite_id)].update(date_availability_dict)
    return all_campsite_availabilities


def get_available_campsites(campground_list, start_window_datetime, end_window_datetime, num_nights=1, days_of_the_week=None):
  call_info_list = get_calls_for_campgrounds_in_date_range(campground_list, start_window_datetime, end_window_datetime)
  print("start call and merge")
  print(len(call_info_list))
  all_campsite_availabilities = asyncio.run(call_and_merge(call_info_list, request_rate_per_minute=API_PER_MINUTE_REQUEST_RATE_LIMIT))
  print("end call and merge")
  all_bookings_matching_search = find_matching_date_periods(start_window_datetime, end_window_datetime, num_nights, days_of_the_week, all_campsite_availabilities)
  return all_bookings_matching_search


# # Example usage
# campground_list = [234073, 234541]
# start = datetime(2024, 10, 3)
# end = datetime(2024, 12, 10)

# call_info_list = get_calls_for_campgrounds_in_date_range(campground_list, start, end)
# print(call_info_list)

# # Run the async function
# all_campsite_availabilities = asyncio.run(call_and_merge(call_info_list, request_rate_per_minute=10))
# print(all_campsite_availabilities)


# all_bookings_matching_search = find_matching_date_periods(start, end, num_nights, days_of_the_week, all_campsite_availabilities)

