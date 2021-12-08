import altair as alt

def bar_chart(df):
    return alt.Chart(df).mark_bar(opacity=0.7).encode(
        x="date",
        y="count",
        color="type",
        order=alt.Order(
            "type",
            sort="ascending"
        ),
        tooltip=["count"]
    )

def histogram(df):
    return alt.Chart(df).mark_bar().encode(
        x=alt.X("count", bin=alt.Bin(step=1), title="Number of results opend"),
        y=alt.Y('count()', title="Number of users")
    )