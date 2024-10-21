# CampFinder


### export aws key

docker build -t camp-finder-api .

docker run -p 8000:5000 -e AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} -e AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} -e AWS_DEFAULT_REGION=us-east-1 camp-finder-api gunicorn -w "1" --timeout 300 -b 0.0.0.0:5000 app:app


curl -X GET http://localhost:8000/health

curl -X POST http://127.0.0.1:8000/filter-campgrounds -H "Content-Type: application/json" -d '{
      "availability": {
        "start_window_date": "2024-11-07", 
        "end_window_date": "2024-11-11", 
        "num_nights": 2, 
        "days_of_the_week": [4, 5]
      },
      "filters": {
        "AND": [
          {"rating.average_rating": {"gt": 3.5}},
          {"rating.number_of_ratings": {"gt": 200}},
          {"location": {"within_radius": {"center": [37.759244, -122.451855], "radius": 170}}}
        ]
      },
      "sort": {
        "key": "rating.average_rating",
        "reverse": true
      }
    }'