import altair as alt


def layered_bar_chart(df, title):
    return (
        alt.Chart(df)
        .mark_bar(opacity=0.7)
        .encode(
            x="date",
            y="count",
            color="type",
            order=alt.Order("type", sort="ascending"),
            tooltip=["count"],
        )
        .properties(title=title)
    )


def bar_chart(df):
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(x="date", y="recurring_users", tooltip=["recurring_users"])
        .properties(title="Recurring users within 7 days")
    )


def histogram(df):
    return (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("count", bin=alt.Bin(step=1), title="Number of results opened"),
            y=alt.Y("count()", title="Number of users"),
            tooltip="count()",
        )
        .properties(title="Users that have opened 2 or more results")
    )
