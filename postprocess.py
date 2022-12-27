import os

import pandas as pd

region_cn = {
    "andingmen": "安定门",
    "anzhen1": "安贞",
    "aolinpikegongyuan11": "奥林匹克公园",
    "baiziwan": "百子湾",
    "beigongda": "北工大",
    "beiyuan2": "北苑",
    "cbd": "CBD",
    "changying": "常营",
    "chaoqing": "朝青",
    "chaoyanggongyuan": "朝阳公园",
    "chaoyangmenwai1": "朝阳门外",
    "chengshousi1": "成寿寺",
    "dashanzi": "大山子",
    "dawanglu": "大望路",
    "dingfuzhuang": "定福庄",
    "dongba": "东坝",
    "dongdaqiao": "东大桥",
    "dongzhimen": "东直门",
    "dougezhuang": "豆各庄",
    "fangzhuang1": "方庄",
    "fatou": "垡头",
    "ganluyuan": "甘露园",
    "gaobeidian": "高碑店",
    "gongti": "工体",
    "guangqumen": "广渠门",
    "guanzhuang": "管庄",
    "guozhan1": "国展",
    "hepingli": "和平里",
    "hongmiao": "红庙",
    "huanlegu": "欢乐谷",
    "huaweiqiao": "华威桥",
    "huixinxijie": "惠新西街",
    "jianguomenwai": "建国门外",
    "jianxiangqiao1": "健翔桥",
    "jinsong": "劲松",
    "jiuxianqiao": "酒仙桥",
    "liangmaqiao": "亮马桥",
    "lishuiqiao1": "立水桥",
    "madian1": "马甸",
    "mudanyuan": "牡丹园",
    "nanshatan1": "南沙滩",
    "nongzhanguan": "农展馆",
    "panjiayuan1": "潘家园",
    "sanlitun": "三里屯",
    "sanyuanqiao": "三元桥",
    "shaoyaoju": "芍药居",
    "shibalidian1": "十八里店",
    "shifoying": "石佛营",
    "shilibao": "十里堡",
    "shilihe": "十里河",
    "shoudoujichang1": "首都机场",
    "shuangjing": "双井",
    "shuangqiao": "双桥",
    "sihui": "四惠",
    "songjiazhuang": "宋家庄",
    "taiyanggong": "太阳宫",
    "tianshuiyuan": "甜水园",
    "tongzhoubeiyuan": "通州北苑",
    "tuanjiehu": "团结湖",
    "wangjing": "望京",
    "xiaohongmen": "小红门",
    "xibahe": "西坝河",
    "yansha1": "燕莎",
    "yayuncun": "亚运村",
    "yayuncunxiaoying": "亚运村小营",
    "zhaoyangqita": "朝阳其它",
    "zhongyangbieshuqu1": "中央别墅区",
}


def read_houses(dirpath):
    df_list = []

    dir_list = os.listdir(dirpath)
    for filename in dir_list:
        if filename.endswith("_houses.csv"):
            filepath = os.path.join(dirpath, filename)
            df = pd.read_csv(filepath)
            df_list.append(df)

    df = pd.concat(df_list)
    print(df.head())
    return df


def transform(df: pd.DataFrame):
    data = {
        "position": [],
        "total_price": [],
        "unit_price": [],
        "year": [],
        "floor": [],
        "area": [],
        "orientation": [],
        "layout": [],
        "description": [],
        "url": [],
        "公交_大钟寺": [],
        "驾车_大钟寺": [],
        "公交_国贸": [],
        "驾车_国贸": [],
        "region": [],
    }

    for _, row in df.iterrows():
        description = []
        for des in row["description"].split("|"):
            if "平米" in des:
                row["area"] = des.replace("平米", "")
            elif "层" in des:
                row["floor"] = des
            elif "东" in des or "西" in des or "南" in des or "北" in des:
                row["orientation"] = des
            elif "室" in des or "厅" in des:
                row["layout"] = des
            elif "年" in des:
                row["year"] = des.replace("年", "").replace("建", "")
            else:
                description.append(des)
        row["description"] = "|".join(description)

        try:
            row["total_price"] = float(row["total_price"].replace("万", ""))
        except:
            pass

        try:
            row["unit_price"] = row["unit_price"].replace("元/平", "")
            row["unit_price"] = float(row["unit_price"])
        except:
            pass

        try:
            row["area"] = float(row["area"])
        except:
            pass

        try:
            row["公交_大钟寺"] = row["transit_duration_大钟寺地铁站"]
            row["驾车_大钟寺"] = row["driving_duration_大钟寺地铁站"]
            row["公交_国贸"] = row["transit_duration_国贸大厦A座"]
            row["驾车_国贸"] = row["driving_duration_国贸大厦A座"]
        except:
            pass

        try:
            if row.get("region") in region_cn:
                row["region"] = region_cn[row["region"]]
        except:
            pass

        for key in data.keys():
            data[key].append(row.get(key, "?"))

    df = pd.DataFrame(data)
    df = df.sort_values(by=["position", "unit_price"])
    return df


def filter(df: pd.DataFrame):
    df = df.drop_duplicates()
    df = df[df["area"] >= 65]
    return df


def to_excel(df: pd.DataFrame, output_filepath="./output/area_houses.xlsx"):
    xlsx = pd.ExcelWriter(output_filepath)
    for area, houses in df.groupby("region"):
        houses.to_excel(xlsx, sheet_name=area)
    xlsx.close()


if __name__ == "__main__":
    df = read_houses("./output")
    df = transform(df)
    df = filter(df)
    to_excel(df)
    pass
