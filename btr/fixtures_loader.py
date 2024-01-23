import json
import os


def load_json(file: str) -> dict:
    """

    :param file: string with path to fixture [str]
    :return: object dictionary [dict]
    """
    with open(os.path.abspath(f'btr/fixtures/{file}'), 'r') as f:
        return json.loads(f.read())
