# World Bank Data


A [Streamlit](https://github.com/streamlit/streamlit) app which fetches an overview data from the [World Bank](https://data.worldbank.org/), specifically from the topics and their indicators defined in [topics.json](app/topics.json), and charts the data for selected countries.


## Features

* It makes heavy use of the [asyncio](https://docs.python.org/3/library/asyncio.html) Python native library to achieve concurrent I/O operations, namely API calls to World Bank.
* If [Redis](https://redis.io/) service available it will cache the data fetched in Redis, if not it will failover to caching in memory.


## Quick Start

Take a look at the [example.env](example.env), create your own `.env` file in the root of this repo and adjust the environment variables.

Create/activate virtual environment and install the app dependencies.

``` bash
python3 -m venv .venv &&
source .venv/bin/activate &&
pip install --upgrade pip &&
pip install -r requirements.txt
```

Run the app out of the box on `localhost`, on port 8501.
``` bash
streamlit run run.py
```

If you want to make use of [Docker](https://www.docker.com/) use the the following command, which utilizes the [compose.yaml](compose.yaml) file to spin the app and a Redis service in the background, which will make the app available on `localhost`, on port 8080.

```
docker compose up --build --remove-orphans -d
```

You can check out the app logs with:
```
docker compose logs -f app
```

## Deployed

Hosted on **Railway**. Expect cold start.    
https://worldbank.up.railway.app/

## License

[![License: MIT](https://img.shields.io/github/license/vlatan/world-bank-data?label=License)](/LICENSE "License: MIT")