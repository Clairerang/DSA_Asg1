import json
from airline_class import AirportDatabase  

def load_airport_data(file_path):
    data = read_json_file(file_path)
    return AirportDatabase(data)

def read_json_file(file_path):
    """
    Reads a JSON file and returns the data as a Python dictionary or list.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict or list:   The JSON data as a Python dictionary or list,
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

# Initialize globally so all pages can import it
airport_db = load_airport_data('airline_routes.json')
