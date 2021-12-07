import json
import pandas as pd
import streamlit as st


from bson.json_util import loads, dumps
from datetime import date, datetime, timedelta
from pymongo import MongoClient

from .eclis import canonical_ecli

def load_clickdata(search: MongoClient, results: MongoClient):
    clickdata = load_clickdata_from_json()
    # dt = datetime.combine(date.today(), datetime.min.time())
    dt = datetime.now() - timedelta(days=7)
    clickdata = load_new_clicks(clickdata, dt, search, results)
    write_clickdata_to_json(clickdata)
    return pd.DataFrame(clickdata)

def load_clickdata_from_json():
    with open("data/clicked_results.json", "r") as f:
        clickdata = loads(json.load(f))
    return clickdata

def write_clickdata_to_json(clickdata):
    with open("data/clicked_results.json", "w") as f:
        json.dump(dumps(clickdata), f)



# @st.cache
def load_new_clicks(clickdata, dt: datetime, search: MongoClient, results: MongoClient):
    """Adds all clickdata that occurred after <datetime> to <clickdata>

    Args:
        clickdata (List[Dict]): clickdata
        datetime (datetime): Last datetime in <clickdata>
        search (MongoClient): Search collection in MongoDB
        results (MongoClient): Results collection in MongoDB

    Returns:
        List[Dict]: Updated clickdata
    """
    queries = list(search.find({"datetime": {"$gte": dt}}))
    print("Datetime: ", dt)
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
                    "date": query["datetime"].strftime("%Y-%m-%d"),
                    "query_reference": query["reference"],
                    "query": query["query"],
                    "result": click["query"],
                    "result_index": eclis.index(click["query"])
                } for click in clicks if eclis.index(click["query"]) < 20]
                clickdata.extend(new_clickdata)


    return return_unique(clickdata)


def return_unique(clickdata):
    seen = set()
    unique_clickdata = []
    for click in clickdata:
        cd = (click["date"], click["query_reference"], click["query"], click["result"], click["result_index"])
        if cd not in seen:
            seen.add(cd)
            unique_clickdata.append(click)
    return unique_clickdata