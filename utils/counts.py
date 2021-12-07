import pandas as pd

from collections import Counter
from datetime import datetime
from pymongo.mongo_client import MongoClient

def get_requests_and_clicks_per_day(clickdata: pd.DataFrame, search: MongoClient):
    clicks_per_day = dict(Counter(clickdata["date"]))
    requests_per_day = get_requests_per_day(search)

    clicks_per_day = counter_to_list(clicks_per_day, "clicks")
    requests_per_day = counter_to_list(requests_per_day, "requests")

    clicks_per_day.extend(requests_per_day)
    return pd.DataFrame(clicks_per_day)

def get_clicks_today(clickdata: pd.DataFrame, search: MongoClient):
    cpd = get_requests_and_clicks_per_day(clickdata, search)
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        return int(cpd[(cpd["date"]==today) & (cpd["type"]=="clicks")]["count"])
    except TypeError as e:
        print(e)
        return 0

def counter_to_list(counts: dict, type_: str):
    return [
        {
            "date": date,
            "type": type_,
            "count": count,
        }
        for date, count in counts.items()
    ]


def get_requests_per_day(search: MongoClient):
    queries = search.find({"datetime": {"$exists": True}}, {"datetime": 1})
    dates = [d["datetime"].strftime("%Y-%m-%d") for d in queries]
    return dict(Counter(dates))

def count_requests(search: MongoClient):
    return search.count_documents({"datetime": {"$exists": True}})

def count_new_requests(date, search: MongoClient):
    return search.count_documents({"datetime": {"$gte": date}})

