from flask import Flask, request, jsonify
from camp_finder.filter.campground_selector import CampgroundData
from datetime import datetime
import json
from camp_finder.utils.s3_utils import download_s3_file
from pathlib import Path
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Path to your campground data file (replace with the actual file path)
S3_KEY = "all_campground_info/recgov_all_converted_100824.jsonl"
jsonl_file = Path.home()/"recgov_all_converted_100824.jsonl"
download_s3_file(S3_KEY, jsonl_file)
campground_data = CampgroundData(jsonl_file)
print("Finished download and data loading")

def custom_serializer(obj):
    """Helper function for serializing datetime objects to JSON."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")


@app.route("/filter-campgrounds", methods=["POST"])
def filter_campgrounds():
    """
    Endpoint to filter and sort campgrounds based on a filter_sort_dict provided in JSON.
    """
    try:
        # Parse the JSON request
        filter_sort_dict = request.get_json()
        print("Received the following filter sort json:")
        print(filter_sort_dict)
        if not filter_sort_dict:
            return jsonify({"error": "Invalid or missing JSON data"}), 400

        # Call the filter_and_sort_campgrounds method to get the filtered and sorted campgrounds
        results = campground_data.filter_and_sort_campgrounds(filter_sort_dict)

        # Return the results as JSON
        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint to ensure the API is running.
    """
    return jsonify({"status": "healthy"}), 200


@app.route("/campground/<string:campground_id>", methods=["GET"])
def get_campground_by_id(campground_id):
    """
    Endpoint to retrieve a campground by its ID.
    """
    try:
        # Find the campground by ID
        campground = next((campground for campground in campground_data.campgrounds if campground['id'] == campground_id), None)

        if not campground:
            return jsonify({"error": "Campground not found"}), 404

        # Return the campground data as JSON
        return jsonify(campground), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 error handler."""
    return jsonify({"error": "Endpoint not found"}), 404


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
