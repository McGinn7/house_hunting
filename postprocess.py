import os
import pandas as pd


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
