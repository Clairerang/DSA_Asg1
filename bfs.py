import json
from collections import deque

# loading of dataset
with open('airline_routes.json', 'r') as file:
    airports = json.load(file)

# BFS Algorithm to find minimum layovers between airports
def bfs_min_connections(airports, start, goal):
    """
    Finds the path with the minimum number of connections (layovers) between two airports
    using Breadth-First Search (BFS).

    Args:
        airports: A dictionary representing the airport and route data.  Keys are
            airport IATA codes (strings), and values are dictionaries with airport
            details, including a 'routes' list.
        start: The IATA code of the starting airport.
        goal: The IATA code of the destination airport.

    Returns:
        A list of airport IATA codes representing the path with the fewest connections,
        or None if no path is found.
    """

    queue = deque([(start, [start])]) #queue stores( current airport, path)
    visited = set() #set to track visited airports

    while queue: 
        current, path = queue.popleft() #get the first airport from the queue

        # if we reached the destination airport, return the path
        if current == goal:
            return path

        visited.add(current) #mark airport as visited

        for route in airports[current].get('routes', []): #get possible flight layover
            neighbor = route['iata'] #get next airport

            #if neighbor hasnt been visited, add it to queue
            #neighbor = next airport in the flight network
            if neighbor in airports and neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor])) #store updated path

    return None

#user inputs
start_airport = input("Enter departure airport IATA code: ").strip().upper()
goal_airport = input("Enter destination airport IATA code: ").strip().upper()

#calling of BFS function to find the shortest route
route = bfs_min_connections(airports, start_airport, goal_airport)

if route:
    print("Minimum layovers found:")
    total_distance = 0
    for i in range(len(route) - 1):
        segment_start, segment_end = route[i], route[i + 1] # to get 2 consecutive airports
        route_info = next((r for r in airports[segment_start]['routes'] if r['iata'] == segment_end), None)
        if route_info:
            carrier_names = ', '.join(carrier['name'] for carrier in route_info.get('carriers', [])) or "Unknown Airline"
            distance = route_info['km']
            total_distance += distance # accumulate total flight distance
            print(f"{segment_start} -> {segment_end} | {distance} km | Airline(s): {carrier_names}")

    print(f"Total distance: {total_distance} km")
    print(f"Number of Layovers (stops): {len(route) - 2}")
else:
    print("No route found between", start_airport, "and", goal_airport)
