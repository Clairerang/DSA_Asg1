import json
import heapq
from collections import defaultdict

# Load the dataset
with open('airline_routes.json', 'r') as file:
   airports = json.load(file)

# Convert JSON to a graph structure
def build_graph(airports):
   """
   Builds a graph representation of the airport network and extracts route information.

   Args:
      airports (dict): A dictionary representing the airport and route data loaded from the JSON file.
                        The keys are airport IATA codes (strings), and the values are dictionaries
                        containing airport details, including a 'routes' list.

   Returns:
      tuple: A tuple containing:
            - graph (defaultdict(list)):  An adjacency list representation of the airport network.
                                          Keys are airport IATA codes (strings), and values are lists
                                          of tuples.  Each tuple represents a flight connection:
                                          (neighboring_airport_iata_code, distance_in_km).
            - route_info (dict): A dictionary storing information about each route.
                                 Keys are tuples: (source_airport_iata, destination_airport_iata).
                                 Values are tuples: (distance_in_km, comma_separated_carrier_names).
                                 'Unknown Airline' is used if carrier information is missing.
   """

   graph = defaultdict(list)
   route_info = {}
   
   for airport, data in airports.items():
      for route in data['routes']:
         neighbor = route['iata']
         distance = route['km']
         carriers = ', '.join(carrier['name'] for carrier in route.get('carriers', [])) or "Unknown Airline"
         graph[airport].append((neighbor, distance))
         route_info[(airport, neighbor)] = (distance, carriers)
   
   return graph, route_info

def yen_k_shortest_paths(graph, route_info, src, dest, k=10):

   """
   Finds the K shortest paths between two airports in a graph using Yen's algorithm.

   Args:
      graph (defaultdict(list)): An adjacency list representing the airport network.
      route_info (dict):  A dictionary storing route information (distance, carriers)
                           as returned by `build_graph`.
      src (str): The IATA code of the source (departure) airport.
      dest (str): The IATA code of the destination airport.
      k (int, optional): The number of shortest paths to find. Defaults to 10.

   Returns:
      list: A list of tuples, where each tuple represents a path and its total distance.
            Each tuple contains: (total_distance_in_km, path_as_list_of_iata_codes).
            The list is sorted by total distance (shortest first).  Returns an empty list
            if no paths are found.
   """

   def dijkstra(source, target):
      """
         Finds the shortest path between two nodes in a graph using Dijkstra's algorithm.

         This is an inner function (nested function) within `yen_k_shortest_paths`.
         It has access to the variables in the enclosing function's scope (like `graph`).

         Args:
            source (str): The IATA code of the starting airport.
            target (str): The IATA code of the destination airport.

         Returns:
            tuple: A tuple containing: (total_distance, path_as_list_of_airport_iatas).
                     Returns (float('inf'), []) if no path is found.
      """

      heap = [(0, source, [])] # Priority queue: (cost, current_node, path_so_far)
      best_dist = {source: 0} # Store the shortest distance found to each node

      while heap:
         cost, node, path = heapq.heappop(heap) # Get the node with the lowest cost
         path = path + [node] # Extend the path

         if node == target:
               return cost, path # Found the target, return the cost and path
         
         for neighbor, weight in graph[node]:
               new_cost = cost + weight # Calculate the new cost to the neighbor

               # If the neighbor hasn't been visited or a shorter path is found
               if neighbor not in best_dist or new_cost < best_dist[neighbor]:
                  best_dist[neighbor] = new_cost
                  heapq.heappush(heap, (new_cost, neighbor, path))
      return float('inf'), []
   
   A = [] # List to store the K shortest paths (found paths)
   B = [] # List to store potential K shortest paths (candidate paths)

   # Find the very first shortest path using Dijkstra's algorithm
   first_cost, first_path = dijkstra(src, dest)
   if first_path:
      A.append((first_cost, first_path))
   else:
      return []
   

   # Yen's algorithm loop: iterate to find K shortest paths
   for i in range(1, k):
      # Iterate through the nodes of the (k-1)th shortest path
      for j in range(len(A[-1][1]) - 1):
         spur_node = A[-1][1][j]
         root_path = A[-1][1][:j + 1]
         removed_edges = []
         
         # Remove edges used by previous shortest paths that share the same root path
         for path_cost, path in A:
               if path[:j + 1] == root_path:
                  last_node = path[j]
                  next_node = path[j + 1]
                  for idx, (neighbor, weight) in enumerate(graph[last_node]):
                     if neighbor == next_node:
                           removed_edges.append((last_node, graph[last_node][idx]))
                           del graph[last_node][idx]
                           break
         
         # Find the shortest path from the spur node to the destination (deviation)
         spur_cost, spur_path = dijkstra(spur_node, dest)
         
         if spur_path:
               total_path = root_path[:-1] + spur_path
               total_cost = sum(route_info[(total_path[i], total_path[i + 1])][0] for i in range(len(total_path) - 1))
               if (total_cost, total_path) not in B:
                  B.append((total_cost, total_path))
         
         # Restore the removed edges to the graph, important for future iterations to ensure that all possible paths can still be explored
         for last_node, edge in removed_edges:
               graph[last_node].append(edge)
      
      if not B:
         break
      
      B.sort()
      A.append(B.pop(0))
   
   return A

graph, route_info = build_graph(airports)

# User inputs
start_iata = input("Enter departure airport IATA code: ").strip().upper()
goal_iata = input("Enter destination airport IATA code: ").strip().upper()

if start_iata not in graph or goal_iata not in graph:
   print("Invalid IATA code(s). Please check and try again.")
else:
   routes = yen_k_shortest_paths(graph, route_info, start_iata, goal_iata, k=10)
   
   if routes:
      print("Top 10 shortest routes found:")
      for idx, (distance, route) in enumerate(routes, start=1):
         print(f"Route {idx}: {distance} km")
         for i in range(len(route) - 1):
               start_iata, next_iata = route[i], route[i + 1]
               route_distance, carrier_names = route_info[(start_iata, next_iata)]
               print(f"  {start_iata} -> {next_iata} | {route_distance} km | Airlines: {carrier_names}")
         print()
   else:
      print(f"No route found from {start_iata} to {goal_iata}.")