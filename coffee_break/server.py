import json
import subprocess
import sys

import pymongo
from flask import Flask, render_template, request

from geocoding_tools import find_starbucks_around, \
    convert_address_to_geocoding

app = Flask(__name__, static_url_path='')

GEO_API_KEY_FILE = "positionstack.key"


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/get_starbucks_around')
def get_starbucks_around():
    """
    Find all starbucks around radius from.
    """
    request_arguments = request.args
    try:
        parsed_args = parse_starbucks_around_args(request_arguments)
    except ValueError:
        return "Content not Found", 400

    answer = find_starbucks_around(
        col, parsed_args[0], parsed_args[1], parsed_args[2])
    return json.dumps(answer)


def parse_starbucks_around_args(request_arguments) -> tuple[int, int, int]:
    """
    Parse all given params
    :param request_arguments - dictionary of all params given from user.
        keys:
        # address - Full address or `latitude, longitude`
        # radius - size of radius (in numbers)
        # address_type - full_address or coordinates
    """
    if request_arguments["address_type"] == "full_address":
        with open(GEO_API_KEY_FILE, "r") as apikey_file:
            api_key = apikey_file.read()

        answer = convert_address_to_geocoding(
            request_arguments["address"], api_key)
        latitude = answer[0]
        longitude = answer[1]
    else:
        latitude, longitude = request_arguments["address"].replace(" ", ""
                                                                   ).split(",")
    try:
        return int(latitude), int(longitude), int(request_arguments["radius"])
    except Exception:
        raise ValueError()


if __name__ == '__main__':
    args = sys.argv
    subprocess.call(
        "./import_starbucks_stores.sh " + args[1] + " " + args[2],
        shell=True
    )
    my_client = pymongo.MongoClient("mongodb://localhost:27017/")
    mydb = my_client[args[1]]
    col = mydb[args[2]]
    app.run(port=8000, debug=True)
