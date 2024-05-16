import asyncio
import random
import pandas as pd
import altair as alt
import streamlit as st
from typing import Iterable
from .indicator import Indicator
from .countries import Countries


async def get_indicators(indicator_ids: list[str]) -> list[dict]:
    """Get indicators data concurrently."""

    async with asyncio.TaskGroup() as tg:
        indicators = [Indicator(iid) for iid in indicator_ids]
        coros = [asyncio.to_thread(ind.get) for ind in indicators]
        tasks = [tg.create_task(coro) for coro in coros]

    return [task.result() for task in tasks]


async def get_countries_data(
    country_codes: Iterable[str], indicator_id: str
) -> list[dict]:
    """Concurrently get multiple countries data for a given indicator."""

    async with asyncio.TaskGroup() as tg:
        indicators = [Indicator(indicator_id, cc) for cc in country_codes]
        coros = [asyncio.to_thread(ind.get) for ind in indicators]
        tasks = [tg.create_task(coro) for coro in coros]

    return [task.result() for task in tasks]


@st.cache_data(show_spinner=False)
def lookup_country_name(_countries: dict[str, str], code: str):
    for name, current_code in _countries.items():
        if code == current_code:
            return name


def chart_data(title: str, data: list[dict], country_codes: list[str]) -> None:
    """Write slider, table and chart to page given the data and country codes."""

    # convert data to dataframe
    df = pd.DataFrame(data, country_codes)
    df = df.reindex(sorted(df.columns), axis=1)
    df.index.name = "Region"

    # display time range slider
    time_range = st.select_slider(
        label="Select a range:",
        options=df.columns,
        value=(df.columns[0], df.columns[-1]),
        key=f"slider.{title.lower()}",
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


def write_indicator(indicator: dict) -> None:
    """Write title, description, table and chart to page."""

    indicator_id = indicator["id"]
    title = indicator["title"]
    description = indicator["description"]

    # get all countries
    countries = Countries().get()
    default_country_code = indicator["country_code"]
    default_country_name = lookup_country_name(countries, default_country_code)
    default_data = indicator["data"]

    # write title and desc to page
    st.write(f"### {title}")
    st.write(description)

    # select a country from multiselect
    selected = st.multiselect(
        label="Choose countries",
        options=countries.keys(),
        default=[default_country_name],
        key=f"multiselect.{title.lower()}",
    )

    if not selected:
        st.error("Please select at least one country/region.")

    # default country on first load
    elif len(selected) == 1 and selected[0] == default_country_name:
        chart_data(title, [default_data], [default_country_code])

    # include/exclude countries
    else:
        country_codes = {countries[cn] for cn in selected}
        result = asyncio.run(get_countries_data(country_codes, indicator_id))
        result = [item for item in result if item.get("data")]

        data = [item["data"] for item in result]
        chart_country_codes = [item["country_code"] for item in result]

        if missing := set(country_codes) - set(chart_country_codes):
            st.error(f"Couldn't fetch results for {", ".join(missing)} right now.")

        chart_data(title, data, chart_country_codes)


def write_topic(title: str, indicator_ids: list[str]) -> None:
    """Write all indicators from a topic."""

    # write topic title to page
    st.title(title)

    indicators = get_indicators(indicator_ids)
    for indicator in asyncio.run(indicators):
        st.divider()
        write_indicator(indicator)
