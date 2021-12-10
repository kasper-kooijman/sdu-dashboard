"""
# My first app
Here's our first attempt at using data to create a table:
"""
import altair as alt
import pandas as pd
import streamlit as st

from collections import Counter
from datetime import datetime, timedelta, date, time
from pymongo import MongoClient

from utils import charts, clicks, counts

client = MongoClient(**st.secrets["mongo"])
SEARCH = client.db.PRODUCTION.search
RESULTS = client.db.PRODUCTION.results
STATISTICS = client.db.PRODUCTION.statistics



start_of_today = datetime.combine(datetime.now(), time())

clickdata = clicks.load_clickdata(SEARCH, RESULTS, STATISTICS)
requests_and_clicks_per_day = counts.get_requests_and_clicks_per_day(clickdata, SEARCH)
clicks_per_user = counts.count_clicks_per_user(clickdata)
recurring_clicks_per_user = counts.count_clicks_per_user(clickdata, recurring_only=True)

st.sidebar.write(f"Total number of requests: {counts.count_requests(SEARCH)}")
st.sidebar.write(f"Total number of results clicked: {len(clickdata)}")
st.sidebar.write(f"Total number of users: {len(clicks_per_user)}")
st.sidebar.write(f"Percentage of recurring users: {round(len(recurring_clicks_per_user)/len(clicks_per_user), 2)}")

st.sidebar.write(f"Requests today: {counts.count_new_requests(start_of_today, SEARCH)}")
st.sidebar.write(f"Results clicked today: {counts.get_clicks_today(clickdata, SEARCH)}")


# Bar chart of clicks and requests per day
alt_chart = charts.layered_bar_chart(requests_and_clicks_per_day)
st.altair_chart(alt_chart, use_container_width=True)

alt_chart = charts.bar_chart(counts.get_weekly_recurring_users(clickdata))
st.altair_chart(alt_chart, use_container_width=True)

# Histogram of clicks per user
hist = charts.histogram(recurring_clicks_per_user)
st.altair_chart(hist, use_container_width=True)
