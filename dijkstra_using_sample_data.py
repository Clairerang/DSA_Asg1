# Dijkstra's algorithm is used to find the shortest path between 2 points (airports)

import csv
import heapq
import os
import math

# read airports.txt to get a dictionary where each key is IATA code of an airport and the value contains attributes of that airport
def parse_airports(file_path):
   airports = {}
   with open(file_path, 'r', encoding="utf-8") as file:
      reader = csv.reader(file)
      next(reader)  # Skip header
      for row in reader:
         airports[row[3]] = {
            'name': row[0],
            'city': row[1],
            'country': row[2],
            'iata': row[3],
            'icao': row[4],
            'latitude': float(row[5]),
            'longitude': float(row[6]),
            'altitude': int(row[7]),
            'timezone': row[8]
         }
   return airports

# read routes.txt to get a dictionary where each key is IATA code of an airport and the value contains airports you can fly to from that airport
def parse_routes(file_path):
   routes = {}
   with open(file_path, 'r', encoding="utf-8") as file:
      reader = csv.reader(file)
      next(reader)  # Skip header
      for row in reader:
         src, dest = row[2], row[3]
         if src not in routes:
            routes[src] = []
         routes[src].append(dest)
   return routes

# used to get the distances between airports
def haversine(lat1, lon1, lat2, lon2):
   R = 6371  # Radius of the Earth in kilometers
   dlat = math.radians(lat2 - lat1)
   dlon = math.radians(lon2 - lon1)
   a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
   c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
   distance = R * c
   return distance

def dijkstra(routes, airports, src, dest):
   queue = [(0, src, [])]
   seen = set()
   min_dist = {src: 0}

   while queue:
      (distance, node, path) = heapq.heappop(queue)
      if node in seen:
         continue

      path = path + [node]
      seen.add(node)

      if node == dest:
         return (distance, path)

      for neighbor in routes.get(node, []):
         if neighbor in seen:
            continue
         prev_dist = min_dist.get(neighbor, float('inf'))
         new_dist = distance + haversine(airports[node]['latitude'], airports[node]['longitude'], airports[neighbor]['latitude'], airports[neighbor]['longitude'])
         if new_dist < prev_dist:
            min_dist[neighbor] = new_dist
            heapq.heappush(queue, (new_dist, neighbor, path))

   return (float('inf'), [])

def main():
   base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.', 'Sample Data'))
   airports_file = os.path.join(base_path, 'Airport Sample.txt')
   routes_file = os.path.join(base_path, 'Route Sample.txt')

   airports = parse_airports(airports_file)
   print("Available airports:")
   for i, airport in enumerate(airports.values(), 1):
      print(f"{i}. {airport['name']} ({airport['iata']})")

   routes = parse_routes(routes_file)

   print("\nTest cases:")
   print("Source: MAG, Destination: HGU (Direct path)")
   print("Source: GKA, Destination: VEY (Layover path)")
   print("Source: POM, Destination: VEY (Layover path)")
   print("Source: GKA, Destination: THU (No path)")



   src = input("\nEnter source airport IATA code: ").strip().upper()
   dest = input("Enter destination airport IATA code: ").strip().upper()

   if src not in airports or dest not in airports:
      print("Invalid airport IATA code.")
      return

   distance, path = dijkstra(routes, airports, src, dest)
   if distance == float('inf'):
      print(f"No path found from {src} to {dest}.")
   else:
      print(f"Shortest path from {src} to {dest}: {' -> '.join(path)} with distance {distance:.2f} km")

main()


