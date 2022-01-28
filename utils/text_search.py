import pandas as pd

from collections import Counter
from pymongo import MongoClient


def load_clickdata(type_: str, search: MongoClient):
    clickdata = search.find(
        {
            "sent_from": {"$exists": True},
            "type_": type_,
        }
    )
    return pd.DataFrame(clickdata)


def load_text_search_results(search: MongoClient):
    clickdata = search.find({"sent_from": "text_search_result"})
    return pd.DataFrame(clickdata)


def get_requests_and_clicks_per_day(search: MongoClient):
    requests = load_clickdata("text", search)
    clicks = load_text_search_results(search)

    request_dates = [cd.strftime("%Y-%m-%d") for cd in requests["datetime"]]
    click_dates = [cd.strftime("%Y-%m-%d") for cd in clicks["datetime"]]

    requests_per_day = counter_to_list(dict(Counter(request_dates)), "requests")
    clicks_per_day = counter_to_list(dict(Counter(click_dates)), "clicks")
    clicks_per_day.extend(requests_per_day)
    return pd.DataFrame(clicks_per_day)


def counter_to_list(counts: dict, type_: str):
    return [
        {
            "date": date,
            "type": type_,
            "count": count,
        }
        for date, count in counts.items()
    ]
