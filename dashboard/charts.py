import plotly.express as px


def revenue_trend(df):

    fig = px.line(
        df,
        x="month",
        y="revenue",
        markers=True,
        title="Monthly Revenue Trend"
    )

    return fig


def region_chart(df):

    fig = px.bar(
        df,
        x="region_name",
        y="revenue",
        title="Revenue By Region"
    )

    return fig


def segment_chart(df):

    fig = px.pie(
        df,
        names="segment_name",
        values="revenue",
        hole=0.5,
        title="Revenue By Segment"
    )

    return fig
