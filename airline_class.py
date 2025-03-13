import json

class Airport:
    def __init__(self, data):
        self.city_name = data.get("city_name")
        self.continent = data.get("continent")
        self.country = data.get("country")
        self.country_code = data.get("country_code")
        self.display_name = data.get("display_name")
        self.elevation = data.get("elevation")
        self.iata = data.get("iata")
        self.icao = data.get("icao")
        self.latitude = data.get("latitude")
        self.longitude = data.get("longitude")
        self.name = data.get("name")
        self.routes = [Route(route) for route in data.get("routes", [])]
        self.timezone = data.get("timezone")

    def __repr__(self):
        return f"Airport({self.iata}, {self.city_name}, {self.country})"


class Route:
    def __init__(self, data):
        self.iata = data.get("iata")
        self.km = data.get("km")
        self.min = data.get("min")
        self.carriers = [Carrier(carrier) for carrier in data.get("carriers", [])]

    def __repr__(self):
        return f"Route(to={self.iata}, km={self.km}, min={self.min})"


class Carrier:
    def __init__(self, data):
        self.iata = data.get("iata")  # Airline IATA Code
        self.name = data.get("name")  # Airline Name
        self.departure_date = data.get("departure_date")  # Departure Date
        self.departure_time = data.get("departure_time")  # Departure Time
        self.arrival_date = data.get("arrival_date")  # Arrival Date
        self.arrival_time = data.get("arrival_time")  # Arrival Time
        self.departure_timezone = data.get("departure_timezone")  # Timezone of Departure
        self.arrival_timezone = data.get("arrival_timezone")  # Timezone of Arrival
        self.seats_remaining = int(data.get("seats_remaining", 0))  # Number of available seats

    def __repr__(self):
        return (f"Carrier({self.iata}, {self.name}, Departure: {self.departure_date} {self.departure_time}, "
                f"Arrival: {self.arrival_date} {self.arrival_time})")


class AirportDatabase:
    def __init__(self, airport_data):
        self.airports = {key: Airport(value) for key, value in airport_data.items()}

    def get_airport(self, iata_code):
        return self.airports.get(iata_code)

    def __repr__(self):
        return f"AirportDatabase({len(self.airports)} airports)"


def read_json_file(file_path):
    """
    Reads a JSON file and returns the data as a Python dictionary or list.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict or list: The JSON data as a Python dictionary or list,
                      or None if an error occurred.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in {file_path}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    file_path = 'airline_routes.json'  # Replace with the actual path to your JSON file

    db = AirportDatabase(read_json_file(file_path))
    
    # Example: Fetch an airport and print details
    airport_code = "AAA"
    airport = db.get_airport(airport_code)
    
    if airport:
        print(f"Airport Details: {airport}")
        
        # Print all routes
        for route in airport.routes:
            print(f"Route to {route.iata}: {route.km} km, {route.min} min")
            
            # Print all carriers for the route
            for carrier in route.carriers:
                print(f"  - {carrier}")
