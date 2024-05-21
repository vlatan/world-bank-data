import asyncio
import requests
from . import cache as ch
from . import constants as co


@ch.cache_data
def get_page_countries(page: int = 1) -> dict:
    """Get JSON result from one page countries API page."""

    url = f"{co.API_BASE_URL}/country"
    params = {"page": page, "format": "json"}
    return requests.get(url, params=params).json()


async def get_countries() -> dict[str, str]:
    """
    Get country names and codes.
    Get result from Redis or from the API and cache in Redis.
    """

    response = get_page_countries()
    pages, result = response[0]["pages"], response[1]
    result = {item["name"]: item["id"] for item in result}

    if pages == 1:
        return result

    page_range = range(2, pages + 1)
    coros = [asyncio.to_thread(get_page_countries, page) for page in page_range]

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(coro) for coro in coros]

    for task in tasks:
        current_result = task.result()[1]
        current_result = {item["name"]: item["id"] for item in current_result}
        result.update(current_result)

    print(result)
    return result
