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
COPY ./.streamlit ./.streamlit

# defult port env var
ENV PORT=8501

# https://docs.docker.com/reference/dockerfile/#healthcheck
HEALTHCHECK CMD curl --fail http://localhost:${PORT}/_stcore/health

# command to run the streamlit app
CMD streamlit run run.py \
    --browser.gatherUsageStats=false \
    --server.port=${PORT} \
    --server.address=0.0.0.0