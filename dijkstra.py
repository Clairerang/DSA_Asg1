import json
import heapq
from math import radians, cos, sin, sqrt, atan2

# Load the dataset
with open('airline_routes.json', 'r') as file:
    airports = json.load(file)

# Calculate heuristic using haversine distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    return R * c

def dijkstra(airports, src, dest):
    queue = [(0, src, [])]
    seen = set()
    min_dist = {src: 0}

    while queue:
        (distance, node, path) = heapq.heappop(queue)
        if node in seen:
            continue

        path = path + [node]
        seen.add(node)

        if node == dest:
            return (distance, path)

        for route in airports[node]['routes']:
            neighbor = route['iata']
            if neighbor in seen:
                continue
            prev_dist = min_dist.get(neighbor, float('inf'))
            new_dist = distance + route['km']
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