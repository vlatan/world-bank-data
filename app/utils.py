import os
import json
import redis
import requests
import functools
import pandas as pd
import altair as alt
import streamlit as st
from redis import Redis
from typing import Callable
from redis.exceptions import ConnectionError


def init_redis_client() -> Redis | None:
    """Initialize Redis client."""

    try:
        host = os.getenv("REDIS_HOST", "localhost")
        password = os.getenv("REDIS_PASSWORD")
        redis_client = redis.Redis(host=host, decode_responses=True)
        redis_client.ping()
        return redis_client
    except ConnectionError:
        return


redis_client = init_redis_client()


def cache_data(ttl: Callable | int) -> Callable:
    """
    Cache data in Redis.
    If Redis not available cache in streamlit.

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

            ex = ttl if isinstance(ttl, int) else 86400

            if not redis_client:
                cached_func = st.cache_data(ttl=ex, show_spinner="Fetching data...")
                return cached_func(func)(*args, **kwargs)

            result = redis_client.get(indicator := args[0])
            if isinstance(result, (str, bytes, bytearray)):
                return json.loads(result)

            result = func(*args, **kwargs)

            # TODO: Put this into non-blocking thread and measure if there's benefit
            redis_client.set(name=indicator, value=json.dumps(result), ex=ex)

            return result

        return wrapper

    if callable(ttl):
        return decorator(ttl)

    return decorator


@cache_data
def get_indicator_data(indicator: str) -> dict[str, list[dict] | str]:
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

    return {
        "title": response["name"],
        "description": response["sourceNote"],
        "data": result,
    }


def write_indicator(indicator: str) -> None:
    """Write title, description, table and chart to page."""

    indicator_data = get_indicator_data(indicator)
    title, description = indicator_data["title"], indicator_data["description"]
    chart_data = pd.DataFrame(data=indicator_data["data"])
    table = chart_data.set_index("date").transpose()

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
