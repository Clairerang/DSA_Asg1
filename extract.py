import json

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


def extract_and_sort_airport_names(json_file_path):
    """
    Reads a JSON file, extracts the airport names, sorts them alphabetically, and returns the sorted list.

    Args:
        json_file_path (str): The path to the JSON file.  The JSON is assumed to be a dictionary where keys are airport codes
                              and values are dictionaries containing airport information, including 'name'.

    Returns:
        list: A list of sorted airport names, or None if an error occurred during file reading or name extraction.
    """
    data = read_json_file(json_file_path)

    if data is None:
        return None  # Error already handled in read_json_file

    airport_names = []
    try:
        for airport_code, airport_data in data.items():
            airport_names.append(airport_data['name'])  # Assuming the airport name is stored under the 'name' key
    except KeyError as e:
        print(f"Error: Missing 'name' key in airport data: {e}")
        return None
    except Exception as e:
        print(f"Error during airport name extraction: {e}")
        return None

    airport_names.sort()  # Sort the list in place
    return airport_names


# Example usage:
if __name__ == "__main__":
    file_path = 'airline_routes.json'  # Replace with the actual path to your JSON file
    sorted_airport_names = extract_and_sort_airport_names(file_path)

    if sorted_airport_names:
        print("Sorted Airport Names:")
        for name in sorted_airport_names:
            print(name)
    else:
        print("Failed to extract and sort airport names, or no airport names were found.")