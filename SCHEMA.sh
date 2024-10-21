
{
  "filters": {
    "AND": [
      { "rating.average_rating": { "gt": 4.0 } },
      { "campsites.attributes.accessible": { "eq": true } },
      { "location": { "within_radius": { "center": [34.0522, -118.2437], "radius": 50 } } }
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


