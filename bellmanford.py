import json
import math

def calculate_distance(lat1_rad, lon1_rad, lat2_rad, lon2_rad):
    """
    Calculates the distance between two points on Earth using the Haversine formula.

    Args:
        lat1_rad: Latitude of the first point in radians.
        lon1_rad: Longitude of the first point in radians.
        lat2_rad: Latitude of the second point in radians.
        lon2_rad: Longitude of the second point in radians.

    Returns:
        The distance between the two points in kilometers.
    """
    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    r = 6371
    return c * r

def calculate_price(distance, price_per_km):
    """Calculates price."""
    return distance * price_per_km

def load_airport_data(filepath):
    """Loads airport data, converts lat/lon to radians."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for airport_code, airport_info in data.items():
                if ("latitude" in airport_info and airport_info["latitude"] is not None and airport_info["latitude"] != "" and
                    "longitude" in airport_info and airport_info["longitude"] is not None and airport_info["longitude"] != ""):
                    try:
                        lat_deg = float(airport_info["latitude"])
                        lon_deg = float(airport_info["longitude"])
                        airport_info["latitude_rad"] = math.radians(lat_deg)
                        airport_info["longitude_rad"] = math.radians(lon_deg)
                    except ValueError:
                        print(f"Warning: Invalid lat/lon for {airport_code}.")
                        airport_info["latitude_rad"] = 0.0
                        airport_info["longitude_rad"] = 0.0
                else:
                    print(f"Warning: Missing or empty lat/lon for {airport_code}.")
                    airport_info["latitude_rad"] = 0.0
                    airport_info["longitude_rad"] = 0.0
            return data
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        print(f"Error loading data: {e}")
        return None

def get_airport_code(prompt):
    """Gets a valid IATA code."""
    while True:
        code = input(prompt).strip().upper()
        if len(code) == 3 and code.isalpha():
            return code
        else:
            print("Invalid IATA code. Please enter a 3-letter code.")

def get_price_for_route(origin_iata, destination_iata, airport_data, price_per_km):
    """
    Calculates the price and distance for a given route (without discounts).

    Args:
        origin_iata: The IATA code of the origin airport.
        destination_iata: The IATA code of the destination airport.
        airport_data: The dictionary containing airport data.
        price_per_km: The price per kilometer.

    Returns:
        A tuple containing:
            - The calculated price (float) or None if the route is invalid.
            - The calculated distance (float) or None if the route is invalid.
    """

    if origin_iata not in airport_data or destination_iata not in airport_data:
        return None, None
    try:
        # Use pre-calculated radian values
        origin_lat_rad = airport_data[origin_iata]["latitude_rad"]
        origin_lon_rad = airport_data[origin_iata]["longitude_rad"]
        dest_lat_rad = airport_data[destination_iata]["latitude_rad"]
        dest_lon_rad = airport_data[destination_iata]["longitude_rad"]
        distance = calculate_distance(origin_lat_rad, origin_lon_rad, dest_lat_rad, dest_lon_rad)
        price = calculate_price(distance, price_per_km)
        return price, distance
    except (KeyError, ValueError, Exception) as e:
        print(f"Error processing route: {e}")
        return None, None

def get_price_for_route_bellman_ford(origin_iata, destination_iata, airport_data, price_per_km, discount_routes):
    """
    Calculates the price and distance for a given route, applying discounts
    using logic similar to Bellman-Ford (for handling one-way/two-way discounts).

    Args:
        origin_iata: IATA code of the origin airport.
        destination_iata: IATA code of the destination airport.
        airport_data: Dictionary containing airport data.
        price_per_km: Price per kilometer.
        discount_routes: Dictionary of discount rules.  Keys are tuples:
                        (origin_iata, destination_iata). Values are tuples:
                        (discount_percentage, is_two_way_discount).

    Returns:
        A tuple: (final_price, distance).  Returns (None, None) on error.
    """

    if origin_iata not in airport_data or destination_iata not in airport_data:
        return None, None
    try:
        origin_lat_rad = airport_data[origin_iata]["latitude_rad"]
        origin_lon_rad = airport_data[origin_iata]["longitude_rad"]
        dest_lat_rad = airport_data[destination_iata]["latitude_rad"]
        dest_lon_rad = airport_data[destination_iata]["longitude_rad"]

        distance = calculate_distance(origin_lat_rad, origin_lon_rad, dest_lat_rad, dest_lon_rad)
        base_price = calculate_price(distance, price_per_km)

        # Apply discounts if applicable
        if (origin_iata, destination_iata) in discount_routes:
            discount_percentage, is_two_way = discount_routes[(origin_iata, destination_iata)]
            final_price = base_price * (1 - discount_percentage)
        elif (destination_iata, origin_iata) in discount_routes:
            discount_percentage, is_two_way = discount_routes[(destination_iata, origin_iata)]
            if is_two_way:
                final_price = base_price * (1 - discount_percentage)
            else:
                final_price = base_price
        else:
            final_price = base_price
        return final_price, distance
    
    except (KeyError, ValueError, Exception) as e:
        print(f"Error processing route: {e}")
        return None, None

def bellman_ford(graph, start, end, airport_data, discount_routes):
    """
    Finds the shortest path (lowest price) between two airports using the
    Bellman-Ford algorithm, handling potential discounts.

    Args:
        graph:  An adjacency list representing the flight network, where keys are
                airport IATA codes and values are dictionaries of neighboring
                airports with associated costs.
        start: The IATA code of the starting airport.
        end: The IATA code of the destination airport.
        airport_data: The dictionary containing airport data.
        discount_routes: A dictionary mapping (origin, destination) IATA pairs
                        to (discount_percentage, is_two_way) tuples.

    Returns:
        A tuple containing:
        - The total cost of the shortest path (float), or None if no path
            exists or a negative-weight cycle is detected.
        - A list of airport IATA codes representing the shortest path,
            or None if no path exists or a negative-weight cycle is detected.
        - The total *distance* of the shortest path (float), or None if no
            path exists or a negative-weight cycle is detected.  This is
            the *actual* distance traveled, *not* a cost.
    """

    distances = {node: float('inf') for node in graph}
    predecessors = {node: None for node in graph}
    distances[start] = 0

    for _ in range(len(graph) - 1):
        changed = False
        for u in graph:
            for v, data in graph[u].items():
                if "cost" in data:
                    cost = data["cost"]
                    if distances[u] + cost < distances[v]:
                        distances[v] = distances[u] + cost
                        predecessors[v] = u
                        changed = True
        if not changed:
            break

    for u in graph:
        for v, data in graph[u].items():
            if "cost" in data:
                cost = data["cost"]
                if distances[u] + cost < distances[v]:
                    print("Negative-weight cycle detected!")
                    return None, None, None

    if end not in distances:
        return None, None, None

    path = []
    total_distance = 0
    current = end
    while current is not None:
        path.append(current)
        previous = predecessors[current]
        if previous is not None:
            total_distance += calculate_distance(airport_data[previous]["latitude_rad"],airport_data[previous]["longitude_rad"],airport_data[current]["latitude_rad"],airport_data[current]["longitude_rad"])

        current = previous

    path.reverse()
    return distances[end], path, total_distance

def print_detailed_route(path, airport_data):
    """
    Prints a detailed breakdown of the route, including airports, distances,
    and airlines.

    Args:
        path:  A list of airport IATA codes representing the route.
        airport_data:  The dictionary containing airport and route data.
    """
    
    if path is None or len(path) < 2:
        print("No route found.")
        return

    print("Shortest route found:")  # Consistent with your image
    total_distance = 0
    for i in range(len(path) - 1):
        origin = path[i]
        destination = path[i + 1]

        # Use pre-calculated radian values for distance calculation
        distance = calculate_distance(
            airport_data[origin]["latitude_rad"],
            airport_data[origin]["longitude_rad"],
            airport_data[destination]["latitude_rad"],
            airport_data[destination]["longitude_rad"]
        )
        total_distance += distance

        # --- Robust Airline Information Retrieval ---
        airlines = []
        # Check if 'routes' and origin airport exist in airport_data
        if "routes" in airport_data.get(origin, {}) :
            for route in airport_data[origin]["routes"]:
                if route.get("iata") == destination:  # Use .get() for safety
                    if "carriers" in route:
                        for carrier in route["carriers"]:
                            airlines.append(carrier.get("name", "Unknown Airline"))  # Use .get()

        airline_str = ", ".join(airlines) if airlines else "Unknown Airline"
        print(f"{origin} -> {destination} | {distance:.0f} km | Airlines: {airline_str}")

    print(f"Total Distance: {total_distance:.0f} km")


def main():
    filepath = "airline_routes.json"
    airport_data = load_airport_data(filepath)

    if not airport_data:
        return

    price_per_km = 0.25

    origin_iata = get_airport_code("Enter departure airport IATA code: ")
    destination_iata = get_airport_code("Enter destination airport IATA code: ")

    discount_routes = {
        ("JFK", "LAX"): (0.10, True),
        ("LHR", "JFK"): (0.08, False),
        ("JFK", "SYD"): (0.12, False),
        ("CDG", "SIN"): (0.15, True),
        ("ATL", "MIA"): (0.05, True),
        ("ORD", "DFW"): (0.10, True),
        ("FRA", "IST"): (0.18, False),
        ("DXB", "BOM"): (0.20, True),
        ("NRT", "HNL"): (0.07, False),
        ("BOS", "JFK"): (0.03, True),
        ("SEA", "SFO"): (0.05, True),
        ("LHR", "CDG"): (0.02, False),
        ("AMS", "BRU"): (0.02, True),
        ("HKG", "TPE"): (0.04, False),
        ("YYZ", "YVR"): (0.09, False),
        ("GRU", "EZE"): (0.11, False),
        ("JNB", "CPT"): (0.06, False),
        ("ZZZ", "LAX"): (0.50, True),
        ("JFK", "XXX"): (0.20, False),
    }

    graph_bf = {}
    for airport, details in airport_data.items():
        graph_bf[airport] = {}
        if "routes" in details:
            for route in details["routes"]:
                destination = route["iata"]
                price, _ = get_price_for_route_bellman_ford(airport, destination, airport_data, price_per_km, discount_routes)
                if price is not None:
                    graph_bf[airport][destination] = {"cost": price}

    bf_price, bf_path, total_bf_distance = bellman_ford(graph_bf, origin_iata, destination_iata, airport_data, discount_routes)
    standard_price, standard_distance = get_price_for_route(origin_iata, destination_iata, airport_data, price_per_km)

    if bf_price is not None:
        print_detailed_route(bf_path, airport_data)  # Use the corrected function

        if standard_price is not None and standard_price != 0:
            discount_percentage = ((standard_price - bf_price) / standard_price) * 100
            print(f"Discount percentage compared to standard price: {discount_percentage:.2f}%")
            print(f"Bellman-Ford Price: ${bf_price:.2f}")
        elif standard_price == 0:
            print("Standard price is zero, cannot calculate discount.")
        else:
            print("No standard price available to compare against.")
    else:
        print("No path found or negative cycle detected (Bellman-Ford).")

    if standard_price is not None:
        print(f"\nPrice (Standard) from {origin_iata} to {destination_iata}: ${standard_price:.2f}")
        print(f"Total Distance (Standard): {standard_distance:.2f} km")
    else:
        print("Could not calculate standard price.")

if __name__ == "__main__":
    main()