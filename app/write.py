import pandas as pd
import altair as alt
import streamlit as st
from typing import Iterable

from .indicator import get_countries_data


def chart_data(
    indicator_id: str, data: Iterable[dict], country_codes: list[str]
) -> None:
    """Write slider, table and chart to page given the data and country codes."""

    # convert data to dataframe
    df = pd.DataFrame(data, country_codes)
    df = df.reindex(sorted(df.columns), axis=1)
    df.index.name = "Region"

    # display time range slider
    time_range = st.select_slider(
        label="Select range:",
        options=df.columns,
        value=(df.columns[0], df.columns[-1]),
        key=f"slider.{indicator_id}",
    )

    # choose the range of columns (years)
    df = df.loc[:, time_range[0] : time_range[1]]

    # write dataframe to page
    st.dataframe(df, use_container_width=True)

    # melt data to display on chart
    df = df.transpose().reset_index()
    df = pd.melt(df, id_vars=["index"]).rename(
        columns={"index": "Year", "value": "Value"}
    )

    chart = (
        alt.Chart(df)
        .mark_area(opacity=0.3)
        .encode(x="Year:T", y=alt.Y("Value:Q", stack=None), color="Region:N")
    )

    st.altair_chart(chart, use_container_width=True)


async def write_indicator(indicator_id: str, countries: dict[str, str]) -> None:
    """Write title, description, table and chart to page."""

    # check if default countries are a subset of the options
    default_countries = ["United States", "United Kingdom"]
    if not (set(default_countries) <= set(countries.keys())):
        default_countries = []

    # select a country from multiselect
    selected = st.multiselect(
        label="Select countries:",
        options=countries.keys(),
        default=default_countries,
        key=f"multiselect.{indicator_id}",
    )

    if not selected:
        st.error("Please select at least one country/region.")

    # include/exclude countries
    else:
        country_codes = {countries[cn] for cn in selected}
        result = await get_countries_data(indicator_id, country_codes)
        result = [item for item in result if item.get("data")]

        data = [item["data"] for item in result]
        chart_country_codes = {item["country_code"] for item in result}

        if (missing := country_codes - chart_country_codes) == country_codes:
            msg = f"Couldn't fetch and chart data for {", ".join(missing)} right now."
            st.error(msg)
            return

        elif missing:
            st.error(f"Couldn't fetch results for {", ".join(missing)} right now.")

        chart_data(indicator_id, data, list(chart_country_codes))
