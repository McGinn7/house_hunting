import json
import logging
import os

import pandas as pd

from amap import get_geo_code, get_trainsit_cost
from beike import BeiKe


def deal_position2geocode(positions=[], filepath="./cache/position2geocode.json"):
    position2geocode = {}
    if os.path.exists(filepath):
        try:
            position2geocode = json.load(open(filepath, "r"))
        except Exception as e:
            logging.error(e)

    for position in positions:
        if position not in position2geocode:
            geo_code = get_geo_code(position)
            if geo_code is None:
                logging.warn("failed to get geo code of {}".format(position))
            else:
                logging.debug("position = {}, geo_code = {}".format(position, geo_code))
                position2geocode[position] = geo_code

    json.dump(position2geocode, open(filepath, "w"))
    return position2geocode


def deal_transit_cost(
    origins, destinations, position2geocode, filepath="./cache/transit_cost.json"
):
    transit_cost = {}
    if os.path.exists(filepath):
        try:
            transit_cost = json.load(open(filepath, "r"))
        except Exception as e:
            logging.error(e)

    for origin in origins:
        if origin not in position2geocode:
            logging.error("location of origin({}) not found".format(origin))
            continue
        else:
            location_origin = position2geocode[origin]
        transit_cost_origin = transit_cost.setdefault(origin, dict())
        for destination in destinations:
            if destination not in position2geocode:
                logging.error(
                    "location of destination({}) not found".format(destination)
                )
                continue
            else:
                location_destination = position2geocode[destination]
            if destination not in transit_cost_origin:
                transit_cost_origin[destination] = get_trainsit_cost(
                    location_origin, location_destination
                )

    json.dump(transit_cost, open(filepath, "w"))
    return transit_cost


def save_houses_to_csv(houses, filepath="./houses.csv"):
    data = {}
    for house in houses:
        for key, value in house.items():
            data.setdefault(key, list()).append(value)

    df = pd.DataFrame(data)
    df.to_csv(filepath)
    print("save {} houses to {}".format(df.count(), filepath))


def work():
    origins = [
        "大钟寺地铁站",
        "国贸大厦A座",
    ]
    regions = [
        "chaoyang",
    ]
    condition = "sf1a2a3a4p1bp250ep450"

    house_list = []
    bk = BeiKe()

    for region in regions:
        region_houses = bk.query(region, condition)
        house_list.extend(region_houses)

    destinations = set()
    for house in house_list:
        destinations.add(house["position"])
    logging.info("#destinations = {}".format(len(destinations)))

    position2geocode = deal_position2geocode(destinations)
    transit_cost = deal_transit_cost(origins, destinations, position2geocode)

    for index, origin in enumerate(origins):
        transit_cost_origin = transit_cost.get(origin, {})
        for house in house_list:
            destination = house["position"]
            if destination in transit_cost_origin:
                for key, value in transit_cost_origin[destination].items():
                    house["{}_{}".format(key, index)] = value
            else:
                logging.warn("cost from {} to {} not found".format(origin, destination))

    for house in house_list:
        logging.debug(house)

    save_houses_to_csv(house_list)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    work()
    pass
