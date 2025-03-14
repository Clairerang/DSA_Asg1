import json
import random

import json
import datetime
import random

def randomize_dates(filename: str, output_filename: str):
    """
    Randomizes departure and arrival dates in the given JSON file,
    maintaining the logical relationship between departure time,
    flight duration, and arrival time.  Dates are randomized within
    the next 365 days from the current date.

    Args:
        filename: Path to the input JSON file.
        output_filename: Path to save the modified JSON data.
    """

    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)

    now = datetime.datetime.now()

    for airport_iata, airport_data in data.items():
        if 'routes' in airport_data:
            for route in airport_data['routes']:
                for carrier_data in route['carriers']:
                    # 1. Randomize the *departure date* (within the next 365 days)
                    random_days_offset = random.randint(0, 365)
                    base_departure_datetime = now + datetime.timedelta(days=random_days_offset)

                    # 2. Randomize the *departure time* (between 6 AM and 10 PM)
                    departure_hour = random.randint(6, 22)
                    departure_minute = random.choice([0, 15, 30, 45])
                    base_departure_datetime = base_departure_datetime.replace(hour=departure_hour, minute=departure_minute, second=0, microsecond=0)

                    # 3. Calculate the *arrival datetime* based on the flight duration
                    flight_duration = datetime.timedelta(minutes=int(route['min']))
                    arrival_datetime = base_departure_datetime + flight_duration


                    # 4. Format the dates and times (ISO 8601 format)
                    departure_date = base_departure_datetime.strftime("%Y-%m-%d")
                    departure_time = base_departure_datetime.strftime("%H:%M")
                    arrival_date = arrival_datetime.strftime("%Y-%m-%d")
                    arrival_time = arrival_datetime.strftime("%H:%M")

                    # 5. Update the carrier_data dictionary
                    carrier_data['departure_date'] = departure_date
                    carrier_data['departure_time'] = departure_time
                    carrier_data['arrival_date'] = arrival_date
                    carrier_data['arrival_time'] = arrival_time
                    # Timezones are kept as they were, since those are location-based


    # Save the modified data
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, indent=4)



def main():
    randomize_dates('airline_routes_with_datetime.json', 'airline_routes_with_datetime.json')
    print("Randomized dates and saved to airline_routes_with_datetime.json")


if __name__ == '__main__':
    main()

# def add_seats_remaining(filename: str):
#     """
#     Adds a 'seats_remaining' field to each carrier in the routes of the JSON data,
#     modifying the file in-place.

#     Args:
#         filename: Path to the JSON file.
#     """

#     with open(filename, 'r+', encoding='utf-8') as f:  # Open in 'r+' mode
#         data = json.load(f)

#         for airport_iata, airport_data in data.items():
#             if 'routes' in airport_data:
#                 for route in airport_data['routes']:
#                     for carrier_data in route['carriers']:
#                         seats_remaining = random.randint(0, 15)
#                         carrier_data['seats_remaining'] = seats_remaining

#         f.seek(0)  # Rewind to the beginning of the file
#         json.dump(data, f, indent=4)  # Overwrite the file
#         f.truncate()  # Remove any remaining old content


# def main():
#     add_seats_remaining('airline_routes.json')
#     print("Modified airline_routes.json in place.")

# if __name__ == '__main__':
#     main()
