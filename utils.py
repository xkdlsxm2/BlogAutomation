import json


def print_response(res, indent=2):
    print(json.dumps(res.json(), indent=indent))
