
def format_campground_data_to_llm_input_string(campgrounds):
    formatted_data = []
    for campground in campgrounds:
        campground_name = campground.get("name", "Unknown Campground")
        activities = ", ".join(campground.get("activities", []))
        amenities = ", ".join(campground.get("amenities", []))
        # Ratings
        rating_info = campground.get("rating", {})
        average_rating = rating_info.get("average_rating", "N/A")
        number_of_ratings = rating_info.get("number_of_ratings", 0)
        # Cell coverage rating
        cell_coverage = campground.get("cell_coverage_rating", {})
        cell_coverage_rating = cell_coverage.get("average_rating", "N/A")
        cell_coverage_reviews = cell_coverage.get("number_of_ratings", 0)
        # Notices
        notices = " ".join(campground.get("notices", []))
        # Campsites Information
        campsites = campground.get("campsites", [])
        campground_info = campground.get("info", "None")
        campsite_info = []
        for campsite in campsites:
            site_id = campsite.get("campsite_id", "N/A")
            name = campsite.get("name", "Unnamed Site")
            reservable = "Yes" if campsite.get("reservable") else "No"
            accessible = "Yes" if campsite.get("accessible") else "No"
            campsite_notices = " ".join(campsite.get("notices", []))
            attributes = ", ".join([f"{key}: {val}" for key, val in campsite.get("attributes", [])])
            campsite_info.append(f"Campsite {name} (ID: {site_id}) - Reservable: {reservable}, Accessible: {accessible}. Notices: {campsite_notices} Attributes: {attributes}")
        campsite_str = "\n".join(campsite_info)
        # Reviews
        reviews = campground.get("reviews", [])
        review_info = []
        for review in reviews:
            review_rating = review.get("rating", "N/A")
            review_text = review.get("review", "").replace('\n', ' ')
            upvote_score = review.get("upvote_score", 0)
            campsite_name = review.get("campsite_name", "Unknown")
            review_info.append(f"Rating: {review_rating} Upvotes: {upvote_score}, Campsite: {campsite_name} - {review_text}")
        review_str = "\n".join(review_info)
        # Final formatted entry
        formatted_entry = (
            f"Campground: {campground_name}\n"
            f"{campground_info}"
            f"Activities: {activities}\n"
            f"Amenities: {amenities}\n"
            f"Rating: {average_rating} from {number_of_ratings} reviews\n"
            f"Cell Coverage Rating: {cell_coverage_rating} from {cell_coverage_reviews} reviews\n"
            f"Notices: {notices}"
            f"Reviews:\n{review_str}"
            f"\n\nCampsites:\n{campsite_str}\n\n"
        )
        formatted_data.append(formatted_entry)
    return "\n\n".join(formatted_data)