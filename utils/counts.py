import pandas as pd

from collections import Counter
from datetime import datetime, time, timedelta
from pymongo.mongo_client import MongoClient

def get_requests_and_clicks_per_day(clickdata: pd.DataFrame, search: MongoClient):
    click_dates = [cd.strftime("%Y-%m-%d") for cd in clickdata["date"]]
    clicks_per_day = dict(Counter(click_dates))
    requests_per_day = get_requests_per_day(search)

    clicks_per_day = counter_to_list(clicks_per_day, "clicks")
    requests_per_day = counter_to_list(requests_per_day, "requests")

    clicks_per_day.extend(requests_per_day)
    return pd.DataFrame(clicks_per_day)

def get_clicks_today(clickdata: pd.DataFrame, search: MongoClient):
    cpd = get_requests_and_clicks_per_day(clickdata, search)
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        return int(cpd[(cpd["date"]==today) & (cpd["type"]=="clicks")]["count"])
    except TypeError as e:
        print(e)
        return 0

def counter_to_list(counts: dict, type_: str):
    return [
        {
            "date": date,
            "type": type_,
            "count": count,
        }
        for date, count in counts.items()
    ]


def count_clicks_per_user(clickdata: pd.DataFrame, recurring_only: bool = False):
    clicks_per_user = pd.DataFrame(clickdata.groupby(["user_id"]).size()).reset_index().rename(columns={0: "count"})
    if recurring_only:
        return clicks_per_user[clicks_per_user["count"]>1]
    return clicks_per_user

def get_requests_per_day(search: MongoClient):
    queries = search.find({"datetime": {"$exists": True}}, {"datetime": 1})
    dates = [d["datetime"].strftime("%Y-%m-%d") for d in queries]
    return dict(Counter(dates))

def count_requests(search: MongoClient):
    return search.count_documents({"datetime": {"$exists": True}})

def count_new_requests(date, search: MongoClient):
    return search.count_documents({"datetime": {"$gte": date}})

def get_weekly_recurring_users(clickdata: pd.DataFrame):
    start_date = min(clickdata["date"]) - timedelta(days=7)
    start_date = datetime.combine(start_date, time())
    dates = pd.date_range(start_date,datetime.today()-timedelta(days=7),freq='d')
    recurring_users = []
    for date in dates:
        end_date = date + timedelta(days=7)
        end_date = end_date.strftime("%Y-%m-%d")
        counts = {
            "date": end_date,
            "recurring_users": get_number_of_recurring_users_in_a_week(date, clickdata)
        }
        recurring_users.append(counts)
    return pd.DataFrame(recurring_users)



def get_number_of_recurring_users_in_a_week(start_date: datetime, clickdata: pd.DataFrame):
    end_date = start_date + timedelta(days=7)
    weekly_interval = clickdata[(clickdata["date"]>start_date) & (clickdata["date"]<end_date)]
    weekly_interval["datestr"] = [cd.strftime("%Y-%m-%d") for cd in weekly_interval["date"]]
    counts = weekly_interval.groupby(["user_id", "datestr"]).size()
    counts = Counter(counts.reset_index()["user_id"])
    return len({k:v for k,v in counts.items() if v>1})