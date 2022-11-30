import json
import logging

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


class BeiKe:
    def __init__(self) -> None:
        self.url_template = "https://bj.ke.com/ershoufang/{region}/{condition}/"
        self.house_key = {
            "position": "div[class='positionInfo']",
            "description": "div[class='houseInfo']",
            "total_price": "div[class='totalPrice totalPrice2']",
            "unit_price": "div[class='unitPrice']",
        }

    def query(self, region, condition):
        result = []

        page, num_page = 0, 1
        while page < num_page:
            page += 1
            logging.debug("page = {}, num_page = {}".format(page, num_page))
            _condition = "pg{}{}".format(page, condition)
            url = self.url_template.format(region=region, condition=_condition)
            logging.debug("url = {}".format(url))
            rsp = requests.get(url)
            if rsp.status_code == 200:
                html = BeautifulSoup(rsp.text, "html.parser")

                page_data = html.select_one(
                    "div[class='page-box house-lst-page-box']"
                ).get("page-data")
                num_page = json.loads(page_data).get("totalPage", 1)

                house_list = html.select("ul[class='sellListContent'] > li")
                for house in tqdm(house_list):
                    data = {}
                    is_valid_house = True
                    for key, selector in self.house_key.items():
                        ele = house.select_one(selector)
                        if ele is None:
                            is_valid_house = False
                            break
                        else:
                            value = (
                                str(ele.text).strip().replace(" ", "").replace("\n", "")
                            )
                        data[key] = value
                    if not is_valid_house:
                        continue

                    data["url"] = house.select_one("a").get("href")
                    logging.debug("data = {}".format(data))
                    result.append(data)
        return result


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    bk = BeiKe()
    house_list = bk.query("chaoyang", "sf1a2a3a4p1bp250ep450")
    for house in house_list:
        print(house)
    pass
