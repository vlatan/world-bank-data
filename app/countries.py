import logging
import asyncio
import requests

from . import cache as ch
from .constants import API_BASE_URL


@ch.cache_data
def get_page_countries(page: int = 1) -> tuple[int, dict[str, str]]:
    """Get JSON result from one page of countries API."""

    url = f"{API_BASE_URL}/country"
    params = {"page": page, "format": "json"}

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        response = response.json()
        pages, result = response[0]["pages"], response[1]
        result = {item["name"]: item["id"] for item in result}
        return pages, result
    except Exception:
        msg = f"Couldn't fetch countries from API ({url}) for page {page}."
        logging.exception(msg)
        return 0, {}


async def get_countries() -> dict[str, str]:
    """Get ALL country names and codes."""

    pages, result = get_page_countries()

    if pages in [0, 1]:
        return result

    page_range = range(2, pages + 1)
    coros = [asyncio.to_thread(get_page_countries, page) for page in page_range]

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(coro) for coro in coros]

    for task in tasks:
        _, current_result = task.result()
        result.update(current_result)

    return result
