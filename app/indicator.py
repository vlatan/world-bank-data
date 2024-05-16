import json
import logging
import requests
import streamlit as st
from . import constants as co


class Indicator:
    def __init__(
        self, indicator_id: str, country_code: str | None = None, ttl: int = 86400
    ):
        self.country_code = country_code
        self.redis_client = st.session_state.redis_client
        self.indicator_id = indicator_id
        self.ttl = ttl

    def get_info(self) -> dict[str, str]:
        """Get indicator info (title and description)."""

        # the redis key is the indicator's id
        result = self.redis_client.get(redis_key := self.indicator_id)
        if isinstance(result, (str, bytes, bytearray)):
            return json.loads(result)

        url = f"{co.API_BASE_URL}/indicator/{self.indicator_id}"
        info = requests.get(url, params={"format": "json"}).json()[1][0]

        result = {
            "id": self.indicator_id,
            "title": info["name"].strip(),
            "description": info["sourceNote"].strip().replace("$", "\\$"),
        }

        self.redis_client.set(name=redis_key, value=json.dumps(result), ex=self.ttl)
        return result

    def get_data(self) -> dict[str, str]:
        """Get numerical data for indicator."""

        if not self.country_code:
            msg = "You need to provide a country code for getting the indicator's data."
            logging.error(msg)
            return {}

        # the redis key is country code and indicator id
        redis_key = f"{self.country_code}:{self.indicator_id}"

        result = self.redis_client.get(redis_key)
        if isinstance(result, (str, bytes, bytearray)):
            return json.loads(result)

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

        result = {
            "id": self.indicator_id,
            "country_code": self.country_code,
            "data": dict(sorted(result.items())),
        }

        self.redis_client.set(name=redis_key, value=json.dumps(result), ex=self.ttl)
        return result
