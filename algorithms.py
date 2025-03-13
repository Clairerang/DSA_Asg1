from collections import deque, defaultdict
from data_loader import airport_db  # Import the global AirportDatabase object
import heapq

## BFS
def bfs_min_connections(start_iata, goal_iata):
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

## DIJKSTRA
def yen_k_shortest_paths(src, dest, k=1):
    """
    Finds K-shortest paths between source and destination using Yen's Algorithm.

    Args:
        graph (dict): The airport graph represented as an adjacency list.
        src (str): The IATA code of the departure airport.
        dest (str): The IATA code of the destination airport.
        k (int): Number of shortest paths to find.

    Returns:
        list: A list of routes, each being a sequence of airport IATA codes, or None if no route exists.
    """

    def build_graph(airport_db):
        """Converts airport data into a graph structure."""
        graph = defaultdict(list)

        for airport in airport_db.airports.values():
            for route in airport.routes:
                if route.carriers:  # Ensure the route has available carriers
                    neighbor = route.iata
                    distance = route.km
                    graph[airport.iata].append((neighbor, distance))

        return graph
    
    def dijkstra(source, target):
        """Finds the shortest path from source to target using Dijkstra's Algorithm."""
        heap = [(0, source, [])]
        best_dist = {source: 0}

        while heap:
            cost, node, path = heapq.heappop(heap)
            path = path + [node]

            if node == target:
                return path  # Return only the sequence of IATA codes

            for neighbor, weight in graph.get(node, []):
                new_cost = cost + weight
                if neighbor not in best_dist or new_cost < best_dist[neighbor]:
                    best_dist[neighbor] = new_cost
                    heapq.heappush(heap, (new_cost, neighbor, path))

        return None  # No route found

    graph = build_graph(airport_db)
    # Step 1: Get the first shortest path using Dijkstra
    A = []
    B = []
    first_path = dijkstra(src, dest)

    if first_path:
        A.append(first_path)
    else:
        return None  # Return None if no route exists

    # Step 2: Iteratively find up to K shortest paths
    for i in range(1, k):
        for j in range(len(A[-1]) - 1):
            spur_node = A[-1][j]
            root_path = A[-1][:j + 1]
            removed_edges = []

            for path in A:
                if path[:j + 1] == root_path:
                    last_node = path[j]
                    next_node = path[j + 1]
                    for idx, (neighbor, weight) in enumerate(graph[last_node]):
                        if neighbor == next_node:
                            removed_edges.append((last_node, graph[last_node][idx]))
                            del graph[last_node][idx]
                            break

            spur_path = dijkstra(spur_node, dest)

            if spur_path:
                total_path = root_path[:-1] + spur_path
                if total_path not in B:
                    B.append(total_path)

            for last_node, edge in removed_edges:
                graph[last_node].append(edge)

        if not B:
            break

        B.sort()
        A.append(B.pop(0))

    return A  # Return list of IATA code sequences


if __name__ == "__main__":
    # User input
    start_iata = input("Enter departure airport IATA code: ").strip().upper()
    goal_iata = input("Enter destination airport IATA code: ").strip().upper()


    # BFS
    # print(bfs_min_connections(airport_db, start_iata, goal_iata))


    routes = yen_k_shortest_paths(start_iata, goal_iata)
    # print(routes)
    # if routes:
    #     print(f"Top {len(routes)} shortest routes found:")
    #     for idx, route in enumerate(routes, start=1):
    #         print(f"Route {idx}: {' → '.join(route)}")
    # else:
    #     print(f"No route found from {start_iata} to {goal_iata}.")