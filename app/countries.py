import json
import asyncio
import requests
import streamlit as st


class Countries:
    def __init__(self, ttl: int = 86400):
        self.url = f"https://api.worldbank.org/v2/country?format=json"
        self.redis_client = st.session_state.redis_client
        self.ttl = ttl

    async def _get(self) -> dict[str, str]:
        """Get country names and codes."""

        response = requests.get(self.url).json()
        pages, result = response[0]["pages"], response[1]

        result = {item["name"]: item["id"] for item in result}

        if pages == 1:
            return result

        async with asyncio.TaskGroup() as tg:
            coros = [
                asyncio.to_thread(requests.get, self.url, params={"page": page})
                for page in range(2, pages + 1)
            ]
            tasks = [tg.create_task(coro) for coro in coros]

        for task in tasks:
            current_result = task.result().json()[1]
            current_result = {item["name"]: item["id"] for item in current_result}
            result.update(current_result)

        return result

    def get(self) -> dict[str, str]:
        """Get result from Redis or from the API and cache in Redis."""

        result = self.redis_client.get("countries")
        if isinstance(result, (str, bytes, bytearray)):
            return json.loads(result)

        result = asyncio.run(self._get())
        self.redis_client.set(name="countries", value=json.dumps(result), ex=self.ttl)
        return result
