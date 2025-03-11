import json
from collections import deque

# Load the dataset
with open('airline_routes.json', 'r') as file:
    airports = json.load(file)

# BFS to find flight paths leading to a specified airport (limited to 10 paths)
def bfs_paths_to_airport(airports, goal, max_paths=10):
    all_paths = []
    for start_airport in airports.keys():
        if start_airport == goal:
            continue
        queue = deque([(start_airport, [start_airport])])
        visited = set()

        while queue and len(all_paths) < max_paths:
            current, path = queue.popleft()

            if current == goal:
                all_paths.append(path)
                break

            visited.add(current)

            for route in airports[current].get('routes', []):
                neighbor = route['iata']
                if neighbor in airports and neighbor not in visited and neighbor not in path:
                    queue.append((neighbor, path + [neighbor]))

        if len(all_paths) >= max_paths:
            break

    return all_paths

# User input
goal_airport = input("Enter destination airport IATA code: ").strip().upper()

# Find paths
paths = bfs_paths_to_airport(airports, goal_airport, max_paths=10)

# Display results
if paths:
    print(f"Up to 10 shortest paths found leading to {goal_airport}:")
    for idx, path in enumerate(paths, 1):
        print(f"{idx}: {' -> '.join(path)}")
else:
    print(f"No paths found leading to {goal_airport}.")
