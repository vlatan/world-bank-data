import os
import json
import asyncio
import requests
import functools
import pandas as pd
import streamlit as st
from redis import Redis
from typing import Callable
from redis.exceptions import ConnectionError


@st.cache_resource
def init_redis_client() -> Redis | None:
    """Initialize Redis client."""

    try:
        redis_client = Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            password=os.getenv("REDIS_PASSWORD"),
        )

        redis_client.ping()
        return redis_client

    except ConnectionError:
        return


redis_client = init_redis_client()


def cache_data(ttl: Callable | int) -> Callable:
    """
    Cache data in Redis.
    If Redis not available cache in streamlit.
    If TTL not specified, default is 1 day, 86400 seconds.

    -----------------------------------------------------------------------

    # Ordinary decorator (returns the decorated/modified function)
    # modified_function = decorator(decorated_function)

    # Decorator with arguments (is actually a function that returns a decorator
    # and that decorator then is being called with the decorated function)
    # decorator = decorator(arg)
    # modified_function = decorator(decorated_function)
    # Also can be written as:
    # modified_function = decorator(arg)(decorated_function)

    # If you use @cache_data without arguments (without parenthesis) then
    # the decorated function will be passed as its argument and decorator(func)
    # will be called as if @decorator was directly used on the decorated function
    # without the outer cache_data.

    # If you use @cache_data(ttl=100) with argument then the decorator will be returned,
    # which then will also be ultimately called as decorator(func).

    # Both cases come to the same result but this gymnastic is used to be able to
    # use the decorator @cached_data WITH and WITHOUT parenthesis / arguments.

    # https://stackoverflow.com/a/35572746/1148508
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> dict[str, list[dict] | str]:

            # define key expire time
            ex = ttl if isinstance(ttl, int) else 86400

            # if there's no redis client, cache in memory with streamlit
            if not redis_client:
                cached_func = st.cache_data(ttl=ex, show_spinner="Fetching data...")
                return cached_func(func)(*args, **kwargs)

            # if data in redis return it
            result = redis_client.get(indicator_id := args[0])
            if isinstance(result, (str, bytes, bytearray)):
                return json.loads(result)

            # run the decorated function
            result = func(*args, **kwargs)
            # save the result from the decorated function to redis
            redis_client.set(name=indicator_id, value=json.dumps(result), ex=ex)

            return result

        return wrapper

    if callable(ttl):
        return decorator(ttl)

    return decorator


def get_indicator_info(indicator_id: str) -> dict[str, str]:
    """Get indicator info (title and description)."""

    API_BASE_URL = os.getenv("API_BASE_URL")
    api = f"{API_BASE_URL}/indicator/{indicator_id}?format=json"
    return requests.get(api).json()[1][0]


def get_indicator_data(indicator_id: str) -> list[dict]:
    """Get numerical data for indicator."""

    page, pages, result = 0, 1, []
    API_BASE_URL = os.getenv("API_BASE_URL")
    COUNTRY_CODE = os.getenv("COUNTRY_CODE")
    api = f"{API_BASE_URL}/country/{COUNTRY_CODE}/indicator/{indicator_id}"

    while page < pages:
        page += 1

        response = requests.get(f"{api}?page={page}&format=json").json()
        pages, data = response[0]["pages"], response[1]

        result += [
            {key: value for key, value in item.items() if key in ["date", "value"]}
            for item in data
            if item.get("value") is not None
        ]

    return result


@cache_data
def get_indicator(indicator_id: str) -> dict[str, list[dict] | str]:
    """
    Get data per indicator from World Bank.
    Concurrently runs two requests.
    """

    async def get_data() -> tuple[dict[str, str], list[dict]]:
        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(asyncio.to_thread(get_indicator_info, indicator_id))
            t2 = tg.create_task(asyncio.to_thread(get_indicator_data, indicator_id))
        return t1.result(), t2.result()

    info, data = asyncio.run(get_data())

    return {
        "title": info["name"],
        "description": info["sourceNote"].replace("$", "\\$"),
        "data": data,
    }


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

    async def get_indicators() -> list[dict]:
        async with asyncio.TaskGroup() as tg:
            coros = [asyncio.to_thread(get_indicator, iid) for iid in indicator_ids]
            tasks = [tg.create_task(coro) for coro in coros]
        return [task.result() for task in tasks]

    for indicator in asyncio.run(get_indicators()):
        st.divider()
        write_indicator(indicator["title"], indicator["description"], indicator["data"])
