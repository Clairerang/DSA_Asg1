import json
import heapq
from math import radians, cos, sin, sqrt, atan2

#Load the dataset
with open('airline_routes.json', 'r') as file:
    airports = json.load(file)

#calculate heuristic using haversine distance
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  #Earth radius in kilometers
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat, dlon = lat2 - lat1, lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

#heuristic function
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

# user input by airport IATA codes
start_airport = input("Enter departure airport IATA code: ").strip().upper()
goal_airport = input("Enter destination airport IATA code: ").strip().upper()

route = astar(airports, start_airport, goal_airport)

if route:
    print("Shortest route found:")
    total_distance = 0
    for i in range(len(route) - 1):
        segment_start, segment_end = route[i], route[i + 1]
        route_info = next((r for r in airports[segment_start]['routes'] if r['iata'] == segment_end), None)
        if route_info:
            carrier_names = ', '.join(carrier['name'] for carrier in route_info.get('carriers', [])) or "Unknown Airline"
            distance = route_info['km']
            total_distance += distance
            print(f"{segment_start} -> {segment_end} | {distance} km | Airline(s): {carrier_names}")

    print(f"Total distance: {total_distance} km")
else:
    print("No route found between", start_airport, "and", goal_airport)
