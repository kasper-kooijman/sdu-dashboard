import json
import pandas as pd
import streamlit as st


from bson.json_util import loads, dumps
from datetime import datetime, timedelta
from pymongo import MongoClient

from .eclis import canonical_ecli

def load_clickdata(search: MongoClient, results: MongoClient):
    clickdata = load_clickdata_from_json()
    last_datetime = get_last_datetime(clickdata)
    clickdata = load_new_clicks(clickdata, last_datetime, search, results)
    write_clickdata_to_json(clickdata)
    return pd.DataFrame(clickdata)

def load_clickdata_from_json():
    with open("data/clicked_results.json", "r") as f:
        clickdata = loads(json.load(f))
    return clickdata

def write_clickdata_to_json(clickdata):
    with open("data/clicked_results.json", "w") as f:
        json.dump(dumps(clickdata), f)


def get_last_datetime(clickdata):
    return max(d["date"] for d in clickdata)


# @st.cache
def load_new_clicks(clickdata, datetime: datetime, search: MongoClient, results: MongoClient):
    """Adds all clickdata that occurred after <datetime> to <clickdata>

    Args:
        clickdata (List[Dict]): clickdata
        datetime (datetime): Last datetime in <clickdata>
        search (MongoClient): Search collection in MongoDB
        results (MongoClient): Results collection in MongoDB

    Returns:
        List[Dict]: Updated clickdata
    """
    queries = list(search.find({"datetime": {"$gte": datetime}}))
    print("N queries: ", len(queries))
    for index, query in enumerate(queries):
        if index % 100 == 0:
            print("Iteration ", index)
        user_id = query["user_id"]
        query_datetime = query["datetime"]
        query_delta = query["datetime"] + timedelta(minutes=15)
        search_results = results.rechtspraak.find_one({"reference": query["reference"]})
        if search_results:
            eclis = [canonical_ecli(result["document_id"]) for result in search_results["results"]]
            clicks = list(search.find({"$and": [
                {"user_id": user_id},
                {"query": {"$in": eclis}},
                {"datetime": {"$gte": query_datetime, "$lte": query_delta}},
            ]}))
            if clicks:
                new_clickdata = [{
                    "date": query["datetime"],
                    "query_reference": query["reference"],
                    "query": query["query"],
                    "result": click["query"],
                    "result_index": eclis.index(click["query"])
                } for click in clicks if eclis.index(click["query"]) < 20]
                clickdata.extend(new_clickdata)


    return clickdata
