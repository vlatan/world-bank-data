import asyncio
import pandas as pd
import altair as alt
import streamlit as st
from .indicator import Indicator
from .countries import Countries


async def get_indicators(indicator_ids: list[str]) -> list[dict]:
    """Get indicators data concurrently."""

    async with asyncio.TaskGroup() as tg:
        indicators = [Indicator(iid) for iid in indicator_ids]
        coros = [asyncio.to_thread(ind.get) for ind in indicators]
        tasks = [tg.create_task(coro) for coro in coros]

    return [task.result() for task in tasks]


@st.cache_data
def lookup_country_name(_countries: dict[str, str], code: str):
    for name, current_code in _countries.items():
        if code == current_code:
            return name


def write_indicator(indicator: dict) -> None:
    """Write title, description, table and chart to page."""

    country_code = indicator["country_code"]
    title = indicator["title"]
    description = indicator["description"]
    data = indicator["data"]

    # get all countries
    countries = Countries().get()
    country_name = lookup_country_name(countries, country_code)

    # write title and desc to page
    st.write(f"### {title}")
    st.write(description)

    # select a country from multiselect
    selected = st.multiselect(
        label="Choose countries",
        options=countries.keys(),
        default=[country_name],
        key=title,
    )

    if not selected:
        st.error("Please select at least one country/region.")

    # default country on first load
    elif len(selected) == 1 and selected[0] == country_name:
        # convert data to dataframe
        df = (
            pd.DataFrame({country_code: data.values()}, index=data.keys())
            .sort_index()
            .transpose()
        )

        df.index.name = "Region"
        st.dataframe(df)

        data = df.transpose().reset_index()
        data = pd.melt(data, id_vars=["index"]).rename(
            columns={"index": "year", "value": title}
        )
        chart = (
            alt.Chart(data)
            .mark_area(opacity=0.3)
            .encode(
                x="year:T",
                y=alt.Y(f"{title}:Q", stack=None),
                color="Region:N",
            )
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        # TODO: Add country or countries to table and chart
        pass


def write_topic(title: str, indicator_ids: list[str]) -> None:
    """Write all indicators from a topic."""

    # write topic title to page
    st.title(title)

    indicators = get_indicators(indicator_ids)
    for indicator in asyncio.run(indicators):
        st.divider()
        write_indicator(indicator)
