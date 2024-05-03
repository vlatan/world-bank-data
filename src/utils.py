import os
import requests
import pandas as pd
import altair as alt
import streamlit as st
from pandas import DataFrame
from dotenv import load_dotenv


load_dotenv()


@st.cache_data(show_spinner="Fetching data...")
def get_indicator_data(indicator: str) -> dict[str, DataFrame | str]:
    """Get data per indicator from World Bank."""

    page, pages, result = 0, 1, []
    API_BASE_URL = os.getenv("API_BASE_URL")
    COUNTRY_CODE = os.getenv("COUNTRY_CODE")

    indicator_data_api = f"{API_BASE_URL}/country/{COUNTRY_CODE}/indicator/{indicator}"

    while page < pages:

        page += 1

        response = requests.get(f"{indicator_data_api}?page={page}&format=json").json()
        pages, data = response[0]["pages"], response[1]

        result += [
            {key: value for key, value in item.items() if key in ["date", "value"]}
            for item in data
            if item.get("value") is not None
        ]

    indicator_info_api = f"{API_BASE_URL}/indicator/{indicator}?format=json"
    response = requests.get(indicator_info_api).json()[1][0]

    chart_data = pd.DataFrame(data=result)

    return {
        "title": response["name"],
        "description": response["sourceNote"],
        "chart_data": chart_data,
        "table": chart_data.set_index("date").transpose(),
    }


def write_indicator(indicator: str) -> None:
    """Write title, description, table and chart to page."""

    data = get_indicator_data(indicator)

    title, description = data["title"], data["description"]
    table, chart_data = data["table"], data["chart_data"]

    st.write(f"### {title}")
    st.write(description)
    st.dataframe(table)

    chart = alt.Chart(chart_data).mark_area(opacity=0.4).encode(x="date", y="value")
    st.altair_chart(chart, use_container_width=True)


def write_topic(title: str, indicators: list[str]) -> None:
    """Write all indicators from a topic."""

    st.title(title)
    for indicator in indicators:
        st.divider()
        write_indicator(indicator)
