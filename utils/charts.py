import altair as alt

def bar_chart(df):
    return alt.Chart(df).mark_bar(opacity=0.7).encode(
        x="date",
        y="count",
        color="type",
        order=alt.Order(
            "type",
            sort="ascending"
        )
    )