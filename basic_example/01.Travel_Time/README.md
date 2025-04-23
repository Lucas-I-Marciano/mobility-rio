Example of Response JSON

```json
{
  "results": [
    {
      "search_id": "departure-search",
      "locations": [
        {
          "id": "point-to-1",
          "properties": [
            {
              "travel_time": 540,
              "route": {
                "departure_time": "2025-04-22T09:11:53+01:00",
                "arrival_time": "2025-04-22T09:20:53+01:00",
                "parts": [
                  {
                    "id": 0,
                    "type": "start_end",
                    "mode": "walk",
                    "directions": "Start your journey 37 meters southwest",
                    "distance": 37,
                    "travel_time": 26,
                    "coords": [
                      {
                        "lat": 51.5074975, <-- This is a point that connect with a straigth line with the other coord
                        "lng": -0.1236888
                      },
                      {
                        "lat": 51.507179299999926, <-- This one
                        "lng": -0.12387180000000649
                      }
                    ],
                    "direction": "southwest"
                  },
                  {
                    "id": 1,
                    "type": "road",
                    "mode": "walk",
                    "directions": "Walk 88 meters",
                    "distance": 88,
                    "travel_time": 63,
                    "coords": [
                      {
                        "lat": 51.507179299999926, <-- This is the same point of last point of last id
                        "lng": -0.12387180000000649
                      },
                      {
                        "lat": 51.50707819999999,
                        "lng": -0.12400540000000555
                      },
                      {
                        "lat": 51.507507099999934,
                        "lng": -0.12483000000001435
                      }
                    ]
                  },

```

### Route

POST https://api.traveltimeapp.com/v4/routes

### BODY

```json
{
  "locations": [
    {
      "id": "Home",
      "coords": {
        "lat": 51.581589,
        "lng": -0.0775871
      }
    },
    {
      "id": "Office",
      "coords": {
        "lat": 51.511933,
        "lng": -0.1277888
      }
    }
  ],
  "arrival_searches": [
    {
      "id": "Morning Commute",
      "arrival_location_id": "Office",
      "departure_location_ids": ["Home"],
      "arrival_time": "2021-09-28T09:00:00Z",
      "properties": ["route"],
      "transportation": {
        "type": "driving"
      }
    }
  ]
}
```

### CURL

```json

curl -X POST https://api.traveltimeapp.com/v4/routes \
-H 'Content-Type: application/json' \
-H 'X-Application-Id: 4dc4086a' \
-H 'X-Api-Key: 9e684f497b057a30d592275cfba5de74' \
-d '{
  "locations": [
    {
      "id": "Home",
      "coords": {
        "lat": 51.5815890,
        "lng": -0.0775871
      }
    },
    {
      "id": "Office",
      "coords": {
        "lat": 51.511933,
        "lng": -0.1277888
      }
    }
  ],
  "arrival_searches": [
    {
      "id": "Morning Commute",
      "arrival_location_id": "Office",
      "departure_location_ids": [
        "Home"
      ],
      "arrival_time": "2021-09-28T09:00:00Z",
      "properties": ["route"],
      "transportation": {
        "type": "driving"
      }
    }
  ]
}'
```
