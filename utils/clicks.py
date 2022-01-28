import pandas as pd

from collections import Counter
from datetime import datetime
from pymongo import MongoClient

from .counts_deduced import counter_to_list





def get_requests_and_clicks_per_day(
    type_, clickdata: pd.DataFrame, search: MongoClient
):
    click_dates = [cd.strftime("%Y-%m-%d") for cd in clickdata["datetime"]]
    clicks_per_day = dict(Counter(click_dates))
    requests_per_day = get_requests_per_day(type_, search)

    clicks_per_day = counter_to_list(clicks_per_day, "clicks")
    requests_per_day = counter_to_list(requests_per_day, "requests")

    clicks_per_day.extend(requests_per_day)
    return pd.DataFrame(clicks_per_day)


def get_clicks_today(clickdata: pd.DataFrame, search: MongoClient):
    cpd = get_requests_and_clicks_per_day(clickdata, search)
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        return int(cpd[(cpd["date"] == today) & (cpd["type"] == "clicks")]["count"])
    except TypeError as e:
        print(e)
        return 0


def get_requests_per_day(type_: str, search: MongoClient):
    queries = search.find(
        {"sent_from": {"$exists": True}, "type_": type_}, {"datetime": 1}
    )
    dates = [d["datetime"].strftime("%Y-%m-%d") for d in queries]
    return dict(Counter(dates))


def return_unique(clickdata):
    seen = set()
    unique_clickdata = []
    for click in clickdata:
        cd = (
            click["datetime"],
            click["reference"],
            click["query"],
        )
        if cd not in seen:
            seen.add(cd)
            unique_clickdata.append(click)
    return unique_clickdata
