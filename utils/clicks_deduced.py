import pandas as pd

from pymongo import MongoClient


def load_clickdata_deduced(statistics: MongoClient):
    clickdata = load_clickdata_from_mongo(statistics)
    return pd.DataFrame(clickdata)


def load_clickdata_from_mongo(statistics: MongoClient):
    clickdata = list(statistics.find({}))
    return return_unique(clickdata)


def return_unique(clickdata):
    seen = set()
    unique_clickdata = []
    for click in clickdata:
        cd = (
            click["date"],
            click["query_reference"],
            click["query"],
            click["result"],
            click["result_index"],
        )
        if cd not in seen:
            seen.add(cd)
            unique_clickdata.append(click)
    return unique_clickdata
