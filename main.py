import requests

AMAP_KEY = "055eb143f76c06cad04890b0d396090e"


def test_geo_code(address, city="beijing"):
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


if __name__ == "__main__":
    addr = "北京朝阳西坝河北里202号院8号楼"
    loc = test_geo_code(addr)
    print("address = {}, location = {}".format(addr, loc))    
    pass
