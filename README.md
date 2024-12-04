# CampFinder


### export aws key

docker build -t camp-finder .

docker run -p 8000:5000 -v ~/.aws:/root/.aws camp-finder gunicorn -w "1" --timeout 300 -b 0.0.0.0:5000 app:app


curl -X GET http://localhost:8000/health

curl -X POST http://127.0.0.1:8000/filter-campgrounds -H "Content-Type: application/json" -d '{
    "availability": {
        "start_window_date": "2024-12-03",
        "end_window_date": "2024-12-30",
        "num_nights": 2,
        "days_of_the_week": [4, 5]
    },
    "location": {
        "center": [37.764116, -122.455423],
        "radius": 100
    },
    "filters": {
        "weather": {
            "min_temp": {"gt": 30.0},
            "rain_amount_mm": {"lt": 3.0},
            "humidity": {"between": [0, 90]},
            "max_temp": {"between": [60, 90]}
        },
        "AND": [
            {"rating.average_rating": {"gt": 4.0}},
            {"rating.number_of_ratings": {"gt": 10}}
        ],
        "OR": []
    },
    "sort": {
        "key": "rating.average_rating",
        "reverse": true
    }
}'



aws ecr create-repository --repository-name camp-finder --region us-east-1

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 198449958201.dkr.ecr.us-east-1.amazonaws.com

docker tag camp-finder:latest 198449958201.dkr.ecr.us-east-1.amazonaws.com/camp-finder:latest



aws cloudformation create-stack --stack-name fargate-campfinder-api --template-body file://spin_up_api.yaml --parameters ParameterKey=ImageTag,ParameterValue=latest ParameterKey=CampFinderAPIKey,ParameterValue=camp_finder_api_secret_key --capabilities CAPABILITY_IAM


REGION=us-east-1

curl -X GET "https://{API_ID}.execute-api.{REGION}.amazonaws.com/prod/health" \
-H "x-api-key: camp_finder_api_secret_key"


curl -X POST "https://{API_ID}.execute-api.{REGION}.amazonaws.com/prod/filter-campgrounds" \
-H "x-api-key: camp_finder_api_secret_key" \
-H "Content-Type: application/json" \
-d '{
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





# Create website

npm install @mui/material @emotion/react @emotion/styled
npm install axios
npm install @mui/icons-material

npx create-react-app campground-finder-website
cd campground-finder-website
src/App.js
src/App.css
src/Campground.js
src/CampgroundList.js

npm start

http://localhost:3000






npm run build

aws s3api create-bucket --bucket campground-finder-website --region us-east-1 --create-bucket-configuration LocationConstraint=us-east-1
aws s3 website s3://campground-finder-website/ --index-document index.html --error-document 404.html

aws s3 sync ./build/ s3://campground-finder-website/

cat <<EOL > bucket-policy.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::campground-finder-website/*"
    }
  ]
}
EOL



aws s3api put-bucket-policy --bucket campground-finder-website --policy file://bucket-policy.json




http://campground-finder-website.s3-website-us-east-1.amazonaws.com









