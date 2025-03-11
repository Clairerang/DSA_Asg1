import json
import heapq
from collections import defaultdict

# Load the dataset
with open('airline_routes.json', 'r') as file:
   airports = json.load(file)

# Convert JSON to a graph structure
def build_graph(airports):
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
   def dijkstra(source, target):
      heap = [(0, source, [])]
      best_dist = {source: 0}
      while heap:
         cost, node, path = heapq.heappop(heap)
         path = path + [node]
         if node == target:
               return cost, path
         for neighbor, weight in graph[node]:
               new_cost = cost + weight
               if neighbor not in best_dist or new_cost < best_dist[neighbor]:
                  best_dist[neighbor] = new_cost
                  heapq.heappush(heap, (new_cost, neighbor, path))
      return float('inf'), []
   
   A = []
   B = []
   first_cost, first_path = dijkstra(src, dest)
   if first_path:
      A.append((first_cost, first_path))
   else:
      return []
   
   for i in range(1, k):
      for j in range(len(A[-1][1]) - 1):
         spur_node = A[-1][1][j]
         root_path = A[-1][1][:j + 1]
         removed_edges = []
         
         for path_cost, path in A:
               if path[:j + 1] == root_path:
                  last_node = path[j]
                  next_node = path[j + 1]
                  for idx, (neighbor, weight) in enumerate(graph[last_node]):
                     if neighbor == next_node:
                           removed_edges.append((last_node, graph[last_node][idx]))
                           del graph[last_node][idx]
                           break
         
         spur_cost, spur_path = dijkstra(spur_node, dest)
         
         if spur_path:
               total_path = root_path[:-1] + spur_path
               total_cost = sum(route_info[(total_path[i], total_path[i + 1])][0] for i in range(len(total_path) - 1))
               if (total_cost, total_path) not in B:
                  B.append((total_cost, total_path))
         
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