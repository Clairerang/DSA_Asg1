import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculates the great-circle distance (Haversine formula)."""
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.asin(math.sqrt(a))
    r = 6371  # Radius of Earth in kilometers.
    return c * r

def calculate_price(distance, price_per_km):
    """Calculates the price based on distance and price per kilometer."""
    return round(distance * price_per_km, 2)

def get_price_for_route(origin, destination, price_per_km = 0.25):
    """Calculates the price for a route using the AirportDatabase."""

    try:
        distance = calculate_distance(
            float(origin.latitude), float(origin.longitude),
            float(destination.latitude), float(destination.longitude)
        )
        price = calculate_price(distance, price_per_km)
        return price
    except ValueError as e:
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
    while True:
        origin_iata = get_airport_code("Enter departure airport IATA code: ")
        destination_iata = get_airport_code("Enter destination airport IATA code: ")

        price = get_price_for_route(origin_iata, destination_iata)

        if price is not None:
            print(f"Price from {origin_iata} to {destination_iata}: ${price:.2f}")
        else:
            print(f"Could not calculate price for the route from {origin_iata} to {destination_iata}.")

        another_calculation = input("Calculate another price? (y/n): ").strip().lower()
        if another_calculation != 'y':
            break  

if __name__ == "__main__":
    main()
