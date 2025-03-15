import json
import heapq
from math import radians, cos, sin, sqrt, atan2

# Load the dataset
with open('airline_routes.json', 'r') as file:
    airports = json.load(file)

# Calculate heuristic using haversine distance
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculates the Haversine distance between two points on Earth.

    Args:
        lat1: Latitude of the first point in degrees.
        lon1: Longitude of the first point in degrees.
        lat2: Latitude of the second point in degrees.
        lon2: Longitude of the second point in degrees.

    Returns:
        The Haversine distance in kilometers.
    """

    R = 6371  # Earth radius in kilometers
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c

def dijkstra(airports, src, dest):
    """
    Finds the shortest path between two airports using Dijkstra's algorithm.

    Args:
        airports: A dictionary representing the airport and route data.  The keys
            are airport IATA codes (strings), and the values are dictionaries
            containing airport details, including a 'routes' list.
        src: The IATA code of the source (departure) airport.
        dest: The IATA code of the destination airport.

    Returns:
        A tuple containing:
            - The total distance of the shortest path in kilometers (float).
            - A list of airport IATA codes representing the shortest path
            (list of strings).
        Returns (float('inf'), []) if no path is found.
    """
    queue = [(0, src, [])]  # Priority queue: (distance, current_node, path_so_far)
    seen = set()    # Keep track of visited nodes
    min_dist = {src: 0} # Store the minimum distance to reach each node

    while queue:
        (distance, node, path) = heapq.heappop(queue) # Get the node with the smallest distance
        if node in seen:
            continue

        path = path + [node]
        seen.add(node)

        if node == dest:
            return (distance, path)
        
        # Iterate through the routes (edges) from the current airport
        for route in airports[node]['routes']:
            neighbor = route['iata']

            if neighbor in seen:
                continue

            prev_dist = min_dist.get(neighbor, float('inf'))
            new_dist = distance + route['km']

            # If a shorter path to the neighbor is found, update min_dist and add to the queue
            if new_dist < prev_dist:
                min_dist[neighbor] = new_dist
                heapq.heappush(queue, (new_dist, neighbor, path))

    return (float('inf'), [])

# User inputs
start_iata = input("Enter departure airport IATA code: ").strip().upper()
goal_iata = input("Enter destination airport IATA code: ").strip().upper()

if start_iata not in airports or goal_iata not in airports:
    print("Invalid IATA code(s). Please check and try again.")
else:
    distance, route = dijkstra(airports, start_iata, goal_iata)

    if route:
        print("Shortest route found:")
        for i in range(len(route) - 1):
            start_iata, next_iata = route[i], route[i + 1]
            route_info = next(route for route in airports[start_iata]['routes'] if route['iata'] == next_iata)
            carrier_names = ', '.join(carrier['name'] for carrier in route_info.get('carriers', [])) or "Unknown Airline"
            print(f"{start_iata} -> {next_iata} | {route_info['km']} km | Airlines: {carrier_names}")

        print(f"Total Distance: {distance} km")
    else:
        print(f"No route found from {start_iata} to {goal_iata}.")