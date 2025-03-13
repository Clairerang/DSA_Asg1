import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculates the great-circle distance (Haversine formula)."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of Earth in kilometers.
    return c * r

def calculate_price(distance, price_per_km):
    """Calculates the price based on distance and price per kilometer."""
    return round(distance * price_per_km, 2)

def get_price_for_route(origin, destination, price_per_km = 0.25):
    """Calculates the price for a route using the AirportDatabase."""

    try:
        distance = calculate_distance(
            float(origin.latitude), float(origin.longitude),
            float(destination.latitude), float(destination.longitude)
        )
        price = calculate_price(distance, price_per_km)
        return price
    except ValueError as e:
        print(f"Error processing route: {e}")
        return None
