from math import radians, cos, sin, asin, sqrt

def haversine(origin_lng, origin_lat, dest_lng, dest_lat):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    origin_lng, origin_lat, dest_lng, dest_lat = map(radians, [origin_lng, origin_lat, dest_lng, dest_lat])

    # haversine formula 
    dlon = dest_lng - origin_lng 
    dlat = dest_lat - origin_lat 
    a = sin(dlat/2)**2 + cos(origin_lat) * cos(dest_lat) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r