import json
from collections import deque

# loading of dataset
with open('airline_routes.json', 'r') as file:
    airports = json.load(file)

# BFS Algorithm to find minimum layovers between airports
def bfs_min_connections(airports, start, goal):
    queue = deque([(start, [start])])
    visited = set()

    while queue:
        current, path = queue.popleft()

        if current == goal:
            return path

        visited.add(current)

        for route in airports[current].get('routes', []):
            neighbor = route['iata']
            if neighbor in airports and neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None

#user inputs
start_airport = input("Enter departure airport IATA code: ").strip().upper()
goal_airport = input("Enter destination airport IATA code: ").strip().upper()

route = bfs_min_connections(airports, start_airport, goal_airport)

if route:
    print("Minimum layovers found:")
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
    print(f"Number of Layovers (stops): {len(route) - 1}")
else:
    print("No route found between", start_airport, "and", goal_airport)
