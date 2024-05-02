import os
import re
import requests
import pandas as pd
import altair as alt
import streamlit as st
from pandas import DataFrame
from dotenv import load_dotenv


load_dotenv()


@st.cache_data
def get_indicator_data(indicator: str) -> dict[str, DataFrame | str]:
    """Get data per indicator from World Bank."""

    page, pages, result = 0, 1, []
    API_BASE_URL = os.getenv("API_BASE_URL")
    indicator_data_api = f"{API_BASE_URL}/country/mk/indicator/{indicator}?format=json"

    while page < pages:

        page += 1

        response = requests.get(f"{indicator_data_api}&page={page}").json()
        pages, data = response[0]["pages"], response[1]

        result += [
            {key: value for key, value in item.items() if key in ["date", "value"]}
            for item in data
            if item.get("value") is not None
        ]

    indicator_text_api = f"{API_BASE_URL}/indicator/{indicator}?format=json"
    response = requests.get(indicator_text_api).json()[1][0]

    chart_data = pd.DataFrame(data=result)

    return {
        "title": response["name"],
        "description": response["sourceNote"],
        "chart_data": chart_data,
        "table": chart_data.set_index("date").transpose(),
    }


def write_data(indicator: str) -> None:
    """Write title, description, table and chart to page."""

    data = get_indicator_data(indicator)

    title, description = data["title"], data["description"]
    table, chart_data = data["table"], data["chart_data"]

    st.write(f"### {title}")
    st.write(description)
    st.dataframe(table)

    chart = alt.Chart(chart_data).mark_area(opacity=0.4).encode(x="date", y="value")
    st.altair_chart(chart, use_container_width=True)
