from collections import deque
from data_loader import airport_db  # Import the global AirportDatabase object

def bfs_min_connections(airport_db, start_iata, goal_iata):
    """
    Finds the shortest flight route (minimum layovers) between two airports using BFS,
    ensuring that only routes with available carriers are considered.

    Args:
        airport_db (AirportDatabase): The airport database containing all airports.
        start_iata (str): IATA code of the departure airport.
        goal_iata (str): IATA code of the arrival airport.

    Returns:
        list: The sequence of airport IATA codes forming the shortest route, or None if no route exists.
    """

    # Ensure the airports exist in the database
    start_airport = airport_db.get_airport(start_iata)
    goal_airport = airport_db.get_airport(goal_iata)

    if not start_airport or not goal_airport:
        print("Invalid airport IATA code(s).")
        return None

    # BFS queue (each entry is (current_airport, path_taken))
    queue = deque([(start_airport, [start_airport.iata])])
    visited = set()

    while queue:
        current_airport, path = queue.popleft()

        if current_airport.iata == goal_iata:
            return path  # Found the shortest path

        visited.add(current_airport.iata)

        # Explore all direct flight routes from the current airport
        for route in current_airport.routes:
            next_airport = airport_db.get_airport(route.iata)

            # Ensure the route has at least one carrier with flights available
            if next_airport and next_airport.iata not in visited and any(route.carriers):
                visited.add(next_airport.iata)
                queue.append((next_airport, path + [next_airport.iata]))

    return None  # No route found

if __name__ == "__main__":
    print(bfs_min_connections(airport_db, "KIE", "KHY"))