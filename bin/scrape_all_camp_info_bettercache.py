import json
import os
import threading
import random
import time
import requests
import sys


backup_file = "all_data_backup2_GOOD.jsonl"
errors_file = "errors_file.txt"

lock_site = threading.Lock()
lock_api = threading.Lock()

last_called_site = 0
last_called_api = 0

# Set up different intervals for each rate limit
MIN_INTERVAL_SITE = 60 / 30   
MIN_INTERVAL_API = 60 / 2000 

def rate_limited_site(func):
    def wrapper(*args, **kwargs):
        global last_called_site
        with lock_site.acquire(timeout=5):
            now = time.time()
            if now - last_called_site < MIN_INTERVAL_SITE:
                time_to_wait = MIN_INTERVAL_SITE - (now - last_called_site)
                time.sleep(time_to_wait)
            last_called_site = time.time()
        return func(*args, **kwargs)
    return wrapper

def rate_limited_api(func):
    def wrapper(*args, **kwargs):
        global last_called_api
        with lock_api.acquire(timeout=5):
            now = time.time()
            if now - last_called_api < MIN_INTERVAL_API:
                time_to_wait = MIN_INTERVAL_API - (now - last_called_api)
                time.sleep(time_to_wait)
            last_called_api = time.time()
        return func(*args, **kwargs)
    return wrapper


user_agents = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    # Chrome on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:91.0) Gecko/20100101 Firefox/91.0",
    # Chrome on Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    # Firefox on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.48",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36 Edg/92.0.902.67",
    # Safari on macOS
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    # Safari on iOS
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 13_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Mobile/15E148 Safari/604.1",
    # Opera on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.172",
    # Android - Chrome and Firefox
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.164 Mobile Safari/537.36",
    "Mozilla/5.0 (Android 11; Mobile; rv:89.0) Gecko/89.0 Firefox/89.0",
    # Generic User Agents for diversity
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
]



RECREATION_GOV_API_KEY = os.environ["RECREATION_GOV_API_KEY"]

def write_errors(errors_dict):
    with open(errors_file, 'a+') as f:
        f.write(json.dumps(errors_dict) + '\n')

#### get list of campsite ids from campground id ###
#  EXTRACT: CampsiteID
# @rate_limited_api
# def get_campsite_list_for_campground(campground_id, api_key):
#     headers = {
#         "accept": 'application/json',
#         "apikey": api_key 
#     }
#     offset = 0
#     all_campsites = []
#     while True:
#         url = f"https://ridb.recreation.gov/api/v1/facilities/{campground_id}/campsites?limit=50&offset={offset}"
#         response = requests.get(url,  headers=headers)
#         data = response.json()
#         all_campsites.extend(data["RECDATA"])
#         offset += 50
#         if len(data["RECDATA"]) == 0:
#             break
#     return all_campsites
@rate_limited_api
def get_campsite_list_for_campground(campground_id, api_key):
    headers = {
        "accept": 'application/json',
        "apikey": api_key 
    }
    offset = 0
    url = f"https://ridb.recreation.gov/api/v1/facilities/{campground_id}/campsites?limit=50000&offset={offset}"
    for i in range(10):
        response = requests.get(url,  headers=headers)
        if response.status_code == 200:
            break
    else:
        function_name = "get_campsite_list_for_campground"
        print(campground_id)
        print(response.status_code)
        print(response)
        print(function_name)
        write_errors({"status_code":response.status_code, "response": response.text, "function": function_name, "params": campground_id})
        raise ValueError(f"Error on {campground_id} in function {function_name}, {str(response)}, {str(response.status_code)}")
    data = response.json()
    return data["RECDATA"]


###  get campsite need to know

@rate_limited_site
def get_campsite_info_notices(campsite_id):
    #EXTRACT: notices
    headers = {
        "User-Agent": random.choice(user_agents)
    }
    rating_info = {}
    url = f"https://www.recreation.gov/api/camps/campsites/{campsite_id}"
    for i in range(10):
        response = requests.get(url,  headers=headers)
        if response.status_code == 200:
            break
    else:
        function_name = "get_campsite_info_notices"
        print(campsite_id)
        print(response.status_code)
        print(response)
        print(function_name)
        write_errors({"status_code":response.status_code, "response": response.text, "function": function_name, "params": campsite_id})
        raise ValueError(f"Error on {campsite_id} in function {function_name}, {str(response)}, {str(response.status_code)}")
    data = response.json()
    return data


@rate_limited_api
def get_campsite_info(campsite_id, api_key):
    headers = {
        "accept": 'application/json',
        "apikey": api_key 
    }
    url = f"https://ridb.recreation.gov/api/v1/campsites/{campsite_id}"
    for i in range(10):
        response = requests.get(url,  headers=headers)
        if response.status_code == 200:
            break
    else:
        function_name = "get_campsite_info"
        print(campsite_id)
        print(response.status_code)
        print(response)
        print(function_name)
        write_errors({"status_code":response.status_code, "response": response.text, "function": function_name, "params": campsite_id})
        raise ValueError(f"Error on {campsite_id} in function {function_name}, {str(response)}, {str(response.status_code)}")
    data = response.json()
    if data and len(data) > 0 and ("ATTRIBUTES" in data[0]):
        campsite_attribute_dict = {campsite_attribute["AttributeName"]:campsite_attribute["AttributeValue"] for campsite_attribute in data[0]["ATTRIBUTES"]}
    else:
        campsite_attribute_dict = None
    return {
        "max_num_people": campsite_attribute_dict.get("Max Num of People", None),
        "near_water": (("LAKE ACCESS" in campsite_attribute_dict) or ("Proximity to Water" in campsite_attribute_dict)),
        "water_spigot": campsite_attribute_dict.get("WATER SPIGOT", None),
        "drinking_water": campsite_attribute_dict.get("DRINKING WATER", None),
        "campfire_allowed": campsite_attribute_dict.get("Campfire Allowed", None),
        "type_of_site_access": campsite_attribute_dict.get("Site Access", None),
        "facility_id": data[0]["FacilityID"],
        "all_attributes": campsite_attribute_dict
        }


###### GET CAMPSITE REVIEWS!!! #######

@rate_limited_site
def get_campsite_reviews(campsite_id):
    #EXTRACT
    # review["review"]
    #     review["not_helpful_votes_count"]
    #     review["not_helpful_votes_count"]
    #     review["rating"]
    #
    headers = {
        "User-Agent": random.choice(user_agents)
    }
    rating_info = {}
    url = f"https://www.recreation.gov/api/ratingreview/public?location_id={campsite_id}&location_type=Campsite&page_size=1000&sort_key=MOST_RECENT&start_key=&rating="
    for i in range(10):
        response = requests.get(url,  headers=headers)
        if response.status_code == 200:
            break
    else:
        function_name = "get_campsite_reviews"
        print(campground_id)
        print(response.status_code)
        print(response)
        print(function_name)
        write_errors({"status_code":response.status_code, "response": response.text, "function": function_name, "params": campsite_id})
        raise ValueError(f"Error on {campsite_id} in function {function_name}, {str(response)}, {str(response.status_code)}")
    data = response.json()
    return data


#OVERALL RATING AND COuNT and CELL COVERAGE
@rate_limited_site
def get_campground_ratings(campground_id):
    headers = {
        "User-Agent": random.choice(user_agents)
    }
    rating_info = {}
    url = f"https://www.recreation.gov/api/ratingreview/aggregate?location_id={campground_id}&location_type=Campground&page_size=10&sort_key=MOST_RECENT"
    for i in range(10):
        response = requests.get(url,  headers=headers)
        if response.status_code == 200:
            break
    else:
        function_name = "get_campground_ratings"
        print(campground_id)
        print(response.status_code)
        print(response)
        print(function_name)
        write_errors({"status_code":response.status_code, "response": response.text, "function": function_name, "params": campground_id})
        raise ValueError(f"Error on {campground_id} in function {function_name}, {str(response)}, {str(response.status_code)}")
    data = response.json()
    return data

    #{'aggregate_cell_coverage_ratings': [{'average_rating': 1.7586206896551724, 'carrier': 'Verizon', 'number_of_ratings': 29, 'star_counts': {'0': 4, '1': 7, '2': 10, '3': 8, '4': 0}}, {'average_rating': 0.2777777777777778, 'carrier': 'AT&T', 'number_of_ratings': 18, 'star_counts': {'0': 15, '1': 2, '2': 0, '3': 1, '4': 0}}, {'average_rating': 0.42857142857142855, 'carrier': 'T-Mobile', 'number_of_ratings': 7, 'star_counts': {'0': 4, '1': 3, '2': 0, '3': 0, '4': 0}}, {'average_rating': 1.5, 'carrier': 'Sprint', 'number_of_ratings': 2, 'star_counts': {'0': 1, '1': 0, '2': 0, '3': 1, '4': 0}}], 'average_rating': 4.203125, 'location_id': '234382', 'location_type': 'Campground', 'number_of_ratings': 64, 'star_counts': {'1': 2, '2': 5, '3': 10, '4': 8, '5': 39}}



@rate_limited_site
def get_campground_general_info(campground_id):
    url = f"https://www.recreation.gov/api/camps/campgrounds/{campground_id}"
    headers = {
        'accept': 'application/json, text/plain, */*',
        'User-Agent': random.choice(user_agents)
    }
    for i in range(10):
        response = requests.get(url,  headers=headers)
        if response.status_code == 200:
            break
    else:
        function_name = "get_campground_general_info"
        print(campground_id)
        print(response.status_code)
        print(response)
        print(function_name)
        write_errors({"status_code":response.status_code, "response": response.text, "function": function_name, "params": campground_id})
        raise ValueError(f"Error on {campground_id} in function {function_name}, {str(response)}, {str(response.status_code)}")
    data = response.json()
    return data
    # campground_info_text = data["campground"]["facility_description_map"]
    # campground_name = data["campground"]["facility_name"]
    # campground_amenities = data["campground"]["amenities"]
    # campground_noticies = data["campground"]["notices"]
    # toilet_type = [campground_amenities[k] for k in campground_amenities.keys() if "Toilet" in k]
    # return {"campground_info_text": campground_info_text,
    #         "campground_name": campground_name,
    #         "campground_amenities": campground_amenities,
    #         "campground_noticies": campground_noticies,
    #         "toilet_type": toilet_type
    # }


########## REVIEWS #########


#EXTRACT:
# review
# not_helpful_votes_count
# helpful_votes_count
# rating
# for review in d["ratings"]
# d["ratings"][-1]["review"]
# d["last_evaluated_key"]

#https://www.recreation.gov/api/ratingreview/public?parent_location_id=234382&parent_location_type=Campground&page_size=10&sort_key=MOST_RECENT&start_key=&rating=
@rate_limited_site
def get_campground_reviews(campground_id):
    start_key = ""
    url = f"https://www.recreation.gov/api/ratingreview/public?parent_location_id={campground_id}&parent_location_type=Campground&page_size=10000&sort_key=MOST_RECENT&start_key={start_key}"
    headers = {
            'accept': 'application/json, text/plain, */*',
            'User-Agent': random.choice(user_agents)
        }
    for i in range(10):
        response = requests.get(url,  headers=headers)
        if response.status_code == 200:
            break
    else:
        function_name = "get_campground_reviews"
        print(campground_id)
        print(response.status_code)
        print(response)
        print(function_name)
        write_errors({"status_code":response.status_code, "response": response.text, "function": function_name, "params": campground_id})
        raise ValueError(f"Error on {campground_id} in function {function_name}, {str(response)}, {str(response.status_code)}")
    data = response.json()
    return data

def file_exists_and_not_empty(file_path):
    # Check if the file exists and is not empty
    return os.path.isfile(file_path) and os.path.getsize(file_path) > 0



if __name__ == "__main__":
    #with open("/Users/deaxman/Downloads/RIDBFullExport_V1_JSON/Facilities_API_v1.json", "r") as f:
    with open("Facilities_API_v1.json", "r") as f:
        jsn = json.load(f)

    if file_exists_and_not_empty(backup_file):
        with open(backup_file, "r") as f:
            cached_campground_ids = set([json.loads(line.strip())["campground_id"] for line in f])
    else:
        cached_campground_ids = set([])
    c = 0
    total_failures = 0
    for idx, facility in enumerate(jsn["RECDATA"]):
        if facility["Reservable"] and facility["FacilityTypeDescription"] == "Campground":
            print(facility['FacilityID'], facility['FacilityName'], flush=True)
            time.sleep(0.2)
            if facility["FacilityID"] not in cached_campground_ids:
                try:
                    #50 per MINUTE
                    campground_ratings = get_campground_ratings(facility["FacilityID"])
                    #50 per MINUTE
                    general_campground_info = get_campground_general_info(facility["FacilityID"])
                    #50 per MINUTE
                    campground_reviews = get_campground_reviews(facility["FacilityID"])
                    # 50 per SECOND
                    all_campsites = get_campsite_list_for_campground(facility["FacilityID"], RECREATION_GOV_API_KEY) #0.5 seconds
                    #add all_campsites
                    for campsite in all_campsites:
                        if "CampsiteID" in campsite:
                            #50 per MINUTE
                            campsite_notices = get_campsite_info_notices(campsite["CampsiteID"])
                            campsite["notices"] = campsite_notices
                            #50 per SECOND
                            general_campsite_info = get_campsite_info(campsite["CampsiteID"], RECREATION_GOV_API_KEY)
                            campsite["campsite_info"] = general_campsite_info
                            campsite_reviews = get_campsite_reviews(campsite["CampsiteID"])
                            campsite["campsite_reviews"] = campsite_reviews
                    campground_dict = {
                        "campground_id": facility["FacilityID"],
                        "campground_name": facility["FacilityName"],
                        "campground_latitude": facility["FacilityLatitude"],
                        "campground_longitude": facility["FacilityLongitude"],
                        "campground_ratings": campground_ratings,
                        "general_campground_info": general_campground_info,
                        "campground_reviews": campground_reviews,
                        "campsites": all_campsites,
                    }
                    with open(backup_file, 'a+') as f:
                        f.write(json.dumps(campground_dict) + '\n')
                except Exception as e:
                    total_failures += 1
                    print(e)
                    if total_failures > 10:
                        sys.exit(1)
            else:
                print("FOUND IN BACKUP")
            print(f"Finished idx: {idx}, {c} of 4525")
            print(f"Backed up data for facility: {facility['FacilityID']}")
            c += 1

        else:
            print(f"{facility['FacilityID']} NOT CAMPGROUND idx: {idx} of 4500")





