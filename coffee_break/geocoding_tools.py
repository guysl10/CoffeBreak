import json
from typing import Tuple, List, Dict

import requests

GEOCODING_REQEUST = (
    "http://api.positionstack.com/v1/forward?access_key={api_key}&query={"
    "address}&output=json"
)


def convert_address_to_geocoding(
        full_address: str, api_key: str) -> Tuple[str, str]:
    """
    Reach partial address from given full address with PositionStack API.
    :param api_key: key for requesting the server coordinates according to
                    given full address.
    """
    geo_data = requests.get(
        GEOCODING_REQEUST.format(api_key=api_key, address=full_address))
    if geo_data.status_code != 200:
        raise ValueError(geo_data.content)

    geo_data = json.loads(geo_data.content)
    latitude = geo_data["data"][0]["latitude"]
    longitude = geo_data["data"][0]["longitude"]

    return latitude, longitude


def find_starbucks_around(
        collection, latitude: int, longitude: int, radius: int) -> List[Dict]:
    """
    First Ask the db for all stores in the triangle around the coordinates and
    from the response find all stores in radius of given coordinate.

    :note: I ask the db for all stores in triangle around given dot and not
    radius because it's more fast to query the db about indexing O(1)
    instead of calculating all distances in the query O(n).
    :param collection: DB collection for querying the db.
    """
    radius = abs(radius)
    starbucks_around = []

    starbuckses = list(collection.find({"$and": [
        {"Latitude": {"$lt": latitude + radius}},
        {"Latitude": {"$gt": latitude - radius}},
        {"Longitude": {"$gt": longitude - radius}},
        {"Longitude": {"$lt": longitude + radius}}
    ]}, {"_id": 0, "Latitude": 1, "Longitude": 1, "StarbucksId": 1}))

    for starbucks in starbuckses:
        distance = ((
                            (starbucks["Longitude"] - longitude) ** 2 +
                            (starbucks["Latitude"] - latitude) ** 2)
                    ** 0.5)
        if distance <= radius:
            starbucks["distance"] = distance
            starbucks_around.append(starbucks)

    return starbucks_around
