import json
import random

def add_seats_remaining(filename: str):
    """
    Adds a 'seats_remaining' field to each carrier in the routes of the JSON data,
    modifying the file in-place.

    Args:
        filename: Path to the JSON file.
    """

    with open(filename, 'r+', encoding='utf-8') as f:  # Open in 'r+' mode
        data = json.load(f)

        for airport_iata, airport_data in data.items():
            if 'routes' in airport_data:
                for route in airport_data['routes']:
                    for carrier_data in route['carriers']:
                        seats_remaining = random.randint(0, 15)
                        carrier_data['seats_remaining'] = seats_remaining

        f.seek(0)  # Rewind to the beginning of the file
        json.dump(data, f, indent=4)  # Overwrite the file
        f.truncate()  # Remove any remaining old content


def main():
    add_seats_remaining('airline_routes.json')
    print("Modified airline_routes.json in place.")

if __name__ == '__main__':
    main()