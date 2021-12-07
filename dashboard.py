"""
# My first app
Here's our first attempt at using data to create a table:
"""
import altair as alt
import pandas as pd
import streamlit as st

from collections import Counter
from pymongo import MongoClient
from utils.charts import bar_chart
from utils.counts import get_requests_and_clicks_per_day


from utils.clicks import load_clickdata

client = MongoClient(**st.secrets["mongo"])
SEARCH = client.db.PRODUCTION.search
RESULTS = client.db.PRODUCTION.results



# Pull data from the collection.
# Uses st.cache to only rerun when the query changes or after 10 min.
def count_requests():
    return SEARCH.count_documents({"datetime": {"$exists": True}})




def count_new_requests(date):
    return SEARCH.count_documents({"datetime": {"$gte": date}})


def get_requests_per_day():
    queries = SEARCH.find({"datetime": {"$exists": True}}, {"datetime": 1})
    dates = [d["datetime"].strftime("%Y-%m-%d") for d in queries]
    counts = Counter(dates)
    return [[date, value] for date, value in counts.items()]




clickdata = load_clickdata(SEARCH, RESULTS)

n_requests = count_requests()
counts = get_requests_and_clicks_per_day(clickdata, SEARCH)


st.sidebar.write(f"Total number of requests: {n_requests}")
st.sidebar.write(f"Total number of results clicked: {len(clickdata)}")

alt_chart = bar_chart(counts)
st.altair_chart(alt_chart, use_container_width=True)
