import asyncio
import pandas as pd
import streamlit as st
from .indicator import Indicator


async def get_indicators(indicator_ids: list[str]) -> list[dict]:
    """Get indicators data concurrently."""

    async with asyncio.TaskGroup() as tg:
        indicators = [Indicator(iid) for iid in indicator_ids]
        coros = [asyncio.to_thread(ind.get_indicator) for ind in indicators]
        tasks = [tg.create_task(coro) for coro in coros]

    return [task.result() for task in tasks]


def write_indicator(title: str, description: str, data: dict) -> None:
    """Write title, description, table and chart to page."""

    # write title and desc to page
    st.write(f"### {title}")
    st.write(description)

    # convert data to dataframes
    chart_data = pd.DataFrame(data=data)
    table = chart_data.set_index("date").transpose()

    # write dataframe table to page
    st.dataframe(table)

    # write chart to page
    # import altair as alt
    # chart = alt.Chart(chart_data).mark_area(opacity=0.4).encode(x="date", y="value")
    # st.altair_chart(chart, use_container_width=True)

    st.area_chart(
        data=chart_data,
        x="date",
        y="value",
        color=(131, 201, 255, 0.4),
        use_container_width=True,
    )


def write_topic(title: str, indicator_ids: list[str]) -> None:
    """Write all indicators from a topic."""

    # write topic title to page
    st.title(title)

    indicators = get_indicators(indicator_ids)
    for indicator in asyncio.run(indicators):
        st.divider()
        write_indicator(indicator["title"], indicator["description"], indicator["data"])
