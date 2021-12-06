"""
# My first app
Here's our first attempt at using data to create a table:
"""
import json
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from bson.json_util import loads, dumps
from collections import Counter
from datetime import datetime
from pymongo import MongoClient

from utils import canonical_ecli

client = MongoClient(**st.secrets["mongo"])
SEARCH = client.db.PRODUCTION.search
RESULTS = client.db.PRODUCTION.results

with open("data/clicked_results.json", "r") as f:
    clicked_results = loads(json.load(f))

# Pull data from the collection.
# Uses st.cache to only rerun when the query changes or after 10 min.
def count_requests():
    return SEARCH.count_documents({"datetime": {"$exists": True}})


def get_last_datetime(clicked_results):
    return max(d["query"]["datetime"] for d in clicked_results)


def count_new_requests(date):
    return SEARCH.count_documents({"datetime": {"$gte": date}})


def get_requests_per_day():
    queries = SEARCH.find({"datetime": {"$exists": True}}, {"datetime": 1})
    dates = [d["datetime"].strftime("%Y-%m-%d") for d in queries]
    counts = Counter(dates)
    return [[date, value] for date, value in counts.items()]


@st.cache
def get_new_requests(clicked_results, datetime):
    queries = list(SEARCH.find({"datetime": {"$gte": datetime}}))
    print("N queries: ", len(queries))
    for index, query in enumerate(queries):
        if index % 10 == 0:
            print("Iteration ", index)
        user_id = query["user_id"]
        res = RESULTS.rechtspraak.find_one({"reference": query["reference"]})
        if res:
            top_3 = res["results"][:3]
            for top_3_result in top_3:
                document_id = top_3_result["document_id"]
                clicked_on = SEARCH.find_one(
                    {"user_id": user_id, "query": canonical_ecli(document_id)}
                )
                if clicked_on:
                    clicked_results.append({"query": query, "result": clicked_on})
    return clicked_results


n_requests = count_requests()
last_datetime = get_last_datetime(clicked_results)
clicked_results = get_new_requests(clicked_results, last_datetime)
dates, counts = zip(*get_requests_per_day())
df = (
    pd.DataFrame({"date": dates, "counts": counts})
    .rename(columns={"date": "index"})
    .set_index("index")
)

with open("data/clicked_results.json", "w") as f:
    json.dump(dumps(clicked_results), f)

st.sidebar.write(f"Total number of requests: {n_requests}")
st.sidebar.write(f"Total number of results clicked: {len(clicked_results)}")
st.sidebar.write(
    f"New requests since last updated: {count_new_requests(last_datetime)}"
)

st.bar_chart(df)
