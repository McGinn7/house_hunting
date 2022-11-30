import requests
from bs4 import BeautifulSoup


class BeiKe:
    def __init__(self) -> None:
        self.url_template = "https://bj.ke.com/ershoufang/{region}/{condition}/"
        self.house_key = {
            "position": "div[class='positionInfo']",
            "description": "div[class='houseInfo']",
            "total_price": "div[class='totalPrice totalPrice2']",
            "unit_price": "div[class='unitPrice']",
        }
        pass

    def query(self, region, condition):
        url = self.url_template.format(region=region, condition=condition)
        rsp = requests.get(url)
        html = BeautifulSoup(rsp.text, "html.parser")
        house_list = html.select("ul[class='sellListContent'] > li")
        for index, house in enumerate(house_list):
            data = {}
            for key, selector in self.house_key.items():
                ele = house.select_one(selector)
                if ele is None:
                    value = "?"
                else:
                    value = str(ele.text).strip().replace(" ", "").replace("\n", "")
                data[key] = value

            url = house.select_one("a").get("href")
            print(
                "index = {}, pos = {}, desc = {}, total_price = {}, unit_price = {}".format(
                    index,
                    data["position"],
                    data["description"],
                    data["total_price"],
                    data["unit_price"],
                )
            )
            pass

    pass


if __name__ == "__main__":
    bk = BeiKe()
    bk.query("chaoyang", "a2a3a4bp250ep450rs13")
    pass
