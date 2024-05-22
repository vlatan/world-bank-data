import logging
import asyncio
import requests
from . import cache as ch
from typing import Iterable
from . import constants as co


@ch.cache_data
def get_info(indicator_id: str) -> dict[str, str]:
    """Get indicator info (title and description)."""

    url = f"{co.API_BASE_URL}/indicator/{indicator_id}"

    try:
        response = requests.get(url, params={"format": "json"}, timeout=5)
        response.raise_for_status()
        info = response.json()[1][0]
    except Exception:
        logging.exception(f"Couldn't fetch {indicator_id} indicator info from API.")
        return {}

    return {
        "id": indicator_id,
        "title": info["name"].strip(),
        "description": info["sourceNote"].strip().replace("$", "\\$"),
    }


@ch.cache_data
def get_data(country_code: str, indicator_id: str) -> dict[str, str | dict]:
    """Get country data for a given indicator."""

    page, pages, result = 0, 1, {}
    url = f"{co.API_BASE_URL}/country/{country_code}/indicator/{indicator_id}"

    while page < pages:
        page += 1

        response = requests.get(url, params={"page": page, "format": "json"}).json()
        pages, data = response[0]["pages"], response[1]

        if not data:
            continue

        for item in data:
            if value := item.get("value"):
                result[item["date"]] = value

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
) -> list[dict]:
    """Concurrently get data for each country for a given indicator."""

    # create coroutines
    coros = [asyncio.to_thread(get_data, cc, indicator_id) for cc in country_codes]

    # execute tasks in parallel
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(coro) for coro in coros]

    # get results
    return [task.result() for task in tasks]
