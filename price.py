import json
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculates the great-circle distance (Haversine formula)."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of earth in kilometers.
    return c * r

def calculate_price(distance, price_per_km):
    """Calculates the price based on distance and price per kilometer."""
    return distance * price_per_km

def load_airport_data(filepath):
    """Loads airport data from a JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        print(f"Error loading data: {e}")
        return None

def get_price_for_route(origin_iata, destination_iata, airport_data, price_per_km):
    """Calculates the price for a route."""
    if origin_iata not in airport_data or destination_iata not in airport_data:
        return None

    try:
        origin_lat = float(airport_data[origin_iata]["latitude"])
        origin_lon = float(airport_data[origin_iata]["longitude"])
        dest_lat = float(airport_data[destination_iata]["latitude"])
        dest_lon = float(airport_data[destination_iata]["longitude"])

        distance = calculate_distance(origin_lat, origin_lon, dest_lat, dest_lon)
        price = calculate_price(distance, price_per_km)
        return price
    except (KeyError, ValueError, Exception) as e:
        print(f"Error processing route: {e}")
        return None

def get_airport_code(prompt):
    """Gets a valid IATA code from the user."""
    while True:
        code = input(prompt).strip().upper()  
        if len(code) == 3 and code.isalpha(): 
            return code
        else:
            print("Invalid IATA code. Please enter a 3-letter code.")

def main():
    """Main function to handle user input and display results."""
    filepath = "airline_routes.json"
    airport_data = load_airport_data(filepath)

    if not airport_data:
        return  

    price_per_km = 0.20  

    while True: 
        origin_iata = get_airport_code("Enter departure airport IATA code: ")
        destination_iata = get_airport_code("Enter destination airport IATA code: ")

        price = get_price_for_route(origin_iata, destination_iata, airport_data, price_per_km)

        if price is not None:
            print(f"Price from {origin_iata} to {destination_iata}: ${price:.2f}")
        else:
            print(f"Could not calculate price for the route from {origin_iata} to {destination_iata}.")

        
        another_calculation = input("Calculate another price? (y/n): ").strip().lower()
        if another_calculation != 'y':
            break  

if __name__ == "__main__":
    main()