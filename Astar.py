import json
import heapq
from math import radians, cos, sin, sqrt, atan2

# Load the dataset
with open('airline_routes.json', 'r') as file:
    airports = json.load(file)

# Calculate heuristic using haversine distance
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

# Heuristic function
def heuristic(a, b):
    lat1, lon1 = float(airports[a]['latitude']), float(airports[a]['longitude'])
    lat2, lon2 = float(airports[b]['latitude']), float(airports[b]['longitude'])
    return haversine_distance(lat1, lon1, lat2, lon2)

# A* search algorithm implementation
def astar(airports, start, goal):
    open_set = [(0, start, [])]
    visited = set()

    while open_set:
        cost, current, path = heapq.heappop(open_set)

        if current == goal:
            return path + [current]

        if current in visited:
            continue

        visited.add(current)

        for route in airports[current].get('routes', []):
            neighbor = route['iata']
            if neighbor in airports and neighbor not in visited:
                priority = cost + route['km'] + heuristic(neighbor, goal)
                heapq.heappush(open_set, (priority, neighbor, path + [current]))

    return None

# Find airports by country
def find_airports(country_name):
    return [iata for iata, airport in airports.items() if airport['country'].lower() == country_name.lower()]

# User inputs
start_country = input("Enter departure country: ").strip()
goal_country = input("Enter destination country: ").strip()

start_airports = find_airports(start_country)
goal_airports = find_airports(goal_country)

shortest_route = None
shortest_distance = float('inf')

for start in start_airports:
    for goal in goal_airports:
        route = astar(airports, start, goal)
        if route:
            total_distance = sum(
                next(route_info['km'] for route_info in airports[route[i]]['routes'] if route_info['iata'] == route[i + 1])
                for i in range(len(route) - 1)
            )

            if total_distance < shortest_distance:
                shortest_route = route
                shortest_distance = total_distance

if shortest_route:
    print("Shortest route found:")
    for i in range(len(shortest_route) - 1):
        start_iata, next_iata = shortest_route[i], shortest_route[i + 1]
        route_info = next(route for route in airports[start_iata]['routes'] if route['iata'] == next_iata)
        carrier_names = ', '.join(carrier['name'] for carrier in route_info.get('carriers', [])) or "Unknown Airline"
        print(f"{start} -> {goal} | {route_info['km']} km | Airlines: {carrier_names}")

    print(f"Total Distance: {shortest_distance} km")
else:
    print(f"No route found from {start_country} to {goal_country}.")
