from enum import Enum

class TravelMode(str, Enum):
    BUS = "bus" # Default
    CYCLING = "cycling"
    DRIVING = "driving"
    DRIVING_TRAIN = "driving+train"
    PUBLIC_TRANSPORT = "public_transport" 
    WALKING = "walking"
    TRAIN = "train"
    FERRY = "ferry"
    DRIVING_FERRY = "driving+ferry"
    CYCLING_FERRY = "cycling+ferry"