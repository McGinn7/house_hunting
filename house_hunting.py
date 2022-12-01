import logging

from beike import BeiKe
from amap import get_geo_code, get_trainsit_cost


def work():
    origins = [
        "116.343769,39.966839",  # 大钟寺地铁站
        "116.458313,39.912160",  # 国贸大厦A座
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

    position2geocode = {}
    for position in destinations:
        geo_code = get_geo_code(position)
        if geo_code is None:
            logging.warn("failed to get geo code of {}".format(position))
        else:
            logging.debug("position = {}, geo_code = {}".format(position, geo_code))
            position2geocode[position] = geo_code

    cost_info = {}

    for house in house_list:
        destination = position2geocode.get(house["position"])
        for index, origin in enumerate(origins):
            location_pair = (origin, destination)
            if location_pair not in cost_info:
                cost_info[location_pair] = get_trainsit_cost(origin, destination)
            cost = cost_info.get(location_pair, {})
            for key, value in cost.items():
                house["{}_{}".format(key, index)] = value

    for house in house_list:
        print(house)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    work()
    pass
