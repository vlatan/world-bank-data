import os
import requests
import pandas as pd
import altair as alt
import streamlit as st
from pandas import DataFrame
from dotenv import load_dotenv


load_dotenv()


@st.cache_data
def get_data(indicator: str) -> tuple[DataFrame, ...]:
    """Get data per indicator from World Bank."""

    page, pages, result = 0, 1, []
    API_BASE_URL = os.getenv("API_BASE_URL")
    api_endpoint = f"{API_BASE_URL}/{indicator}?format=json"

    while page < pages:

        page += 1

        response = requests.get(f"{api_endpoint}&page={page}").json()
        pages, data = response[0]["pages"], response[1]

        result += [
            {key: value for key, value in item.items() if key in ["date", "value"]}
            for item in data
            if item.get("value") is not None
        ]

    dataframe = pd.DataFrame(data=result)
    table = dataframe.set_index("date").transpose()

    return dataframe, table


def write_data(indicator: str, title: str, description: str | None = None) -> None:
    """Write title, description, table and chart to page."""

    st.write(f"### {title}")

    if description:
        st.write(description)

    df, table = get_data(indicator)

    st.dataframe(table)

    chart = alt.Chart(data=df).mark_area(opacity=0.4).encode(x="date", y="value")
    st.altair_chart(chart, use_container_width=True)
