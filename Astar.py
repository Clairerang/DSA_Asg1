import json
import heapq
from math import radians, cos, sin, sqrt, atan2

# Load the dataset
with open('airline_routes.json', 'r') as file:
    airports = json.load(file)

#Calculates the Haversine distance (shortest distance over Earth's surface) between two points using latitude and longitude.
def haversine_distance(lat1, lon1, lat2, lon2):
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

    #convert latitude and longtitude from degrees to radius
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    #compute the distance using the Haversine formula
    dlat, dlon = lat2 - lat1, lon2 - lon1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c

# heuristic function
def heuristic(a, b):
    """
    Calculates the heuristic (estimated distance) between two airports using the Haversine distance.

    Args:
        airports: The dictionary of airport data.
        a: IATA code of the first airport.
        b: IATA code of the second airport.

    Returns:
        The estimated distance between the two airports in kilometers.
    """

    lat1, lon1 = float(airports[a]['latitude']), float(airports[a]['longitude'])
    lat2, lon2 = float(airports[b]['latitude']), float(airports[b]['longitude'])
    return haversine_distance(lat1, lon1, lat2, lon2)

#A* search algorithm 
def astar_preferred_airline(airports, start, goal, preferred_airlines):
    """
    Uses A* search to find the best flight routes between two airports,
    while ensuring that at least one flight in the route && is operated 
    by a preferred airline.

    """
    
    open_set = [(0, 0, start, [], False)]  # (priority, cost_so_far, current_node, path, has_preferred)
    visited = set() #store visited airport preventing cycles
    best_routes = [] #store best flight
    preferred_airlines = {airline.lower() for airline in preferred_airlines} #store user inputted preferred airlines

    while open_set:
        priority, cost, current, path, has_preferred = heapq.heappop(open_set)

        # if we've reached the destination airport, save the route if it contains a preferred airlines
        if current == goal:
            if has_preferred:  # Ensure at least one preferred airline is in the journey
                best_routes.append((path + [current], cost))
            continue
        
        #mark the current airport as visited
        if current in visited:
            continue

        visited.add(current)

        #explore all direct flights from the current airport
        for route in airports[current].get('routes', []):
            neighbor = route['iata'] #the destination airport for this flight
            airlines = {carrier['name'].lower() for carrier in route.get('carriers', [])} #get airlines for this flight
            is_preferred = bool(airlines.intersection(preferred_airlines)) #check if any airline matches the preferred list

            #add the flight to the search queue if it has not been visited
            if neighbor in airports and neighbor not in visited:
                base_cost = route['km'] #distance for this flight segment
                new_cost = cost + base_cost #update total cost(distance travelled)
                priority = new_cost + heuristic(neighbor, goal) # A* priority: cost + estimated distance
                heapq.heappush(open_set, (priority, new_cost, neighbor, path + [current], has_preferred or is_preferred))

    return sorted(best_routes, key=lambda x: x[1])[:1] #return the shortest route with the preferred airlines

#user input by airport IATA codes
start_airport = input("Enter departure airport IATA code: ").strip().upper()
goal_airport = input("Enter destination airport IATA code: ").strip().upper()
preferred_airlines = input("Enter preferred airlines (comma-separated): ").strip().split(',')
preferred_airlines = [airline.strip().lower() for airline in preferred_airlines] #convert to lower case

routes = astar_preferred_airline(airports, start_airport, goal_airport, preferred_airlines)

if routes:
    print("\nTop best routes containing your preferred airlines:")
    for route, total_distance in routes:
        print("\nRoute:")
        actual_distance = 0
        found_preferred = False
        for i in range(len(route) - 1):
            segment_start, segment_end = route[i], route[i + 1]
            segment_info = next((r for r in airports[segment_start]['routes'] if r['iata'] == segment_end), None)
            if segment_info:
                carrier_names = ', '.join(carrier['name'] for carrier in segment_info.get('carriers', [])) or "Unknown Airline"
                distance = segment_info['km']
                if any(airline in carrier_names.lower() for airline in preferred_airlines):
                    found_preferred = True  # ensure at least one preferred airline is in the final route
                actual_distance += distance
                print(f"{segment_start} -> {segment_end} | {distance} km | Airline(s): {carrier_names}")
        
        if found_preferred:
            print(f"Total Distance: {actual_distance} km\n")
        else:
            print("\nRoute discarded: No preferred airlines were found.\n")
else:
    print("\nNo suitable routes found between", start_airport, "and", goal_airport, "using the preferred airlines.")
