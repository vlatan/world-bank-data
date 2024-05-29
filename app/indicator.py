import logging
import asyncio
import requests
import functools
from typing import Iterable

from . import cache as ch
from .constants import API_BASE_URL


@ch.cache_data
def get_info(indicator_id: str) -> dict[str, str]:
    """Get indicator info (title and description)."""

    url = f"{API_BASE_URL}/indicator/{indicator_id}"

    try:
        response = requests.get(url, params={"format": "json"}, timeout=5)
        response.raise_for_status()
        info = response.json()[1][0]
    except Exception:
        msg = f"Couldn't fetch indicator info from API: {url}"
        logging.exception(msg)
        return {}

    return {
        "id": indicator_id,
        "title": info["name"].strip(),
        "description": info["sourceNote"].strip().replace("$", "\\$"),
    }


@ch.cache_data
def get_page_data(
    country_code: str, indicator_id: str, page: int = 1
) -> None | tuple[int, dict[str, str]]:
    """Get country data for a given indicator for a given page."""

    url = f"{API_BASE_URL}/country/{country_code}/indicator/{indicator_id}"
    params = {"page": page, "format": "json"}

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        response = response.json()
        pages, data = response[0]["pages"], response[1]
        data = {
            item["date"]: item["value"]
            for item in data
            if item.get("value") is not None
        }
        return pages, data
    except Exception:
        msg = f"Couldn't fetch country data from API ({url}) for page {page}."
        logging.exception(msg)
        return None


async def get_data(country_code: str, indicator_id: str) -> dict[str, str | dict]:
    """Get country data for a given indicator."""

    empty_response = {
        "id": indicator_id,
        "country_code": country_code,
        "data": {},
    }

    page_data = functools.partial(get_page_data, country_code, indicator_id)
    if (response := page_data()) is None:
        return empty_response

    pages, result = response

    if pages == 1:
        return {
            "id": indicator_id,
            "country_code": country_code,
            "data": dict(sorted(result.items())),
        }

    page_range = range(2, pages + 1)
    coros = [asyncio.to_thread(page_data, page) for page in page_range]

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(coro) for coro in coros]

    for task in tasks:
        if (current_response := task.result()) is None:
            return empty_response
        _, current_result = current_response
        result.update(current_result)

    return {
        "id": indicator_id,
        "country_code": country_code,
        "data": dict(sorted(result.items())),
    }


async def get_indicators_info(indicator_ids: Iterable[str]) -> Iterable[dict]:
    """Concurrently get info (title and description) for each indicator."""

    # create coroutines
    coroutines = [asyncio.to_thread(get_info, iid) for iid in indicator_ids]

    # execute tasks in parallel
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(coroutine) for coroutine in coroutines]

    # get results
    return [task.result() for task in tasks]


async def get_countries_data(
    indicator_id: str, country_codes: Iterable[str]
) -> Iterable[dict]:
    """Concurrently get data for each country for a given indicator."""

    # execute tasks in parallel
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(get_data(cc, indicator_id)) for cc in country_codes]

    # get results
    return [task.result() for task in tasks]
