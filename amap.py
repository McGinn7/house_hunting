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
    else:
        distance = "?"
        duration = "?"

    logging.debug(
        "origin = {}, destination = {}, duration = {}s, distance = {}m, fee = {}rmb".format(
            loc_origin, loc_destination, duration, distance, taxi_cost
        )
    )
    result = {
        "duration": duration,
        "distance": distance,
        "fee": taxi_cost,
    }
    return result


def get_transit(loc_origin, loc_destination, city_code1="010", city_code2="010"):
    url = "https://restapi.amap.com/v5/direction/transit/integrated?parameters"
    params = {
        "key": AMAP_KEY,
        "origin": loc_origin,
        "destination": loc_destination,
        "city1": city_code1,
        "city2": city_code2,
        "AlternativeRoute": 1,
        "time": "9-00",
        "show_fields": "cost",
    }
    rsp = requests.get(url, params=params)
    if rsp and rsp.status_code == 200:
        data = rsp.json()
        if data["status"] == "1":
            return data
    return {}


def get_trainsit_cost(loc_origin, loc_destination, city_code1="010", city_code2="010"):
    transit_info = get_transit(loc_origin, loc_destination, city_code1, city_code2)
    route = transit_info.get("route", {})
    transits = route.get("transits", [])
    if len(transits) > 0:
        transit = transits[0]
        duration = transit.get("cost", {}).get("duration", "?")
        distance = transit.get("walking_distance", "?")
        transit_fee = transit.get("cost", {}).get("transit_fee", "?")
    else:
        duration = "?"
        distance = "?"
        transit_fee = "?"
    result = {
        "duration": duration,
        "distance": distance,
        "fee": transit_fee,
    }
    logging.debug(
        "origin = {}, destination = {}, duration = {}s, distance = {}m, fee = {}rmb".format(
            loc_origin,
            loc_destination,
            result["duration"],
            result["distance"],
            result["fee"],
        )
    )
    return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    get_trainsit_cost("116.343769,39.966839", "116.441727,39.968358")
    pass
