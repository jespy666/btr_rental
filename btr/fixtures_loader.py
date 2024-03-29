import json
import os


def load_json(file: str) -> dict:
    """
    Load JSON data from a file.

    Args:
        file (str): The path to the JSON file.

    Returns:
        dict: The loaded JSON data as a dictionary.
    """
    with open(os.path.abspath(f'btr/fixtures/{file}'), 'r') as f:
        return json.loads(f.read())
