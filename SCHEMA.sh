

{
  "availability": {
  	"start_window_date": 2024-12-01 #string YYYY-MM-DD,
  	"end_window_date": 2024-12-30 #string YYYY-MM-DD,
  	"num_nights": 2, #int
  	"days_of_the_week": [4, 5] # list[int] [0,1,2,3,4,5,6] Monday is 0 and Sunday is 6
  	}
  "filters": {
    "weather": {"min_temp": {"gt": 40.0}, "rain_amount_mm": {"lt": 1.0 }, "humidity": {"between": [20, 70]}, "max_temp": {"between": [60, 90]} },
    "location": { "center": [34.0522, -118.2437], "radius": 50 } },
    "AND": [
      { "rating.average_rating": { "gt": 4.0 } },
      { "campsites.accessible": { "eq": true } },
      { "rating.number_of_ratings": { "between": (10, 50) } },
      { "amenities": {"contains": [""]}},
      { "activities": {"contains_any": [""]}},
      { "campsites.attributes": {"contains": {"driveway length": { "gt": 20 } } } },
      { "campsites.attributes": {"contains": {"campfire allowed": { "eq": true } } } },
      { "campsites.attributes": {"contains": "campfire allowed" } },
    ],
    "OR": [
      { "rating.average_rating": { "lt": 2.0 } },
      { "campsites.accessible": { "eq": true } }
    ]
  },
  "sort": {
    "key": "rating.average_rating",
    "reverse": true
  }
}

python3.9 convert_and_process_raw_data.py /Users/deaxman/Downloads/all_data_backup2_GOOD_3784.jsonl /Users/deaxman/Downloads/recgov_converted_campgrounds_3784.jsonl



/Users/deaxman/Downloads/recgov_converted_campgrounds.jsonl


{
  "filters": {
    "AND": [
      {
        "<field_name>": {
          "<operator>": "<value>"
        }
      }
    ],
    "OR": [
      {
        "<field_name>": {
          "<operator>": "<value>"
        }
      }
    ]
  },
  "sort": {
    "key": "<field_name>",
    "reverse": "<boolean>"
  }
}





{
  "id": "string",                    # Unique identifier for the campground
  "name": "string",                  # Name of the campground
  "latitude": float,                 # Latitude of the campground location
  "longitude": float,                # Longitude of the campground location
  "activities": [                    # List of activities available at the campground
    "string"
  ],
  "amenities": [                     # List of amenities available at the campground
    "string"
  ],
  "cell_coverage_rating": {           # Information on cell coverage ratings
    "average_rating": float,          # Average cell coverage rating
    "number_of_ratings": int,         # Number of ratings for cell coverage
    "star_counts": {                  # Breakdown of ratings by stars
      "0": int,
      "1": int,
      "2": int,
      "3": int,
      "4": int
    }
  },
  "rating": {                         # General campground rating information
    "average_rating": float,          # Average rating
    "number_of_ratings": int,         # Number of ratings
    "star_counts": {                  # Breakdown of ratings by stars
      "1": int,
      "2": int,
      "3": int,
      "4": int,
      "5": int
    }
  },
  "notices": [                        # List of notices relevant to campers
    "string"
  ],
  "info": "string",                   # Detailed information about the campground facilities, natural features, recreation, etc.
  "reviews": [                        # List of reviews for the campground
    {
      "created_at": "string",         # Timestamp when the review was created (ISO 8601 format)
      "upvote_score": int,            # Score of upvotes for the review
      "rating": int,                  # Rating given in the review
      "review": "string",             # The content of the review
      "campsite_id": "string",        # ID of the campsite being reviewed
      "campsite_name": "string",      # Name/number of the campsite being reviewed
      "campsite_reserved_date": "string" # Date when the campsite was reserved (ISO 8601 format)
    }
  ],
  "campsites": [                      # List of campsites available at the campground
    {
      "campsite_id": "string",        # Unique identifier for the campsite
      "accessible": bool,             # Whether the campsite is accessible
      "latitude": float,              # Latitude of the campsite
      "longitude": float,             # Longitude of the campsite
      "name": "string",               # Name/number of the campsite
      "available": [ # list of booking periods matching specifications
        ["string"] # list of isodate strings that specifies this booking period
      ],
      "weathers": [ # list of weather for each available booking period (this list will be same length as campground["available"]
        {"min_temp": float,
         "max_temp": float,
         "cloud_cover": float,
         "rain_amount_mm": float,
         "humidity": float
        }
      ],
      "reservable": bool,             # Whether the campsite is reservable
      "notices": [                    # List of notices specific to the campsite
        "string"
      ],
      "attributes": [                 # Attributes of the campsite
        [
          "string",                   # Name of the attribute
          bool or string or int       # Value of the attribute
        ]
      ]
    }
  ]
}


{
    #                     "min_temp": day['temp']['min'],
    #                     "max_temp": day['temp']['max'],
    #                     "cloud_cover": day['clouds'],
    #                     "rain_amount_mm": day.get('rain', 0),
    #                     "humidity": day["humidity"]
    #                 }


{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Campground Query Schema",
  "type": "object",
  "properties": {
    "availability": {
      "$ref": "#/definitions/availability"
    },
    "filters": {
      "type": "object",
      "properties": {
        "weather": {
          "$ref": "#/definitions/weatherCondition"
        },
        "AND": {
          "type": "array",
          "items": { "$ref": "#/definitions/condition" }
        },
        "OR": {
          "type": "array",
          "items": { "$ref": "#/definitions/condition" }
        },
        "location": {
          "$ref": "#/definitions/locationCondition"
        }
      },
      "patternProperties": {
        "^(?!weather$|AND$|OR$|location$).+$": {
          "$ref": "#/definitions/condition"
        }
      },
      "additionalProperties": false
    },
    "sort": {
      "type": "object",
      "properties": {
        "key": {
          "type": "string",
          "enum": [
            "rating.average_rating",
            "rating.number_of_ratings",
            "cell_coverage_rating.average_rating",
            "cell_coverage_rating.number_of_ratings",
            "campsites.accessible",
            "amenities",
            "activities",
            "campsites.attributes",
            "location"
          ]
        },
        "reverse": { "type": "boolean" }
      },
      "required": ["key"],
      "additionalProperties": false
    }
  },
  "required": ["filters", "sort"],
  "additionalProperties": false,
  "definitions": {
    "availability": {
      "type": "object",
      "properties": {
        "start_window_date": { "type": "string", "format": "date" },
        "end_window_date": { "type": "string", "format": "date" },
        "num_nights": { "type": "integer", "minimum": 1 },
        "days_of_the_week": {
          "type": "array",
          "items": {
            "type": "integer",
            "minimum": 0,
            "maximum": 6
          }
        }
      },
      "required": ["start_window_date", "end_window_date", "num_nights", "days_of_the_week"],
      "additionalProperties": false
    },
    "condition": {
      "type": "object",
      "additionalProperties": false,
      "minProperties": 1,
      "maxProperties": 1,
      "patternProperties": {
        "^(rating\\.average_rating|rating\\.number_of_ratings|cell_coverage_rating\\.average_rating|cell_coverage_rating\\.number_of_ratings)$": {
          "$ref": "#/definitions/numericComparisonOperators"
        },
        "^campsites\\.accessible$": {
          "$ref": "#/definitions/booleanEqOperator"
        },
        "^(amenities|activities)$": {
          "$ref": "#/definitions/containsOperatorsNonCampsite"
        },
        "^campsites\\.attributes$": {
          "$ref": "#/definitions/campsiteAttributesCondition"
        }
      }
    },
    "numericComparisonOperators": {
      "type": "object",
      "properties": {
        "gt": { "type": "number" },
        "ge": { "type": "number" },
        "lt": { "type": "number" },
        "le": { "type": "number" },
        "eq": { "type": "number" },
        "between": {
          "type": "array",
          "items": { "type": "number" },
          "minItems": 2,
          "maxItems": 2
        }
      },
      "additionalProperties": false,
      "minProperties": 1,
      "maxProperties": 1
    },
    "booleanEqOperator": {
      "type": "object",
      "properties": {
        "eq": { "type": "boolean" }
      },
      "additionalProperties": false,
      "required": ["eq"]
    },
    "containsOperatorsNonCampsite": {
      "type": "object",
      "properties": {
        "contains": {
          "type": "array",
          "items": { "type": "string" }
        },
        "contains_any": {
          "type": "array",
          "items": { "type": "string" }
        }
      },
      "additionalProperties": false,
      "minProperties": 1,
      "maxProperties": 1
    },
    "campsiteAttributesCondition": {
      "type": "object",
      "properties": {
        "contains": {
          "oneOf": [
            { "type": "string" },
            {
              "type": "object",
              "additionalProperties": {
                "oneOf": [
                  { "type": "boolean" },
                  {
                    "type": "object",
                    "properties": {
                      "gt": { "type": "number" },
                      "ge": { "type": "number" },
                      "lt": { "type": "number" },
                      "le": { "type": "number" },
                      "eq": { "type": ["number", "string", "boolean"] },
                      "between": {
                        "type": "array",
                        "items": { "type": "number" },
                        "minItems": 2,
                        "maxItems": 2
                      }
                    },
                    "additionalProperties": false,
                    "minProperties": 1,
                    "maxProperties": 1
                  }
                ]
              }
            }
          ]
        }
      },
      "additionalProperties": false,
      "required": ["contains"]
    },
    "locationCondition": {
      "type": "object",
      "properties": {
        "center": {
          "type": "array",
          "items": { "type": "number" },
          "minItems": 2,
          "maxItems": 2
        },
        "radius": { "type": "number" }
      },
      "required": ["center", "radius"],
      "additionalProperties": false
    },
    "weatherCondition": {
      "type": "object",
      "properties": {
        "min_temp": { "$ref": "#/definitions/numericComparisonOperators" },
        "max_temp": { "$ref": "#/definitions/numericComparisonOperators" },
        "rain_amount_mm": { "$ref": "#/definitions/numericComparisonOperators" },
        "humidity": { "$ref": "#/definitions/numericComparisonOperators" }
      },
      "additionalProperties": false
    }
  }
}
python
Copy code
import google.generativeai as genai
from typing import TypedDict, Union, List, Dict, Literal

# Define the lists of possible values
campsite_attrs = [
    "campfire allowed",
    "capacity rating",
    "checkin time",
    "checkout time",
    "drinking water",
    "driveway entry",
    "driveway grade",
    "driveway length",
    "driveway surface",
    "fire pit",
    "first aid kit"
    # Add any additional campsite attributes here
]

activities_list = [
    "accessible swimming",
    "amphitheater",
    "antiquing",
    "archery",
    "auto touring",
    "backpacking"
    # Add any additional activities here
]

amenities_list = [
    "accessible boat dock",
    "amphitheater",
    "appalachian clubhouse",
    "archeological sites",
    "archery",
    "atm",
    "atv area"
    # Add any additional amenities here
]

# Define NumericCondition
class NumericCondition(TypedDict, total=False):
    gt: float
    ge: float
    lt: float
    le: float
    eq: float
    between: List[float]

# Define BooleanCondition
class BooleanCondition(TypedDict):
    eq: bool

# Define StringEqualityCondition
class StringEqualityCondition(TypedDict):
    eq: str

# Define CampsiteAttributeConditionValue
CampsiteAttributeConditionValue = Union[
    bool,
    NumericCondition,
    StringEqualityCondition
]

# Define CampsiteAttributesCondition
class CampsiteAttributesCondition(TypedDict):
    contains: Union[
        Literal[tuple(campsite_attrs)],
        Dict[Literal[tuple(campsite_attrs)], CampsiteAttributeConditionValue]
    ]

# Define ListCondition for amenities and activities
class ListCondition(TypedDict, total=False):
    contains: List[Literal[tuple(amenities_list + activities_list)]]
    contains_any: List[Literal[tuple(amenities_list + activities_list)]]

# Define LocationCondition
class LocationCondition(TypedDict):
    center: List[float]  # [latitude, longitude]
    radius: float        # Radius in kilometers

# Define Condition
class Condition(TypedDict, total=False):
    rating_average_rating: NumericCondition
    rating_number_of_ratings: NumericCondition
    cell_coverage_rating_average_rating: NumericCondition
    cell_coverage_rating_number_of_ratings: NumericCondition
    campsites_accessible: BooleanCondition
    amenities: ListCondition
    activities: ListCondition
    campsites_attributes: CampsiteAttributesCondition

# Define Filters
class Filters(TypedDict, total=False):
    weather: Dict[str, NumericCondition]
    AND: List[Condition]
    OR: List[Condition]
    location: LocationCondition
    # Additional conditions can be included directly
    rating_average_rating: NumericCondition
    rating_number_of_ratings: NumericCondition
    cell_coverage_rating_average_rating: NumericCondition
    cell_coverage_rating_number_of_ratings: NumericCondition
    campsites_accessible: BooleanCondition
    amenities: ListCondition
    activities: ListCondition
    campsites_attributes: CampsiteAttributesCondition

# Define Availability
class Availability(TypedDict):
    start_window_date: str  # YYYY-MM-DD
    end_window_date: str    # YYYY-MM-DD
    num_nights: int
    days_of_the_week: List[int]  # 0 (Monday) to 6 (Sunday)

# Define Sort
class Sort(TypedDict):
    key: str
    reverse: bool

# Define the overall QuerySchema
class QuerySchema(TypedDict, total=False):
    availability: Availability
    filters: Filters
    sort: Sort

# Now, configure the model to use this schema
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# Set up the generation config with the response schema
generation_config = genai.GenerationConfig(
    response_mime_type="application/json",
    response_schema=QuerySchema
)

# Example prompt
prompt = "Create a query to find campgrounds with specific conditions and sorting."

# Generate the content
result = model.generate_content(
    prompt,
    generation_config=generation_config
)

print(result)