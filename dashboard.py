"""
# My first app
Here's our first attempt at using data to create a table:
"""
import altair as alt
import pandas as pd
import streamlit as st

from collections import Counter
from datetime import datetime, date, time
from pymongo import MongoClient

from utils import charts, clicks, counts

client = MongoClient(**st.secrets["mongo"])
SEARCH = client.db.PRODUCTION.search
RESULTS = client.db.PRODUCTION.results



# Pull data from the collection.
# Uses st.cache to only rerun when the query changes or after 10 min.




def get_requests_per_day():
    queries = SEARCH.find({"datetime": {"$exists": True}}, {"datetime": 1})
    dates = [d["datetime"].strftime("%Y-%m-%d") for d in queries]
    counts = Counter(dates)
    return [[date, value] for date, value in counts.items()]



start_of_today = datetime.combine(date.today(), time())

clickdata = clicks.load_clickdata(SEARCH, RESULTS)
requests_and_clicks_per_day = counts.get_requests_and_clicks_per_day(clickdata, SEARCH)


st.sidebar.write(f"Total number of requests: {counts.count_requests(SEARCH)}")
st.sidebar.write(f"Total number of results clicked: {len(clickdata)}")

st.sidebar.write(f"Requests today: {counts.count_new_requests(start_of_today, SEARCH)}")
st.sidebar.write(f"Results clicked today: {counts.get_clicks_today(clickdata, SEARCH)}")

alt_chart = charts.bar_chart(requests_and_clicks_per_day)
st.altair_chart(alt_chart, use_container_width=True)
