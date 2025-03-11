import json
import math

def calculate_distance(lat1_rad, lon1_rad, lat2_rad, lon2_rad):
    """Calculates distance (Haversine, optimized)."""
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
    """Loads airport data, converting lat/lon to radians."""
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
    """Calculates price (no discounts), using pre-calculated radians."""
    if origin_iata not in airport_data or destination_iata not in airport_data:
        return None, None
    try:
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
    """Calculates price (Bellman-Ford, discounts), using pre-calculated radians."""
    if origin_iata not in airport_data or destination_iata not in airport_data:
        return None, None
    try:
        origin_lat_rad = airport_data[origin_iata]["latitude_rad"]
        origin_lon_rad = airport_data[origin_iata]["longitude_rad"]
        dest_lat_rad = airport_data[destination_iata]["latitude_rad"]
        dest_lon_rad = airport_data[destination_iata]["longitude_rad"]
        distance = calculate_distance(origin_lat_rad, origin_lon_rad, dest_lat_rad, dest_lon_rad)
        base_price = calculate_price(distance, price_per_km)

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

def bellman_ford(graph, start, end, airport_data, discount_routes): # Added parameters
    """Finds the shortest path using Bellman-Ford (with early exit)."""
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

    # Pass airport_data and discount_routes to bellman_ford
    bf_price, bf_path, total_distance = bellman_ford(graph_bf, origin_iata, destination_iata, airport_data, discount_routes)
    standard_price, standard_distance = get_price_for_route(origin_iata, destination_iata, airport_data, price_per_km)

    if bf_price is not None:
        print(f"Shortest distance (Bellman-Ford) from {origin_iata} to {destination_iata}: ${bf_price:.2f}")
        print(f"Path: {', '.join(bf_path)}")
        print(f"Total Distance (Bellman-Ford): {total_distance:.2f} km")

        if standard_price is not None and standard_price != 0:
            discount_percentage = ((standard_price - bf_price) / standard_price) * 100
            print(f"Discount percentage compared to standard price: {discount_percentage:.2f}%")
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