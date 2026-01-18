# https://docs.streamlit.io/deploy/tutorials/docker

# Docker image
FROM python:3.12-slim

# set the container's working directory
WORKDIR /src

# create virtual environment with uv and install dependencies
COPY requirements.txt .
RUN --mount=from=ghcr.io/astral-sh/uv:0.9.26,source=/uv,target=/bin/uv \
    uv venv && \
    uv pip install --no-cache-dir --upgrade -r requirements.txt && \
    rm requirements.txt

# copy all the necessary app files into the working dir
COPY ./run.py ./
COPY ./app ./app

# prepend the virtual environment path in the PATH env var
# streamlit config options
# https://docs.streamlit.io/develop/concepts/configuration/options
# https://docs.streamlit.io/develop/api-reference/configuration/config.toml

ENV PORT=8080 \
    VIRTUAL_ENV=/src/.venv

ENV PATH="${VIRTUAL_ENV}/bin:${PATH}" \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_CLIENT_SHOW_ERROR_DETAILS=false \
    STREAMLIT_CLIENT_TOOLBAR_MODE=minimal \
    STREAMLIT_SERVER_FILE_WATCHER_TYPE=none \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_RUN_ON_SAVE=false \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=${PORT} \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# https://docs.docker.com/reference/dockerfile/#healthcheck
HEALTHCHECK CMD curl --fail http://localhost:${STREAMLIT_SERVER_PORT}/_stcore/health

# command to run the streamlit app
ENTRYPOINT ["streamlit", "run", "run.py"]