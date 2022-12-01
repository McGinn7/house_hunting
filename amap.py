import logging
import requests

AMAP_KEY = "055eb143f76c06cad04890b0d396090e"


def get_geo_code(address, city="beijing"):
    url = "https://restapi.amap.com/v3/geocode/geo?parameters"
    params = {
        "key": AMAP_KEY,
        "address": address,
        "city": city,
    }
    rsp = requests.get(url, params)
    if rsp.status_code == 200:
        geocodes = rsp.json().get("geocodes", [])
        if len(geocodes) == 0:
            return None
        location = geocodes[0].get("location")
        return location
    return None


def get_driving(loc_origin, loc_destination):
    url = "https://restapi.amap.com/v5/direction/driving?parameters"
    params = {
        "key": AMAP_KEY,
        "origin": loc_origin,
        "destination": loc_destination,
        "show_fields": "cost",
    }
    rsp = requests.post(url, params=params)
    if rsp and rsp.status_code == 200:
        data = rsp.json()
        if data["status"] == "1":
            return data
    return {}


def get_driving_cost(loc_origin, loc_destination):
    driving_info = get_driving(loc_origin, loc_destination)
    route = driving_info.get("route", {})
    taxi_cost = route.get("taxi_cost", "?")
    paths = route.get("paths", [])
    if len(paths) > 0:
        path = paths[0]
        distance = path.get("distance", "?")
        duration = path.get("cost", {}).get("duration", "?")
        if duration != "?":
            duration = "{:.1f}".format(float(duration) / 60)
    else:
        distance = "?"
        duration = "?"

    logging.debug(
        "origin = {}, destination = {}, duration = {}min, distance = {}m, taxi_cost = {}rmb".format(
            loc_origin, loc_destination, duration, distance, taxi_cost
        )
    )
    result = {
        "duration": duration,
        "distance": distance,
        "taxi_cost": taxi_cost,
    }
    return result


if __name__ == "__main__":
    pass
