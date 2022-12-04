import json
import logging
import os

import pandas as pd
from tqdm import tqdm

from amap import get_driving_cost, get_geo_code, get_trainsit_cost
from beike import BeiKe


def deal_position2geocode(positions=[], filepath="./cache/position2geocode.json"):
    logging.info("[deal_position2geocode] #positions = {}".format(len(positions)))
    position2geocode = {}
    if os.path.exists(filepath):
        try:
            position2geocode = json.load(open(filepath, "r"))
        except Exception as e:
            logging.error(e)

    for position in tqdm(positions):
        if position not in position2geocode:
            geo_code = get_geo_code(position)
            if geo_code is None:
                logging.warning("failed to get geo code of {}".format(position))
            else:
                logging.debug("position = {}, geo_code = {}".format(position, geo_code))
                position2geocode[position] = geo_code

    json.dump(position2geocode, open(filepath, "w"))
    return position2geocode


def deal_traffic_cost(origins, destinations, position2geocode, cost_func, filepath):
    transit_cost = {}
    if os.path.exists(filepath):
        try:
            transit_cost = json.load(open(filepath, "r"))
        except Exception as e:
            logging.error(e)

    for origin in origins:
        if origin not in tqdm(position2geocode):
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
                transit_cost_origin[destination] = cost_func(
                    location_origin, location_destination
                )

    json.dump(transit_cost, open(filepath, "w"))
    return transit_cost


def save_houses_to_csv(houses, filepath="./houses.csv"):
    num_key = max([len(house) for house in houses])
    data = {}
    for house in houses:
        if len(house) == num_key:
            for key, value in house.items():
                data.setdefault(key, list()).append(value)

    df = pd.DataFrame(data)
    df.to_csv(filepath)
    logging.info("save {} houses to {}".format(df.count(), filepath))


def work():
    origins = [
        "大钟寺地铁站",
        "国贸大厦A座",
    ]
    regions = [
        "chaoyang",
    ]
    condition = "sf1a1a2a3a4p1p2p3p4p5"

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
    traffic_mode = {
        "transit": get_trainsit_cost,
        "driving": get_driving_cost,
    }
    for traffic, cost_func in traffic_mode.items():
        traffic_cost = deal_traffic_cost(
            origins,
            destinations,
            position2geocode,
            cost_func,
            "./cache/{}_cost.json".format(traffic),
        )
        for origin in origins:
            traffic_cost_origin = traffic_cost.get(origin, {})
            for house in house_list:
                destination = house["position"]
                if destination in traffic_cost_origin:
                    for key, value in traffic_cost_origin[destination].items():
                        house["{}_{}_{}".format(traffic, key, origin)] = value
                else:
                    logging.warning(
                        "cost from {} to {} in {} not found".format(
                            origin, destination, traffic
                        )
                    )

    for house in house_list:
        logging.debug(house)

    save_houses_to_csv(house_list)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    work()
    pass
