import os
import json
import asyncio
import requests
import streamlit as st
from . import constants as co


class Indicator:
    def __init__(self, indicator_id: str, country_code: str = "USA", ttl: int = 86400):
        self.country_code = country_code
        self.redis_client = st.session_state.redis_client
        self.indicator_id = indicator_id
        self.ttl = ttl

    def get_info(self) -> dict[str, str]:
        """Get indicator info (title and description)."""

        url = f"{co.API_BASE_URL}/indicator/{self.indicator_id}"
        return requests.get(url, params={"format": "json"}).json()[1][0]

    def get_data(self) -> list[dict]:
        """Get numerical data for indicator."""

        page, pages, result = 0, 1, []
        url = f"{co.API_BASE_URL}/country/{self.country_code}/indicator/{self.indicator_id}"

        while page < pages:
            page += 1

            response = requests.get(url, params={"page": page, "format": "json"}).json()
            pages, data = response[0]["pages"], response[1]

            result += [
                {key: value for key, value in item.items() if key in ["date", "value"]}
                for item in data
                # if item.get("value") is not None
            ]

        return result

    async def _get(self) -> tuple[dict[str, str], list[dict]]:
        """Concurrently get indicator info and data from two ednpoints."""

        async with asyncio.TaskGroup() as tg:
            t1 = tg.create_task(asyncio.to_thread(self.get_info))
            t2 = tg.create_task(asyncio.to_thread(self.get_data))
        return t1.result(), t2.result()

    def get(self) -> dict[str, list[dict] | str]:
        """
        Get from Redis cache the indicator info and data if available.
        If not hit the API and save the result to Redis cache.
        """

        result = self.redis_client.get(self.indicator_id)
        if isinstance(result, (str, bytes, bytearray)):
            return json.loads(result)

        info, data = asyncio.run(self._get())

        result = {
            "title": info["name"],
            "description": info["sourceNote"].replace("$", "\\$"),
            "data": data,
        }

        self.redis_client.set(
            name=self.indicator_id, value=json.dumps(result), ex=self.ttl
        )
        return result
