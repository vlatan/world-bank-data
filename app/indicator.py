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

    def get_data(self) -> dict[str, str]:
        """Get numerical data for indicator."""

        page, pages, result = 0, 1, {}
        url = f"{co.API_BASE_URL}/country/{self.country_code}/indicator/{self.indicator_id}"

        while page < pages:
            page += 1

            response = requests.get(url, params={"page": page, "format": "json"}).json()
            pages, data = response[0]["pages"], response[1]

            if not data:
                continue

            for item in data:
                if value := item.get("value"):
                    result[item["date"]] = value

        return dict(sorted(result.items()))

    async def _get(self) -> tuple[dict[str, str], dict[str, str]]:
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

        # the key is country code and indicator
        redis_key = f"{self.country_code}:{self.indicator_id}"

        result = self.redis_client.get(redis_key)
        if isinstance(result, (str, bytes, bytearray)):
            return json.loads(result)

        info, data = asyncio.run(self._get())

        result = {
            "id": self.indicator_id,
            "country_code": self.country_code,
            "title": info["name"].strip(),
            "description": info["sourceNote"].strip().replace("$", "\\$"),
            "data": data,
        }

        self.redis_client.set(name=redis_key, value=json.dumps(result), ex=self.ttl)
        return result
