import requests
import os

from dotenv import load_dotenv
load_dotenv()  # take environment variables


url = "https://api.traveltimeapp.com/v4/routes"
headers = {
    "Content-Type": "application/json",
    "X-Application-Id": os.getenv("Application-Id"),
    "X-Api-Key": os.getenv("Api-Key")
}
data = {
    "locations": [
        {
            "id": "luz_station",
            "coords": {
                "lng": -46.635393,
                "lat": -23.5351223
            }
        },
        {
            "id": "berrine_street",
            "coords": {
                "lng": -46.6936505,
                "lat": -23.6046125
            }
        }
    ],
    "departure_searches": [
        {
            "id": "departure search example",
            "departure_location_id": "luz_station",
            "arrival_location_ids": [
                "berrine_street"
            ],
            "departure_time": "2025-04-12T01:00:00Z",
            "properties": ["route"], # ["travel_time", "distance", "route"]
            "transportation": {
                "type": "public_transport"
            }
        }
    ]
}

response = requests.post(url, headers=headers, json=data, verify=False)
print(response.json())
