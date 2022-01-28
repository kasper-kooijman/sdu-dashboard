import streamlit as st

from datetime import datetime, date, time
from pymongo import MongoClient

from utils import (
    charts,
    clicks_deduced,
    counts_deduced,
    text_search,
)

client = MongoClient(**st.secrets["mongo"])
SEARCH = client.db.PRODUCTION.search
RESULTS = client.db.PRODUCTION.results
STATISTICS = client.db.PRODUCTION.statistics


start_of_today = datetime.combine(date.today(), time())
# start_of_today = datetime.now() - timedelta(days=8)
# start_of_today = datetime.now()

clickdata_deduced = clicks_deduced.load_clickdata_deduced(STATISTICS)

doc_search_per_day = counts_deduced.get_requests_and_clicks_per_day(
    clickdata_deduced, SEARCH
)

text_search_per_day = text_search.get_requests_and_clicks_per_day(search=SEARCH)

clicks_per_user = counts_deduced.count_clicks_per_user(clickdata_deduced)
recurring_clicks_per_user = counts_deduced.count_clicks_per_user(
    clickdata_deduced, recurring_only=True
)

st.sidebar.write(f"Total number of requests: {counts_deduced.count_requests(SEARCH)}")
st.sidebar.write(f"Total number of results clicked: {len(clickdata_deduced)}")
st.sidebar.write(f"Total number of users: {len(clicks_per_user)}")
st.sidebar.write(
    f"Percentage of recurring users: {round(len(recurring_clicks_per_user)/len(clicks_per_user), 2)}"
)

st.sidebar.write(
    f"Requests today: {counts_deduced.count_new_requests(start_of_today, SEARCH)}"
)
st.sidebar.write(
    f"Results clicked today: {counts_deduced.get_clicks_today(clickdata_deduced, SEARCH)}"
)


# Bar chart of clicks and requests per day
alt_chart = charts.layered_bar_chart(
    doc_search_per_day,
    "Doc search requests and opened results per day.",
)
st.altair_chart(alt_chart, use_container_width=True)

alt_chart = charts.layered_bar_chart(
    text_search_per_day,
    "Text search requests and results opened per day.",
)
st.altair_chart(alt_chart, use_container_width=True)

alt_chart = charts.bar_chart(
    counts_deduced.get_weekly_recurring_users(clickdata_deduced)
)
st.altair_chart(alt_chart, use_container_width=True)
