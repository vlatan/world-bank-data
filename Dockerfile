# https://docs.streamlit.io/deploy/tutorials/docker

# Docker image
FROM python:3.12-slim

# Update OS and install packages
RUN apt-get update && apt-get install -y \
    build-essential curl software-properties-common \
    && rm -rf /var/lib/apt/lists/*

# create virtual environment and prepend its bin dir in $PATH
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="${VIRTUAL_ENV}/bin:${PATH}" \
    # Allow statements and log messages to immediately appear in logs
    PYTHONUNBUFFERED=1

# set the container's working directory
WORKDIR /src

# copy requirements file and install dependencies
COPY ./requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir --upgrade -r requirements.txt

# copy all the necessary app files into the working dir
COPY ./run.py ./
COPY ./app ./app

# streamlit config options
# https://docs.streamlit.io/develop/concepts/configuration/options
ENV PORT=8000
ENV STREAMLIT_CLIENT_SHOW_ERROR_DETAILS=false \
    STREAMLIT_CLIENT_TOOLBAR_MODE=minimal \
    STREAMLIT_SERVER_FILE_WATCHER_TYPE=none \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_RUN_ON_SAVE=false \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_PORT=${PORT} \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# https://docs.docker.com/reference/dockerfile/#healthcheck
HEALTHCHECK CMD curl --fail http://localhost:${PORT}/_stcore/health

# command to run the streamlit app
CMD streamlit run run.py