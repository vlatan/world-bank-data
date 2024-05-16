import asyncio
import random
import pandas as pd
import altair as alt
import streamlit as st
from typing import Iterable
from .indicator import Indicator
from .countries import Countries


async def get_indicators_info(indicator_ids: Iterable[str]) -> Iterable[dict]:
    """Concurrently get info (title and description) for each indicator."""

    indicators = [Indicator(indicator_id) for indicator_id in indicator_ids]
    coroutines = [asyncio.to_thread(indicator.get_info) for indicator in indicators]

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(coroutine) for coroutine in coroutines]

    return [task.result() for task in tasks]


async def get_countries_data(indicator_id: str, country_codes: Iterable[str]) -> list[dict]:
    """Concurrently get multiple countries data for a given indicator."""

    indicators = [Indicator(indicator_id, cc) for cc in country_codes]
    coros = [asyncio.to_thread(ind.get_data) for ind in indicators]
    
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(coro) for coro in coros]

    return [task.result() for task in tasks]


@st.cache_data(show_spinner=False)
def lookup_country_name(_countries: dict[str, str], code: str):
    for name, current_code in _countries.items():
        if code == current_code:
            return name


def chart_data(indicator_id: str, data: list[dict], country_codes: list[str]) -> None:
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
    st.dataframe(df)

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

    # select a country from multiselect
    selected = st.multiselect(
        label="Select countries:",
        options=countries.keys(),
        default=["United States", "China"],
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
        chart_country_codes = [item["country_code"] for item in result]

        if missing := set(country_codes) - set(chart_country_codes):
            st.error(f"Couldn't fetch results for {", ".join(missing)} right now.")

        chart_data(indicator_id, data, chart_country_codes)


async def write_topic(title: str, indicator_ids: list[str]) -> None:
    """Write all indicators from a topic."""

    # write topic title to page
    st.title(title)

    # get all countries
    countries = await Countries().get()

    # get titles and descriptions for every indicator
    indicator_infos = await get_indicators_info(indicator_ids)

    for indicator_id, indicator_info in zip(indicator_ids, indicator_infos):
        st.divider()
        # write title and desc to page
        st.write(f"### {indicator_info.get("title")}")
        st.write(indicator_info.get("description"))
        # write multiselect, table and chart
        await write_indicator(indicator_id, countries)
