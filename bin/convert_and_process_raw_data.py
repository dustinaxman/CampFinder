import sys
import json
from bs4 import BeautifulSoup
import math
from collections import defaultdict


def calculate_token_count(text):
    encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text, disallowed_special=()))


def get_campground_activities(general_campground_info):
    campground_info = general_campground_info["campground"]
    if "activities" in campground_info and campground_info["activities"]:
        activities = campground_info["activities"]
        return [activity["activity_name"].lower() for activity in activities]
    else:
        return []


amenities_map = { 
    "Accessible Picnic Areas": "Accessible Picnic Area",
    "Accessible Vault Toilets": "Accessible Vault Toilet",
    "Basketball Courts": "Basketball Court",
    "Boat Rentals": "Boat Rental",
    "Electric Hook-Up": "Electric Hookups",
    "Firewood Vender": "Firewood",
    "Firewood Vendor": "Firewood",
    "Flush Toilets": "Flush Toilet",
    "Picnic Shelters": "Picnic Shelter",
    "Grills": "Grill",
    "Picnic Tables": "Picnic Table",
    "Playgroiund": "Playground",
    "Restrooms": "Restroom",
    "Showers": "Shower",
    "Vault Toilets": "Vault Toilet",
    "Tent Pads": "Tent Pad",
    "Visitors Center": "Visitor Center",
    "Volleyball Courts": "Volleyball Court"
}

def get_campground_amenities(general_campground_info):
    campground_info = general_campground_info["campground"]
    if "amenities" in campground_info and campground_info["amenities"]:
        amenities = campground_info["amenities"]
        return [amenities_map[amenity.lower()] if amenity.lower() in amenities_map else amenity.lower() for amenity in amenities]
    else:
        return []

# def get_toilet_type(general_campground_info):
#     campground_amenities = get_campground_amenities(general_campground_info)
#     toilet_type = [campground_amenities[k] for k in campground_amenities if "Toilet" in k]
#     return toilet_type


# def get_drinking_water_types(general_campground_info):
#     campground_amenities = get_campground_amenities(general_campground_info)
#     drinking_water_type = [campground_amenities[k] for k in campground_amenities if "Drinking" in k]
#     return drinking_water_type


#"campground_ratings":  "aggregate_cell_coverage_ratings" 
def get_cell_coverage(aggregate_cell_coverage_ratings, agg_type="All"):
    if agg_type == "All":
        total_ratings = 0
        weighted_rating_sum = 0
        aggregated_star_counts = {"0": 0, "1": 0, "2": 0, "3": 0, "4": 0}
        # Aggregate data across carriers
        for carrier in aggregate_cell_coverage_ratings:
            num_ratings = carrier["number_of_ratings"]
            weighted_rating_sum += carrier["average_rating"] * num_ratings
            total_ratings += num_ratings   
            # Sum star counts
            for star, count in carrier["star_counts"].items():
                aggregated_star_counts[star] += count
        # Calculate overall average rating
        average_rating = weighted_rating_sum / total_ratings if total_ratings > 0 else 0
        # Prepare final aggregated result
        aggregated_result = {
            "average_rating": average_rating,
            "number_of_ratings": total_ratings,
            "star_counts": aggregated_star_counts
        }
    else:
        selected_carrier = [c for c in aggregate_cell_coverage_ratings if c["carrier"] == agg_type][0]
        aggregated_result = {
            "average_rating_cell_coverage": selected_carrier["average_rating"],
            "number_of_ratings_cell_coverage": selected_carrier["number_of_ratings"],
            "star_counts_cell_coverage": selected_carrier["star_counts"]
        }
    return aggregated_result


#"campground_ratings"
def get_campground_ratings(campground_ratings):
    return {
        "average_rating": campground_ratings["average_rating"],
        "number_of_ratings": campground_ratings["number_of_ratings"],
        "star_counts": campground_ratings["star_counts"]
    }


#   "general_campground_info" "campground" "facility_description_map"
# ]

def clean_html(text):
        return BeautifulSoup(text, "html.parser").get_text()

def get_campground_notices(general_campground_info):
    campground_info = general_campground_info["campground"]
    if "notices" not in campground_info:
        notices = []
    else:
        notices = campground_info["notices"]
    return [clean_html(notice.get("notice_text", "")) for notice in notices]


def get_campground_info(general_campground_info):
    campground_info = general_campground_info.get("campground", {})
    facility_description_map = campground_info.get("facility_description_map", {})
    if campground_info is None:
        campground_info = {}
    if facility_description_map is None:
        facility_description_map = {}
    # Initialize an empty formatted string
    formatted_string = ""
    # Iterate over the dictionary and format each section
    for section, content in facility_description_map.items():
        formatted_string += f"{section}:\n"
        formatted_string += f"{clean_html(content)}\n"
    sections_to_add = set(["cancellation_description"])
    for section, content in campground_info.items():
        if section in sections_to_add:
            formatted_string += f"{section}:\n"
            formatted_string += f"{clean_html(content)}\n"
    return formatted_string


def get_campground_reviews(campground_reviews):
    all_reviews = []
    for review in campground_reviews["ratings"]:
        created_at = review.get("created_at", None)
        helpful_votes_count = review.get("helpful_votes_count", None)
        not_helpful_votes_count = review.get("not_helpful_votes_count", None)
        rating = review.get("rating", None)
        accessibility_comment = review.get("accessibility_comment", None)
        review_comment = review.get("review", None)
        reservation_info = review.get("reservation_info", None)
        if reservation_info:
            campsite_id = reservation_info.get("campsite_id", None)
            campsite_name = reservation_info.get("product_description", None)
            campsite_reserved_date = reservation_info.get("start_date", None)
        else:
            campsite_id = None
            campsite_name = None
            campsite_reserved_date = None
        all_reviews.append({
                "created_at": created_at,
                "upvote_score": helpful_votes_count - not_helpful_votes_count,
                "rating": rating,
                "review": f"{accessibility_comment} {review_comment}".strip(),
                "campsite_id": campsite_id,
                "campsite_name": campsite_name,
                "campsite_reserved_date": campsite_reserved_date
            })
    return all_reviews


def get_campsites(campsites):
    all_campsites = []
    for campsite in campsites:
        campsite_formatted = {}
        campsite_formatted["campsite_id"] = campsite["CampsiteID"]
        campsite_formatted["accessible"] = campsite["CampsiteAccessible"]
        campsite_formatted["latitude"] = campsite["CampsiteLatitude"]
        campsite_formatted["longitude"] = campsite["CampsiteLongitude"]
        campsite_formatted["name"] = campsite["CampsiteName"]
        campsite_formatted["reservable"] = campsite["CampsiteReservable"]
        campsite_formatted["notices"] = [notice["notice_text"] for notice in campsite.get("notices", {}).get("campsite", {}).get("notices", [])]
        campsite_formatted["attributes"] = get_and_process_all_attributes_from_campsite(campsite)
        all_campsites.append(campsite_formatted)
    return all_campsites


def process_attr_vals(val):
    if isinstance(val, str):
        val = val.lower().replace("_", " ").strip()
        if val in ["y", "yes", "true"]:
            val = True
        elif val in ["n", "no", "false"]:
            val = False
        elif val.isdigit():
            val = float(val)
        else:
            pass #print(val)
    elif val is None:
        val = False
    elif isinstance(val, bool):
        pass
    else:
        print(val, type(val))
    return val


def clean_data(data):
    # Mapping for conversions
    conversions = {
        "max num people": "max num of people",
        "max num horses": "max num of horses",
        "max num vehicles": "max num of vehicles",
        "min num people": "min num of people",
        "min num vehicles": "min num of vehicles",
        "num bedrooms": "num rooms",
        "num of bedrooms": "num rooms",
        "num of rooms": "num rooms",
        "num beds": "num of beds",
        "site access": "type of site access",
        "site height/overhead clearance": "site height",
        "proximity water": "proximity to water",
        "check-in": "checkin time",
        "check-out": "checkout time",
        "electric hookup": "electricity hookup",
        "electric hookups": "electricity hookup",
        "water hookups": "water hookup",
        "capacity/size rating": "capacity rating",
        "hike in distance": "hike in distance to site",
        "is equip mandatory": "is equipment mandatory",
        "amphitheather": "amphitheater",
    }
    # Keys to remove
    removals = {"map x coordinate", "map y coordinate", "facility id", ""}
    keys_to_map_to_bool_false_if_empty = ["pets allowed", "water hookup", "campfire allowed", "double driveway", "electricity hookup", "is equipment mandatory", "shade"]
    empty_values = ["", "na", "n/a", "none", "nan"]
    keys_to_remove_foot_quote = ["hike in distance to site", "driveway length", "max vehicle length", "site height", "site length", "site width", "tent pad length", "tent pad width"]
    # Process the data
    cleaned_data = []
    for key, value in data:
        # If the key is in removals, skip this tuple
        if key in removals:
            continue
        # If the key is in conversions, update the key
        if key in conversions:
            key = conversions[key]
        # Add the modified tuple to the cleaned_data list
        if key == value:
            value = True
        if value in empty_values and key in keys_to_map_to_bool_false_if_empty:
            value = False
        if key == "type of site access" and value in empty_values:
            value = "drive-in"
        if key in ["driveway entry", "type of site access"] and isinstance(value, str):
            value = value.replace(" ", "-")
        if key == "max num of horses" and value == "`":
            value = "n/a"
        if key == "placed on map":
            if value == 0:
                value = False
            elif value == 1:
                value = True
        if key == "restaurant":
            if value == "":
                value = False
        if key == "dump station":
            if value == "":
                value = False
        if key == "water hookup":
            if value == "water hookups":
                value = True
        if key == "pets allowed":
            if value == "50 amp":
                value = True
            elif value == "domestic":
                value = True
            elif value == "domestic,horse":
                value = "horse"
        if key == "min num of people":
            if value == "":
                value = 0
        if key == "coin showers":
            if value == "":
                value = False
        if key == "max vehicle length":
            if isinstance(value, str):
                value = value.replace("ft", "").replace("rv/trailer", "").replace("+", "").strip()
                if "-" in value:
                    value = value.split("-")[1]
                if value in ["n/a", "none", "nan", ""]:
                    value = 0
                if isinstance(value, str) and value.isdigit():
                    value = int(value)
        if key == "picnic table" and value == "":
            value = False
        if key == "general store" and value == "":
            value = False
        if key == "site width":
            if isinstance(value, str):
                value = value.replace("ft", "").replace("feet", "").replace("+", "").strip()
                if "/" in value:
                    value = value.split("/")[0]
                if "*" in value:
                    value = value.split("*")[0].strip()
                if value == "":
                    value = 0
                if value == "pull through":
                    value = 30
                if isinstance(value, str) and value.isdigit():
                    value = float(value)
        if key == "tent pad length":
            if value in ["", "na"]:
                value = 0
            value = str(value)
        if key == "air conditioning":
            if value in ["central", "room only"]:
                value = True
        if key == "site length":
            if isinstance(value, str):
                if value.strip() in ["", "n/a"]:
                    value = 0
                if isinstance(value, str) and " total site sf" in value:
                    site_width = [d for d in data if d[0] == "site width"]
                    if len(site_width) > 0:
                        site_width = site_width[0]
                    else:
                        site_width = 0.0
                    if isinstance(site_width, str) and site_width.isdigit():
                        value = value.replace(" total site sf", "").strip().replace(",", "")
                        if site_width > 0:
                            value =  float(value) / float(site_width)
                        else:
                            value =  math.sqrt(float(value))
                if isinstance(value, str):
                    value = value.replace("ft", "").replace("feet", "").replace("+", "").strip()
                if isinstance(value, str) and "(" in value:
                    value = value.split("(")[0].strip()
                if isinstance(value, str) and "/" in value:
                    value = value.split("/")[1].strip()
                if isinstance(value, str) and value.isdigit():
                    value = float(value)
                    if value < 0:
                        value = 0
        if key == "host" and value == "":
            value = False
        if key == "base number of people" and value == True:
            value = 1
        if key == "visitor center" and value == "":
            value = False
        if key == "type of site access":
            if value == False or value == "drive-up":
                value = "drive-in"
            elif value == "walk-in":
                value = "hike-in"
        if key == "parking area" and value == "":
            value = False
        if key == "concessions" and value == "":
            value = False
        if key == "num rooms":
            if value in ["none", "", "large tent", "small tent"]:
                value = 0
        if key == "max num of people":
            if isinstance(value, str):
                value = value.replace("adults", "").strip()
            if value == False or value == "" or value == 0:
                value = 6
            if isinstance(value, str) and value.isdigit():
                value = int(value)
        if key == "supplies" and value == "":
            value = False
        if key == "grills/fire ring" and value == "grills":
            value = True
        if key == "driveway length":
            if isinstance(value, str):
                if "ft" in value:
                    value = value.split("ft")[0].strip()
                if "feet" in value:
                    value = value.split("feet")[0].strip()
                if "x" in value:
                    value = value.split("x")[0].strip()
                if "&" in value:
                    value = value.split("&")[0].strip()
                if "+" in value:
                    value = value.split("+")[0].strip()
                if value.strip() == "":
                    value = 0
                if isinstance(value, str) and value.isdigit():
                    value = float(value)
                    if value < 0:
                        value = 0
        if key == "gift shop" and value == "":
            value = False
        if key == "min num of vehicles" and value in ["", "n/a"]:
            value = 0
        if key == "max num of horses" and value in ["", "n/a", "nan"]:
            value = 100
        if key == "tent pad width":
            if value in ["", "na"]:
                value = 0
            value = str(value)
        if key == "emergency phone" and value == "":
            value = False
        if key == "num of beds":
            if value in ["", "none"]:
                value = 0
        if key == "drinking water" and value == "":
            value = False
        if key == "site height":
            if isinstance(value, str) and "+" in value:
                value = value.replace("+", "").strip()
            if value in ["", "infinite"]:
                value = 100
            if isinstance(value, str) and value.isdigit():
                value = int(value)
        if key == "max num of vehicles":
            if value in ["", "n/a"]:
                value = 0
        if key == "hike in distance to site" and value == "":
            value = 0
        if key == "base number of vehicles" and value == True:
            value = 1
        if isinstance(value, int) and value < 0:
            value = 0
        if key in keys_to_remove_foot_quote and isinstance(value, str):
            value = value.replace("'", "")
            if isinstance(value, str) and value.isdigit():
                value = float(value)
        cleaned_data.append((key, value))
    return cleaned_data


def get_and_process_all_attributes_from_campsite(campsite):
    attributes_1 = {attr["AttributeName"].lower().replace("_", " ").strip(): process_attr_vals(attr["AttributeValue"]) for attr in campsite["ATTRIBUTES"]}
    attributes_2 = {k.lower().replace("_", " ").strip(): process_attr_vals(v) for k, v in campsite["campsite_info"].items() if k != "all_attributes"}
    attributes_3 = {k.lower().replace("_", " ").strip(): process_attr_vals(v) for k, v in campsite["campsite_info"]["all_attributes"].items()}
    attributes_4 = {(v["attribute_name"] if "attribute_name" in v else k).lower().replace("_", " ").strip(): process_attr_vals(v["attribute_value"]) for top_level_key in ["equipment_details_map", "site_details_map"] for k, v in campsite["notices"]["campsite"][top_level_key].items() if "attribute_value" in v}
    if campsite["notices"]["campsite"]["amenities"] is None:
        attributes_5 = dict()
    else:
        # try:
        attributes_5 = {(v["attribute_name"] if "attribute_name" in v else v["attribute_code"]).lower().replace("_", " ").strip(): process_attr_vals(v["attribute_value"]) for v in campsite["notices"]["campsite"]["amenities"] if "attribute_value" in v}        
        # except KeyError:
        #     print(campsite["notices"]["campsite"]["amenities"])
    if campsite["notices"]["campsite"]["attributes"] is None:
        attributes_6 = dict()
    else:
        attributes_6 = {attr["attribute_name"].lower().replace("_", " ").strip(): process_attr_vals(attr["attribute_value"]) for attr in campsite["notices"]["campsite"]["attributes"] if "attribute_value" in attr}
    cleaned_attributes = clean_data(list(attributes_1.items()) + list(attributes_2.items()) + list(attributes_3.items()) + list(attributes_4.items()) + list(attributes_5.items()) + list(attributes_6.items()))
    return sorted(list(set(cleaned_attributes)), key=lambda a:a[0])


def get_campground_dict(campground):
    campground_activities = get_campground_activities(campground["general_campground_info"])
    campground_amenities = get_campground_amenities(campground["general_campground_info"])
    cell_coverage_ratings = get_cell_coverage(campground["campground_ratings"].get("aggregate_cell_coverage_ratings", {}), agg_type="All")
    campground_rating = get_campground_ratings(campground["campground_ratings"])
    campground_notices_list = get_campground_notices(campground["general_campground_info"])
    campground_info = get_campground_info(campground["general_campground_info"])
    campground_reviews_list = get_campground_reviews(campground["campground_reviews"])
    campsites_list = get_campsites(campground["campsites"])
    campground_processed_dict = {
        "id": campground["campground_id"],
        "name": campground["campground_name"],
        "latitude": campground["campground_latitude"],
        "longitude": campground["campground_longitude"],
        "activities": campground_activities,
        "amenities": campground_amenities,
        "cell_coverage_rating": cell_coverage_ratings,
        "rating": campground_rating,
        "notices": campground_notices_list,
        "info": campground_info,
        "reviews": campground_reviews_list,
        "campsites": campsites_list
    }
    return campground_processed_dict


def process_raw_pulled_jsonl(jsonl_file):
    with open(jsonl_file, "r") as f:
        return [get_campground_dict(json.loads(line.strip())) for line in f]
            

# for campground in all_campgrounds:
#     calculate_token_count()


if __name__ == "__main__":
    jsonl_file = sys.argv[1]
    out_jsonl = sys.argv[2]
    camp_id_maps_filename = sys.argv[3]
    campsite_to_campground_id_map = {}
    campground_to_campsite_id_map = defaultdict(list)
    all_campgrounds = process_raw_pulled_jsonl(jsonl_file)
    for campground in all_campgrounds:
        for campsite in campground["campsites"]:
            campsite_to_campground_id_map[campsite["campsite_id"]] = campground["id"]
            campground_to_campsite_id_map[campground["id"]].append(campsite["campsite_id"])
    camp_id_maps = {"campsite_to_campground_id_map": campsite_to_campground_id_map,
                    "campground_to_campsite_id_map": campground_to_campsite_id_map}
    with open(out_jsonl, "w") as f:
        f.write("\n".join([json.dumps(c) for c in all_campgrounds]))
    with open(camp_id_maps_filename, "w") as f:
        f.write(json.dumps(camp_id_maps))




# make readme and make it github
# speed up the pull


# check if the llm works to get info (how to format, structured out)
# add in the dynamic grabbing of info about the stuff nearby
# look at camply and figure out how it works
# host it so I can provide list of campsites or campground and date and get a list of ones available on that date
# OR
# give a date and an email and a set of campgrounds/sites and message them when one is open
# get to the point where we have an api that 
#     1. gives a set of campsites or campground (based on a bunch of filter inputs and text with model, etc)
#     2. the ability to see only available or both and select to be notified







# pip install -q -U google-generativeai








# import google.generativeai as genai
# import os
# import markdown
# import PIL.Image

# genai.configure(api_key=os.environ["GOOGLE_AI_API_KEY"])

# model=genai.GenerativeModel(
#   model_name="gemini-1.5-flash-exp-0827",
#   system_instruction="You are a cat. Your name is Neko.")


# #gemini-1.5-flash-exp-0827
# #gemini-1.5-pro-exp-0827
# #gemini-1.5-pro-002
# #gemini-1.5-flash-002

# # LOAD FILES

# sample_file = PIL.Image.open(media / "organ.jpg")

# sample_file = genai.upload_file(path="gemini.pdf",
#                                 display_name="Gemini 1.5 PDF")

# print(f"Uploaded file '{sample_file.display_name}' as: {sample_file.uri}")

# import time

# # Check whether the file is ready to be used.
# while sample_file.state.name == "PROCESSING":
#     print('.', end='')
#     time.sleep(10)
#     file = genai.get_file(sample_file.name)
#     print(f"Retrieved file '{file.display_name}' as: {sample_file.uri}")

# if sample_file.state.name == "FAILED":
#   raise ValueError(sample_file.state.name)


# # RUN EVAL

# response = model.generate_content(
#     ["Tell me about this instrument", sample_file],
#     generation_config=genai.types.GenerationConfig(
#         # Only one candidate for now.
#         candidate_count=1,
#         max_output_tokens=1000,
#         temperature=1.0,
#     ),
# )


# import enum
# from typing_extensions import TypedDict

# class Grade(enum.Enum):
#     A_PLUS = "a+"
#     A = "a"
#     B = "b"
#     C = "c"
#     D = "d"
#     F = "f"

# class Recipe(TypedDict):
#     recipe_name: str
#     grade: Grade
    
# generation_config={"response_mime_type": "application/json",
#                    "response_schema": list[Recipe]}

# generation_config=genai.GenerationConfig(
#         response_mime_type="text/x.enum",
#         response_schema={
#             "type": "STRING",
#             "enum": ["Percussion", "String", "Woodwind", "Brass", "Keyboard"],
#         },

# markdown.markdown(response.text)




