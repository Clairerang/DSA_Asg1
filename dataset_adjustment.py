import json
import datetime
import random

def add_date_time_to_routes(filename: str, output_filename: str):
    """
    Adds realistic departure and arrival date/time information to the routes
    in the given JSON file, and saves the modified data to a new JSON file.

    Args:
        filename: Path to the input JSON file.
        output_filename: Path to save the modified JSON data.
    """

    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for airport_iata, airport_data in data.items():
        if 'routes' in airport_data:
            for route in airport_data['routes']:
                for carrier_data in route['carriers']:  # Iterate through carriers
                    # Get base departure time (using current date for simplicity)
                    now = datetime.datetime.now()
                    base_departure_datetime = datetime.datetime(now.year, now.month, now.day, random.randint(6, 22), random.choice([0, 15, 30, 45]))  # Random hour between 6 AM and 10 PM


                    # Convert duration from minutes to timedelta
                    flight_duration = datetime.timedelta(minutes=int(route['min']))

                    # Calculate arrival time
                    arrival_datetime = base_departure_datetime + flight_duration

                    # Format date and time strings (ISO 8601 format)
                    departure_date = base_departure_datetime.strftime("%Y-%m-%d")
                    departure_time = base_departure_datetime.strftime("%H:%M")
                    arrival_date = arrival_datetime.strftime("%Y-%m-%d")
                    arrival_time = arrival_datetime.strftime("%H:%M")
                    
                    # Get Timezone for departure and arrival
                    departure_timezone = airport_data['timezone']
                    arrival_timezone = data.get(route['iata'], {}).get('timezone', 'UTC') # Default to UTC if not available

                    # Add date and time information to the *carrier_data* dictionary
                    carrier_data['departure_date'] = departure_date
                    carrier_data['departure_time'] = departure_time
                    carrier_data['arrival_date'] = arrival_date
                    carrier_data['arrival_time'] = arrival_time
                    carrier_data['departure_timezone'] = departure_timezone #added departure and arrival timezones
                    carrier_data['arrival_timezone'] = arrival_timezone

    # Save the modified data to a new JSON file
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=4)  # Use indent for readability



def main():
  add_date_time_to_routes('airline_routes.json', 'airline_routes_with_datetime.json')

if __name__ == '__main__':
    main()